from typing import Optional, Union, List, Callable

import numpy as np
import scipy as sp

from ._base import BaseNotes
from ._utils import note_name_formatting, chord_name_formatting
from .chord_names import chord_names
from .envelope import Envelope


NUM_C0 = 12 # MIDI note number of C0
NUM_A4 = 69 # MIDI note number of A4
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
SUPPORTED_WAVEFORMS = ["sin", "square", "sawtooth", "triangle"]
SUPPORTED_UNITS = ["s", "ms", "ql"]


class Note(BaseNotes):
    def __init__(
        self,
        query: Union[str, int],
        octave: int = 4,
        waveform: Union[str, Callable] = 'sin',
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120,
        envelope: Optional[Envelope] = None,
        duty: Optional[float] = 0.5,
        width: Optional[float] = 1.,
        sr: int = 22050,
        A4: float = 440.,
    ):
        """
        Note class.
        Single note. It can be initialized with note name or MIDI note
        number.

        Args:
            query (Union[str, int]):
                String of note name or midi note number. If string is
                given, valid string pattern is '[A-Ga-g][#♯+b♭-]?\d*'.
                Ex: 'C', 'C#', 'Cb', 'C4'
            octave (int, optional):
                Octave of the note. This argument is ignored if octave
                is specified in the note name string, or if query is
                int. Defaults to 4.
            waveform (Union[str, Callable], optional):
                Waveform type. This value becomes the default value
                when render() and play(). Spported waveform types:
                    - 'sin'
                    - 'square'
                    - 'sawtooth'
                    - 'triangle'
                    - user-defined waveform function
                user-defined waveform function must take time axis as
                an argument and return an array like waveform of the
                same length. Defaults to 'sin'.
            duration (float, optional):
                Duration. This value becomes the default value when
                rendering the waveform. Defaults to 1..
            unit (str, optional):
                Unit of duration. This value becomes the default value
                when rendering the waveform. Supported units:
                    - 's': seconds
                    - 'ms': milliseconds
                    - 'ql': quarter length (bpm is required)
                Defaults to 's'.
            bpm (float, optional):
                BPM (beats per minute). If unit is not 'ql', this
                argument is ignored. This value becomes the default
                value when rendering the waveform. Defaults to 120.
            envelope (Envelope, optional):
                Envelope of the note. This value becomes the default
                value when rendering the waveform. Defaults to
                Envelope() with attack=0., decay=0., sustain=1.,
                release=0., hold=0..
            duty (float, optional):
                Duty cycle for when waveform is 'square'. This value
                becomes the default value when rendering the waveform.
                Defaults to 0.5.
            width (float, optional):
                Width for when waveform is 'sawtooth'. This value
                becomes the default value when rendering the waveform.
                Defaults to 1..
            sr (int, optional):
                Sampling rate. This value becomes the default value
                when rendering the waveform. Defaults to 22050.
            A4 (float, optional):
                tuning. freqency of A4. Defaults to 440..

        \Attributes:
            - name (str): note name
            - octave (int): octave of the note
            - idx (int): index of the note name when C as 0
            - num (int): MIDI note number
            - freq (float): frequency of the note
            - waveform (Union[str, Callable]): default waveform type
            - duration (float): default duration
            - unit (str): default unit of duration
            - bpm (float): default BPM
            - envelope (Envelope): default envelope
            - duty (float): default duty
            - width (float): default width
            - sr (int): default sampling rate
            - A4 (float): tuning. freqency of A4

        Examples:
            >>> import munotes as mn
            >>> note = mn.Note("C4")
            >>> print(note)
            C4

            You can also input note name and octave separately.

            >>> note = mn.Note("C", 4)
            >>> print(note)
            C4

            You can also input MIDI note number as an integer.

            >>> note = mn.Note(60)
            >>> print(note)
            C4
        """
        if isinstance(query, str):
            self._name, self._octave = note_name_formatting(query, octave)
            self._idx = self._return_name_idx()
            self._num = NUM_C0 + 12*self.octave + self.idx
        elif isinstance(query, int):
            assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
            self._num = query
            self._name = KEY_NAMES[(self.num - NUM_C0) % 12]
            self._idx = self._return_name_idx()
            self._octave = (self.num - NUM_C0) // 12
        else:
            raise ValueError(
                "Input must be a string or an integer, "
                f"but got '{type(query)}'"
            )

        self._init_attrs(
            waveform=waveform,
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            duty=duty,
            width=width,
            sr=sr,
            A4=A4,
        )

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self = Note(
            value,
            octave=self.octave,
            waveform=self.waveform,
            duration=self.duration,
            unit=self.unit,
            bpm=self.bpm,
            envelope=self.envelope,
            duty=self.duty,
            width=self.width,
            sr=self.sr,
            A4=self.A4,
        )

    @property
    def idx(self) -> int:
        return self._idx

    @idx.setter
    def idx(self, value):
        raise Exception("idx is read only")

    @property
    def octave(self) -> int:
        return self._octave

    @octave.setter
    def octave(self, value):
        self.transpose(12 * (value - self.octave))

    @property
    def num(self) -> int:
        return self._num

    @num.setter
    def num(self, value):
        raise Exception("num is read only")

    @property
    def freq(self) -> float:
        return self._freq

    @freq.setter
    def freq(self, value):
        raise Exception("freq is read only")

    @property
    def A4(self) -> float:
        return self._A4

    @A4.setter
    def A4(self, value):
        raise Exception("A4 is read only")

    def _return_name_idx(self) -> int:
        """Return index of the note name in KEY_NAMES"""
        idx = KEY_NAMES.index(self.name[0])
        idx = (idx + ('#' in self.name) - ('b' in self.name)) % 12
        return idx

    def _return_time_axis(self, sec: float) -> np.ndarray:
        """
        Generate time axis from duration and sampling rate.

        Args:
            sec (float): Duration in seconds.

        Returns:
            np.ndarray: Time axis.
        """
        freqs = np.array([note.freq for note in self._notes])
        t = np.linspace(0, 2*np.pi * sec * freqs, int(self.sr * sec), axis=1)
        return t

    def transpose(self, n_semitones: int) -> None:
        """
        Transpose note.

        Args:
            n_semitones (int): Number of semitones to transpose.

        Examples:
            >>> note = mn.Note("C4")
            >>> note.transpose(1)
            >>> print(note)
            C#4
        """
        for note in self._notes:
            note._idx = (note.idx + n_semitones) % 12
            note._name = KEY_NAMES[note.idx]
            note._num += n_semitones
            note._octave = (note.num - NUM_C0) // 12
            note._freq = note._A4 * 2** ((note.num - NUM_A4) / 12)

    def tuning(self, freq: float = 440., stand_A4: bool = True) -> None:
        """
        Tuning.

        Args:
            freq (float, optional):
                Freqency of the note or A4. Defaults to 440..
            stand_A4 (bool, optional):
                If True, the tuning standard is A4. If False, the note
                frequency is changed to ``freq``.
        Examples:
            >>> note = mn.Note("C4")
            >>> print(note.freq)
            >>> note.tuning(450.)
            >>> print(note.freq)
            261.6255653005986
            267.5716008756122

            >>> note = mn.Note("C4")
            >>> print(note.freq)
            >>> note.tuning(270., stand_A4=False)
            >>> print(note.freq)
            261.6255653005986
            270.0
        """
        for note in self._notes:
            if stand_A4:
                note._A4 = freq
                note._freq = note._A4 * 2 ** ((note.num - NUM_A4) / 12)
            else:
                note._freq = freq
                note._A4 = note._freq / 2 ** ((note.num - NUM_A4) / 12)

    def render(
        self,
        waveform: Optional[Union[str, Callable]] = None,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        duty: Optional[float] = None,
        width: Optional[float] = None,
    ) -> np.ndarray:
        """
        Rendering waveform of the note. If an argument is not specified,
        its attribute value set on initialization is used as the default
        value.

        Returns:
            np.ndarray: Waveform of the note.

        Examples:
            >>> note = mn.Note("C4")
            >>> note.render('sin')
            array([ 0.        ,  0.07448499,  0.14855616, ..., -0.59706869,
                   -0.65516123, -0.70961388])

            >>> note.render(lambda t: np.sin(t) + np.sin(2*t))
            array([0.        , 0.23622339, 0.46803688, ..., 1.75357961, 1.72041279,
                   1.66076322])
        """
        waveform = waveform or self.waveform
        duration = duration if duration is not None else self.duration
        unit = unit or self.unit
        assert unit in SUPPORTED_UNITS, \
            f"unit must be in {SUPPORTED_UNITS} but got '{unit}'"
        bpm = bpm or self.bpm
        envelope = envelope or self.envelope
        duty = duty or self.duty
        width = width or self.width

        if unit == "s":
            sec = duration
        elif unit == "ms":
            sec = duration / 1000
        elif unit == "ql":
            sec = duration * 60 / bpm
        else:
            raise ValueError(
                f"unit must be in {SUPPORTED_UNITS}, but got '{unit}'"
            )
        t = self._return_time_axis(sec + envelope.release)

        if isinstance(waveform, str):
            if waveform == "sin":
                y = np.sum(np.sin(t), axis=0)
            elif waveform == "square":
                y = np.sum(sp.signal.square(t, duty=duty), axis=0)
            elif waveform == "sawtooth":
                y = np.sum(sp.signal.sawtooth(t, width=width), axis=0)
            elif waveform == "triangle":
                y = np.sum(sp.signal.sawtooth(t, width=0.5), axis=0)
            else:
                raise ValueError(
                    f"waveform string must be in {SUPPORTED_WAVEFORMS}, "
                    f"but got '{waveform}'"
                )
        else:
            y = np.sum([waveform(ti) for ti in t], axis=0)
        y = self._normalize(y)
        window = envelope.get_window(len(y), unit="sample", inner_release=True)
        y *= window
        return y

    def __add__(self, other):
        if isinstance(other, str):
            return str(self) + other
        elif isinstance(other, Note):
            return Notes([self, *other._notes])
        else:
            raise TypeError(
                "unsupported operand type(s) for +: 'Note' and "
                f"'{type(other)}'"
            )

    def __str__(self):
        return f'{self.name}{self.octave}'

    def __repr__(self):
        return f'Note {self.name}{self.octave}'

    def __int__(self):
        return self.num

    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        elif isinstance(other, int):
            return int(self) == other
        elif isinstance(other, Note):
            return self.num == other.num
        else:
            raise TypeError(
                "unsupported operand type(s) for ==: 'Note' and "
                f"'{type(other)}'"
            )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return int(self) < other

    def __le__(self, other):
        return int(self) <= other

    def __gt__(self, other):
        return int(self) > other

    def __ge__(self, other):
        return int(self) >= other


class Rest(Note):
    def __init__(
        self,
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120
    ):
        """
        Rest class for Track and Stream class. Return zeros array when
        rendering.

        Examples:
            >>> rest = mn.Rest()
            >>> rest.sin()
            array([0., 0., 0., ..., 0., 0., 0.])
        """
        self._name = 'Rest'
        self._octave = None
        self._freq = 0.
        self._num = None
        self._idx = None
        self._init_attrs(
            duration=duration,
            unit=unit,
            bpm=bpm,
        )

    def render(self, *args, **kwargs):
        return np.zeros_like(super().render(*args, **kwargs))

    def transpose(self, *args, **kwargs):
        pass

    def tuning(self, *args, **kwargs):
        pass

    def __str__(self):
        return 'Rest'

    def __repr__(self):
        return 'Rest'


class Notes(Note):
    def __init__(
        self,
        notes: List[Union[Note, int, str]],
        waveform: Union[str, Callable] = 'sin',
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120,
        envelope: Optional[Envelope] = None,
        duty: Optional[float] = 0.5,
        width: Optional[float] = 1.,
        sr: int = 22050,
        A4: float = 440.,
    ):
        """
        Notes class. Manage multiple notes at once. Default attributes
        (waveform, duration, unit, bpm, sr, A4) set in each Note are
        ignored and the attributes set in this class are used.

        Similar to the Note class, it is possible to generate waveforms
        using render() and sin().

        Args:
            notes (List[Union[Note, int, str]]):
                List of notes. Supported note types:
                    - Note: mn.Note, mn.Notes, etc.
                    - str: note name.
                    - int: midi note number.

        \Attributes:
            - notes (List[Note]): list of notes
            - names (List[str]): list of note names
            - fullnames (List[str]): list of note fullnames
            - nums (List[int]): list of MIDI note numbers

        Examples:
            >>> import musicnote as mn
            >>> notes = mn.Notes(
            >>>     mn.Note("C4"),
            >>>     mn.Note("E4"),
            >>>     mn.Note("G4")
            >>> )
            >>> notes
            Notes [Note C4, Note E4, Note G4]

            >>> notes = mn.Notes("C4", "E4", "G4")
            >>> notes
            Notes [Note C4, Note E4, Note G4]

            >>> notes = mn.Notes(60, 64, 67)
            >>> notes
            Notes [Note C4, Note E4, Note G4]

            >>> notes = mn.Notes(60, 64, 67) + mn.Note("C5")
            >>> notes
            Notes [Note C4, Note E4, Note G4, Note C5]
        """
        if isinstance(notes, Note):
            raise TypeError(
                "The Notes class does not support Note classes as input. "
                "Enter a list of notes at once as an argument."
            )
        notes_ = []
        for note in notes:
            if isinstance(note, Note):
                notes_ += note._notes
            elif isinstance(note, (str, int)):
                notes_.append(Note(note))
            else:
                raise ValueError(f"Unsupported type: '{type(note)}'")
        self.notes = sorted(notes_, key=lambda note: note.num)
        self._notes = self.notes
        self.names = [note.name for note in self]
        self.fullnames = [str(note) for note in self]
        self.nums = [note.num for note in self]

        self._init_attrs(
            waveform=waveform,
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            duty=duty,
            width=width,
            sr=sr,
            A4=A4,
        )

    def transpose(self, n_semitones: int) -> None:
        super().transpose(n_semitones)
        self.names = [note.name for note in self.notes]
        self._nums = [note.num for note in self.notes]

    def append(self, *note: Union[Note, int]) -> None:
        """
        Append notes.

        Args:
            note (Union[Note, int]):
                Note (or Notes or Chord) or midi note number

        Examples:
            >>> notes = mn.Notes(mn.Note("C4"))
            >>> notes.append(mn.Note("E4"), mn.Note("G4"))
            >>> notes
            Notes [Note C4, Note E4, Note G4]
        """
        self = Notes(
            [self, *note],
            duration=self.duration,
            unit=self.unit,
            bpm=self.bpm,
            envelope=self.envelope,
            duty=self.duty,
            width=self.width,
            sr=self.sr,
            A4=self.A4,
        )

    def __len__(self):
        return len(self.notes)

    def __getitem__(self, index):
        return self.notes[index]

    def __iter__(self):
        return iter(self.notes)

    def __add__(self, other):
        return Notes([self, other])

    def __repr__(self):
        return f'Notes {self.notes}'

    def __str__(self):
        return ' '.join(self.fullnames)


class Chord(Notes):
    def __init__(
        self,
        chord_name: str,
        type: Optional[str] = None,
        octave: int = 4,
        waveform: Union[str, Callable] = 'sin',
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120,
        envelope: Optional[Envelope] = None,
        duty: Optional[float] = 0.5,
        width: Optional[float] = 1.,
        sr: int = 22050,
        A4: float = 440.,
    ):
        """
        Chord class.
        Estimating notes from chord names and creating a Notes object.

        Supported chord names are shown in ``mn.chord_names``.
        ``mn.chord_names`` is a dictionary of chord names and intervals
        between notes with the root note as 0.
        Ex: {'': (0, 4, 7), 'm': (0, 3, 7), 'dim7': (0, 3, 6, 9), ...}.
        You can add your own chord names and intervals to this
        dictionary.

        Args:
            chord_name (str):
                string of chord name. Chord type in the string is
                ignored if 'type' argument is specified.
            type (str, optional):
                chord type. Ex. '', 'm7', '7', 'sus4'.
            octave (int, optional):
                octave of the root note to initialize notes.

        \Attributes:
            - name (str): chord name
            - root (Note): root note.
            - interval (tuple):
                interval of the chord. Ex: (0,4,7) for C major
            - type (str): chord type. Ex: "m" for C minor
            - names (tuple): note names of the chord.
            - notes (List[Note]): notes of the chord.
            - idxs (int): index of the root note.

        Examples:
            >>> import musicnotes as mn
            >>> chord = mn.Chord("C")
            >>> chord.names
            ['C', 'E', 'G']

            Adding arbitrary chords.

            >>> mn.chord_names["black"] = (0, 1, 2, 3, 4)
            >>> chord = mn.Chord("C", "black")
            >>> chord.names
            ['C', 'C#', 'D', 'D#', 'E']
        """
        root_name, type = chord_name_formatting(chord_name, type)
        root = Note(root_name, octave)
        name = root.name + type
        interval = chord_names[type]

        self._name = name
        self._type = type
        self._interval = interval
        self.root = root
        self._idxs = [(self.root.idx + i) % 12 for i in self.interval]
        self._octave = octave
        super().__init__(
            [self.root.num + i for i in self.interval],
            waveform=waveform,
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            duty=duty,
            width=width,
            sr=sr,
            A4=A4,
        )

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        raise Exception("name is read only")

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        raise Exception("type is read only")

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, value):
        raise Exception("interval is read only")

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value
        self._name = self.root.name + self.type
        self._idxs = [(self.root.idx + i) % 12 for i in self.interval]

    @property
    def idxs(self):
        return self._idxs

    @idxs.setter
    def idxs(self, value):
        raise Exception("idxs is read only")

    def transpose(self, n_semitones: int):
        """
        Transpose chord

        Examples:
            >>> chord = mn.Chord("C")
            >>> chord.transpose(1)
            >>> chord.names
            ['C#', 'F', 'G#']
        """
        super().transpose(n_semitones)
        self.root = self.notes[0]

    def append(self, value) -> None:
        raise Exception("Chord class does not support append()")

    def __repr__(self):
        return f'Chord {self.name}'

    def __str__(self):
        return self.name
