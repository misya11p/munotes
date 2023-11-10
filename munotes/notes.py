from __future__ import annotations
from .name_strings import note_name_formatting, chord_name_formatting
from .chord_names import chord_names
import numpy as np
import scipy as sp
import IPython
from typing import Optional, Union, Callable, List


NUM_C0 = 12 # MIDI note number of C0
NUM_A4 = 69 # MIDI note number of A4
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
SUPPOERTED_WAVEFORMS = ["sin", "square", "sawtooth", "triangle"]
SUPPOERTED_UNITS = ["s", "ms", "ql"]


class Note:
    def __init__(
        self,
        query: Union[str, int],
        octave: int = 4,
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120,
        A4: float = 440.
    ):
        """
        Note class.
        Single note. It can be initialized with note name or MIDI note
        number.

        Args:
            query (Union[str, int]):
                string of note name or midi note number. If string is
                given, valid string pattern is '[A-Ga-g][#♯+b♭-]?\d*'.
                Ex: 'C', 'C#', 'Cb', 'C4'
            octave (int, optional):
                octave of the note. This argument is ignored if octave
                is specified in the note name string, or if query is
                int. Defaults to 4.
            duration (float, optional):
                duration. This value becomes the default value when
                rendering the waveform. Defaults to 1..
            unit (str, optional):
                unit of duration. This value becomes the default value
                when rendering the waveform. Supported units:
                    - 's': seconds
                    - 'ms': milliseconds
                    - 'ql': quarter length (bpm is required)
                Defaults to 's'.
            bpm (float, optional):
                BPM (beats per minute). If unit is not 'ql', this
                argument is ignored. This value becomes the default
                value when rendering the waveform. Defaults to 120.
            A4 (float, optional):
                tuning. freqency of A4. Defaults to 440..

        \Attributes:
            - name (str): note name
            - octave (int): octave of the note
            - idx (int): index of the note name when C as 0
            - num (int): MIDI note number
            - freq (float): frequency of the note
            - A4 (float): tuning. freqency of A4
            - duration (float): default duration when rendering
            - unit (str): default unit of duration when rendering
            - bpm (float): default BPM when rendering

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
            self.name, self._octave = note_name_formatting(query, octave)
            self._idx = self._return_name_idx()
            self._num = NUM_C0 + 12*self.octave + self.idx
        elif isinstance(query, int):
            assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
            self._num = query
            self.name = KEY_NAMES[(self.num - NUM_C0) % 12]
            self._idx = self._return_name_idx()
            self._octave = (self.num - NUM_C0) // 12
        else:
            raise ValueError("Input must be a string or an integer")

        self._A4 = A4
        self._freq = self._A4 * 2**((self.num - NUM_A4)/12)
        self._notes = [self]
        self.duration = duration
        self.unit = unit
        self.bpm = bpm

    @property
    def num(self) -> int:
        return self._num

    @num.setter
    def num(self, value):
        raise Exception("num is read only")

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
    def A4(self) -> float:
        return self._A4

    @A4.setter
    def A4(self, value):
        self._A4 = value
        for note in self._notes:
            note._A4 = value
            note._freq = note.A4 * 2**((note.num - NUM_A4)/12)

    @property
    def freq(self) -> float:
        return self._freq

    @freq.setter
    def freq(self, value):
        for note in self._notes:
            note.A4 = value / 2**((note.num - NUM_A4)/12)

    def _return_name_idx(self) -> int:
        """Return index of the note name in KEY_NAMES"""
        idx = KEY_NAMES.index(self.name[0])
        idx = (idx + ('#' in self.name) - ('b' in self.name)) % 12
        return idx

    def _return_time_axis(self, sec: float, sr: int) -> np.ndarray:
        """
        Generate time axis from duration and sampling rate

        Args:
            sec (float): duration in seconds
            sr (int): sampling rate

        Returns:
            np.ndarray: Time axis
        """
        freqs = np.array([note.freq for note in self._notes])
        t = np.linspace(0, 2*np.pi * sec * freqs, int(sr*sec), axis=1)
        return t

    def render(
        self,
        waveform: Union[str, Callable] = 'sin',
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm = None,
        sr: int = 22050,
        **kwargs
    ) -> np.ndarray:
        """
        Rendering waveform of the note.

        Args:
            waveform (Union[str, Callable], Optional):
                waveform type. spported waveform types:
                    - 'sin'
                    - 'square'
                    - 'sawtooth'
                    - 'triangle'
                    - user-defined waveform function
            duration (float, optional):
                duration of the note. if None, Note.duration is used.
            unit (str, optional):
                unit of duration. supported units:
                    - 's': seconds
                    - 'ms': milliseconds
                    - 'ql': quarter length (bpm is required)
            bpm (float, optional):
                BPM (beats per minute). Required when unit is 'ql'.
            sr (int, optional): sampling rate.
            **kwargs (optional):
                keyword arguments for waveform function. 'duty' for
                'square', 'width' for 'sawtooth' and any args for
                user-defined waveform function are supported.

        Returns:
            np.ndarray: waveform of the note

        Examples:
            >>> note = mn.Note("C4")
            >>> note.render('sin')
            array([ 0.        ,  0.07448499,  0.14855616, ..., -0.59706869,
                   -0.65516123, -0.70961388])

            >>> note.render(lambda t: np.sin(t) + np.sin(2*t))
            array([0.        , 0.23622339, 0.46803688, ..., 1.75357961, 1.72041279,
                   1.66076322])

        Note:
            Generating a waveform by inputting a string into this
            method, as in ``note.render('sin')``, is the same as
            generating a waveform by calling the method directly, as in
            ``note.sin()``.
        """
        duration = duration if duration is not None else self.duration
        unit = unit or self.unit
        bpm = bpm or self.bpm
        if unit == "s":
            sec = duration
        elif unit == "ms":
            sec = duration / 1000
        elif unit == "ql":
            sec = duration * 60 / bpm
        else:
            raise ValueError(f"unit must be in {SUPPOERTED_UNITS}, but got '{unit}'")

        t = self._return_time_axis(sec, sr)
        if isinstance(waveform, str):
            if waveform == "sin":
                y = np.sum(np.sin(t), axis=0)
            elif waveform == "square":
                duty = kwargs.get("duty", 0.5)
                y = np.sum(sp.signal.square(t, duty=duty), axis=0)
            elif waveform == "sawtooth":
                width = kwargs.get("width", 1.)
                y = np.sum(sp.signal.sawtooth(t, width=width), axis=0)
            elif waveform == "triangle":
                y = np.sum(sp.signal.sawtooth(t, width=0.5), axis=0)
            else:
                raise ValueError(f"waveform string must be in {SUPPOERTED_WAVEFORMS}, but got '{waveform}'")
        else:
            y = np.sum([waveform(ti, **kwargs) for ti in t], axis=0)
        return y

    def sin(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        sr: int = 22050
    ) -> np.ndarray:
        """
        Generate sin wave of the note. It is the same as 
        ``Note.render('sin')``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)
            sr (int, optional): sampling rate

        Returns:
            np.ndarray: sin wave of the note
        """
        return self.render('sin', duration, unit, bpm, sr)

    def square(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        duty: float = 0.5,
        sr: int = 22050
    ) -> np.ndarray:
        """
        Generate square wave of the note. It is the same as
        ``Note.render('square')``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)
            duty (float, optional): duty cycle
            sr (int, optional): sampling rate

        Returns:
            np.ndarray: square wave of the note
        """
        return self.render('square', duration, unit, bpm, sr, duty=duty)

    def sawtooth(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        width: float = 1.,
        sr: int = 22050
    ) -> np.ndarray:
        """
        Generate sawtooth wave of the note. It is the same as
        ``Note.render('sawtooth')``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)
            width (float, optional): width of sawtooth
            sr (int, optional): sampling rate

        Returns:
            np.ndarray: sawtooth wave of the note
        """
        return self.render('sawtooth', duration, unit, bpm, sr, width=width)

    def triangle(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        sr: int = 22050
    ) -> np.ndarray:
        """
        Generate triangle wave of the note. It is the same as
        ``Note.render('triangle')``, ``note.sawtooth(width=0.5)``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)
            sr (int, optional): sampling rate

        Returns:
            np.ndarray: triangle wave of the note
        """
        return self.render('triangle', duration, unit, bpm, sr)

    def play(
        self,
        waveform: Union[str, Callable] = 'sin',
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        sr: int = 22050,
        **kwargs
    ) -> IPython.display.Audio:
        """
        Play note sound in IPython notebook. Return
        IPython.display.Audio object. This wave is generated by
        ``Note.render()``.

        Args:
            waveform (Union[str, Callables], optional): waveform type.
            duration (float, optional): duration.
            unit (str, optional): unit of duration.
            bpm (float, optional):BPM (beats per minute).
            sr (int, optional): sampling rate.

        Returns:
            IPython.display.Audio: audio object
        """
        y = self.render(waveform, duration, unit, bpm, sr, **kwargs)
        return IPython.display.Audio(y, rate=sr)


    def transpose(self, n_semitones: int) -> None:
        """
        Transpose note.

        Args:
            n_semitones (int): number of semitones to transpose

        Examples:
            >>> note = mn.Note("C4")
            >>> note.transpose(1)
            >>> print(note)
            C#4
        """
        for note in self._notes:
            note._idx = (note.idx + n_semitones) % 12
            note.name = KEY_NAMES[note.idx]
            note._num += n_semitones
            note._octave = (note.num - NUM_C0) // 12
            note._freq = note._A4 * 2**((note.num - NUM_A4)/12)

    def tuning(self, freq: float = 440., stand_A4: bool = False) -> None:
        """
        Tuning.

        Args:
            freq (float, optional): freqency of note.
            stand_A4 (bool, optional):
                if True, the tuning standard is A4.

        Examples:
            >>> note = mn.Note("C4")
            >>> print(note.freq)
            >>> note.tuning(270.)
            >>> print(note.freq)
            261.6255653005986
            270.0

            >>> note = mn.Note("C4")
            >>> print(note.freq)
            >>> note.tuning(450., stand_A4=True)
            >>> print(note.freq)
            261.6255653005986
            267.5716008756122
        """
        if stand_A4:
            for note in self._notes:
                note.A4 = freq
        else:
            for note in self._notes:
                note.freq = freq


    def __add__(self, other):
        if isinstance(other, str):
            return str(self) + other
        elif isinstance(other, (Note, Notes)):
            return Notes(self, other)
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'Note' and '{type(other)}'")

    def __str__(self):
        return f'{self.name}{self.octave}'

    def __repr__(self):
        return f'Note {self.name}{self.octave}'

    def __int__(self):
        return self.num

    def __eq__(self, other):
        return self.num == other.num

    def __lt__(self, other):
        return self.num < other

    def __le__(self, other):
        return self.num <= other

    def __gt__(self, other):
        return self.num > other

    def __ge__(self, other):
        return self.num >= other



class Rest(Note):
    def __init__(self):
        """
        Rest class for Track and Stream class. Return zeros array when
        rendering.

        Examples:
            >>> rest = mn.Rest()
            >>> rest.sin()
            array([0., 0., 0., ..., 0., 0., 0.])
        """
        self.name = 'Rest'
        self._octave = None
        self._freq = 0.
        self._num = None
        self._idx = None
        self._A4 = 440.
        self._notes = [self]

    @property
    def A4(self) -> float:
        return self._A4

    @A4.setter
    def A4(self, value):
        self._A4 = value

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, value):
        pass

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
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120,
        A4: float = 440.
    ):
        """
        Notes class. Manage multiple notes at once. Some arguments set
        in each Note are ignored and the values set in this class are
        used: duration, unit, bpm, A4.

        Args:
            notes (List[Union[Note, int, str]]):
                List of notes. Supported note types:
                    - Note (mn.Note, mn.Notes, etc.)
                    - str (note name)
                    - int (midi note number)

        \Attributes:
            - notes (List[Note]): list of notes
            - names (List[str]): list of note names
            - fullnames (List[str]): list of note fullnames
            - nums (List[int]): list of MIDI note numbers
            - duration (float): default duration when rendering
            - unit (str): default unit of duration when rendering
            - bpm (float): default BPM when rendering
            - A4 (float): tuning. frequency of A4.

        Inherited Methods:
            **These methods is the same as in the mn.Note**

            - sin: Generate sin wave of the notes
            - square: Generate square wave of the notes
            - sawtooth: Generate sawtooth wave of the notes
            - triangle: Generate triangle wave of the notes
            - render: Rendering waveform of the note
            - play: Play note sound
            - transpose: Transpose notes
            - tuning: Sound tuning

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
            raise TypeError("The Notes class does not support Note classes as input. Enter a list of notes at once as an argument.")
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
        self._nums = [note.num for note in self]
        self.duration = duration
        self.unit = unit
        self.bpm = bpm
        self.A4 = A4

    @property
    def nums(self):
        return self._nums

    @nums.setter
    def nums(self, value):
        raise Exception("nums is read only")


    def transpose(self, n_semitones: int) -> None:
        super().transpose(n_semitones)
        self.names = [note.name for note in self.notes]
        self._nums = [note.num for note in self.notes]

    def tuning(self, A4_freq: float):
        """
        Tuning based on A4.

        Args:
            A4_freq (float): frequency of A4.

        Note:
            In this class, does not supported tuning based on other
            notes.
        """
        self.A4 = A4_freq


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
            A4=self.A4
        )


    def __len__(self):
        return len(self.notes)

    def __getitem__(self, index):
        return self.notes[index]

    def __iter__(self):
        return iter(self.notes)

    def __add__(self, other):
        return Notes(self, other)

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
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120,
        A4: float = 440.
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
            - duration (float): default duration when rendering
            - unit (str): default unit of duration when rendering
            - bpm (float): default BPM when rendering
            - A4 (float): tuning. frequency of A4 when playing sound.

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

        Note:
            Unlike Note, the argument value takes precedence over the
            input string.
        """
        root_name, type = chord_name_formatting(chord_name, type)
        root = Note(root_name, octave)
        name = root.name + type
        interval = chord_names[type]

        self.name = name
        self._type = type
        self._interval = interval
        self.root = root
        self._idxs = [(self.root.idx + i) % 12 for i in self.interval]
        super().__init__(
            [self.root.num + i for i in self.interval],
            duration=duration,
            unit=unit,
            bpm=bpm,
            A4=A4
        )

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
        self.name = self.root.name + self.type
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
