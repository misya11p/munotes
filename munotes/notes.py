from __future__ import annotations
from .format import check_nname, nname_formatting
import numpy as np
from scipy import signal
import IPython
from typing import Union, Callable
import re


NUM_C0 = 12 # MIDI note number of C0
NUM_A4 = 69 # MIDI note number of A4
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
SUPPOERTED_WAVEFORMS = ["sin", "square", "sawtooth"]
PLAY_SR = 22050 # sampling rate for play()



class Note:
    def __init__(
        self,
        query: Union[str, int],
        octave: int = 4,
        A4: float = 440.
    ):
        """
        Note class.
        Single note. It can be initialized with note name or MIDI note number.

        Args:
            query (Union[str, int]): string of note name or midi note number
            octave (int, optional): octave of the note.
            A4 (float, optional): tuning. freqency of A4.

        \Attributes:
            - name (str): note name
            - octave (int): octave of the note
            - idx (int): index of the note name when C as 0
            - num (int): MIDI note number
            - freq (float): frequency of the note
            - A4 (float): tuning. freqency of A4

        Examples:
            >>> import munotes as mn
            >>> note = mn.Note("C", 4)
            >>> print(note)
            C4
        """
        if isinstance(query, str):
            self.name = check_nname(query, return_nname=True)
            self.idx = self._return_name_idx()
            self.octave = octave
            self.num = NUM_C0 + 12*self.octave + self.idx
        elif isinstance(query, int):
            assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
            self.num = query
            self.name = KEY_NAMES[(self.num - NUM_C0) % 12]
            self.idx = self._return_name_idx()
            self.octave = (self.num - NUM_C0) // 12
        else:
            raise ValueError("Input must be a string or an integer")

        self.exist_octave = self.octave != None
        self._A4 = A4
        self._freq = self._A4 * 2**((self.num - NUM_A4)/12)
        self._notes = [self]

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


    def sin(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate sin wave of the note

        Args:
            sec (float, optional): duration in seconds.
            sr (int, optional): sampling rate.

        Returns:
            np.ndarray: sin wave of the note

        Examples:
            >>> note = mn.Note("C", 4)
            >>> note.sin()
            array([ 0.        ,  0.07448499,  0.14855616, ..., -0.59706869,
            -0.65516123, -0.70961388])
        """
        t = self._return_time_axis(sec, sr)
        return np.sum(np.sin(t), axis=0)

    def square(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate square wave of the note

        Args:
            sec (float, optional): duration in seconds.
            sr (int, optional): sampling rate.

        Returns:
            np.ndarray: square wave of the note
        """
        t = self._return_time_axis(sec, sr)
        return np.sum(signal.square(t), axis=0)

    def sawtooth(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate sawtooth wave of the note

        Args:
            sec (float, optional): duration in seconds.
            sr (int, optional): sampling rate.

        Returns:
            np.ndarray: sawtooth wave of the note
        """
        t = self._return_time_axis(sec, sr)
        return np.sum(signal.sawtooth(t), axis=0)

    def render(
        self,
        waveform: Union[str, Callable] = 'sin',
        sec: float = 1.,
        sr: int = 22050
    ) -> np.ndarray:
        """
        Rendering waveform of the note.

        Args:
            waveform (Union[str, Callable], Optional):
                waveform.
                spported waveform types:
                    - 'sin'
                    - 'square'
                    - 'sawtooth'
                    - user-defined waveform function
            sec (float, optional):
                duration in seconds.
            sr (int, optional):
                sampling rate.

        Returns:
            np.ndarray: waveform of the note

        Examples:
            >>> note = mn.Note("C", 4)
            >>> note.render('sin')
            array([ 0.        ,  0.07448499,  0.14855616, ..., -0.59706869,
            -0.65516123, -0.70961388])

            >>> note.render(lambda t: np.sin(t) + np.sin(2*t))
            array([0.        , 0.23622339, 0.46803688, ..., 1.75357961, 1.72041279,
            1.66076322])

        Note:
            Generating a waveform by inputting a string into this method,
            as in ``note.render('sin')``, is the same as generating a waveform by
            calling the method directly, as in ``note.sin()``.
        """
        if isinstance(waveform, str):
            assert waveform in SUPPOERTED_WAVEFORMS, \
                f"waveform string must be in {SUPPOERTED_WAVEFORMS}"
            return getattr(self, waveform)(sec, sr)
        else:
            t = self._return_time_axis(sec, sr)
            return np.sum(waveform(t), axis=0)

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

    def play(
        self,
        waveform: Union[str, Callable] = 'sin',
        sec: float = 1.
    ) -> IPython.display.Audio:
        """
        Play note sound in IPython notebook.
        Return IPython.display.Audio object.

        Args:
            waveform (Union[str, Callables], optional):
                waveform type or waveform function.
            sec (float, optional):
                duration in seconds.

        Returns:
            IPython.display.Audio: audio object
        """
        y = self.render(waveform, sec, PLAY_SR)
        return IPython.display.Audio(y, rate=PLAY_SR)


    def transpose(self, n_semitones: int) -> None:
        """
        Transpose note.

        Args:
            n_semitones (int): number of semitones to transpose

        Examples:
            >>> note = mn.Note("C", 4)
            >>> note.transpose(1)
            >>> print(note)
            C#4
        """
        for note in self._notes:
            note.idx = (note.idx + n_semitones) % 12
            note.name = KEY_NAMES[note.idx]
            note.num += n_semitones
            note.octave = (note.num - NUM_C0) // 12
            note.freq = note._A4 * 2**((note.num - NUM_A4)/12)

    def tuning(self, freq: float = 440., stand_A4: bool = True) -> None:
        """
        Tuning sound.

        Args:
            freq (float, optional): freqency of note.
            stand_A4 (bool, optional): if True, the tuning standard is A4.

        Examples:
            >>> note = mn.Note("C", 4)
            >>> print(note.freq)
            >>> note.tuning(450.)
            >>> print(note.freq)
            261.6255653005986
            267.5716008756122

            >>> note = mn.Note("C", 4)
            >>> print(note.freq)
            >>> note.tuning(270., stand_A4=False)
            >>> print(note.freq)
            261.6255653005986
            270.0
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

    def __lt__(self, other):
        return self.num < other

    def __le__(self, other):
        return self.num <= other

    def __gt__(self, other):
        return self.num > other

    def __ge__(self, other):
        return self.num >= other



class Notes(Note):
    def __init__(self, *notes: Union[Note, Notes, int], A4: float = 440.):
        """
        Notes class. Manage multiple notes at once.

        Args:
            *notes (Union[Note, Notes, int]):
                notes.
                supported input types:
                    - Note
                    - Notes
                    - int (midi note number)
            A4 (float, optional):
                tuning. frequency of A4.

        \Attributes:
            - notes (List[Note]): list of notes
            - n_notes (int): number of notes
            - A4 (float): tuning. frequency of A4.

        \Methods:
            **The usage of these methods is the same as in the mn.Note**

            - sin: Generate sin wave of the notes
            - square: Generate square wave of the notes
            - sawtooth: Generate sawtooth wave of the notes
            - render: Rendering waveform of the note
            - play: Play note sound
            - tuning: tuning sound
            - transpose: Transpose notes

        Examples:
            >>> import musicnote as mn
            >>> notes = mn.Notes(
                    mn.Note("C", 4),
                    mn.Note("E", 4),
                    mn.Note("G", 4)
                    )
            >>> notes
            Notes [Note C4, Note E4, Note G4]

            >>> notes = mn.Notes(60, 64, 67)
            >>> notes
            Notes [Note C4, Note E4, Note G4]
        """
        assert notes, "Notes must be input"
        self.notes = []
        for note in notes:
            if isinstance(note, Notes):
                self.notes += note.notes
            elif isinstance(note, Note):
                self.notes.append(note)
            elif isinstance(note, int):
                self.notes.append(Note(note))
            else:
                raise ValueError(f"Unsupported type: '{type(note)}'")
        self._notes = self.notes
        self.n_notes = len(self)
        self.names = [note.name for note in self.notes]
        self.nums = [note.num for note in self.notes]
        self._A4 = A4
        self.tuning(self.A4)


    def tuning(self, A4_freq: float):
        self.A4 = A4_freq


    def append(self, note: Union[Note, Notes, int]) -> None:
        """
        Append note.

        Args:
            note (Union[Note, Notes]): Note or Notes or midi note number

        Examples:
            >>> notes = mn.Notes(mn.Note("C", 4))
            >>> notes.append(mn.Note("E", 4))
            >>> notes
            Notes [Note C4, Note E4]
        """
        self = Notes(self, note)


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
        return f'Notes {self.notes}'



chord_intervals = {
    "": (0,4,7),
    "m": (0,3,7),
    "7": (0,4,7,10),
    "m7": (0,3,7,10),
    "M7": (0,4,7,11),
    "mM7": (0,3,7,11),
    "sus4": (0,5,7),
    "dim": (0,3,6),
    "dim7": (0,3,6,9),
    "aug": (0,4,8),
    "6": (0,4,7,9),
    "m6": (0,3,7,9),
    "sus2": (0,2,7)
}
chords = list(chord_intervals.keys())
PITCH_PATTERN = '[A-G][#, b]*'

class Chord(Notes):
    def __init__(self, chord_name: str, octave: int = 4, A4: float = 440.):
        """
        Chord class.
        Estimating notes from chord names and creating a notes object.

        Args:
            chord_name (str):
                chord name string
            octave (int, optional):
                octave of the root note when playing sound.
            A4 (float, optional):
                tuning. frequency of A4 when playing sound.

        \Attributes:
            - name (str): chord name
            - root (Note): root note.
            - interval (tuple): interval of the chord. Ex: (0,4,7) for C major
            - type (str): chord type. Ex: "m" for C minor
            - octave (int): octave of the root note when playing sound.
            - A4 (float): tuning. frequency of A4 when playing sound.
            - note_names (tuple): note names of the chord.
            - notes (List[Note]): notes of the chord.
            - idx (int): index of the root note.

        Examples:
            >>> import musicnotes as mn
            >>> chord = mn.Chord("C")
            >>> chord.note_names
            ['C', 'E', 'G']
        """
        chord_name = nname_formatting(chord_name)
        pitch_search = re.match(PITCH_PATTERN, chord_name)
        assert pitch_search, f"'{chord_name}' is an invalid string"

        border = pitch_search.end()
        root_name, type = chord_name[:border], chord_name[border:]
        root = Note(root_name, octave)
        name = root.name + type
        interval = chord_intervals[type]

        self.name = name
        self.root = root
        self.interval = interval
        self.type = type
        super().__init__(*[self.root.num + i for i in self.interval], A4=A4)


    def transpose(self, n_semitones: int):
        """
        Transpose chord

        Examples:
            >>> chord = mn.Chord("C")
            >>> chord.transpose(1)
            >>> chord.note_names
            ['C#', 'F', 'G#']
        """
        super().transpose(n_semitones)
        self.root = self.notes[0]
        self.name = self.root.name + self.type
        self.idxs = [(self.root.idx + i) % 12 for i in self.interval]


    def __repr__(self):
        return f'Chord {self.name}'

    def __str__(self):
        return self.name