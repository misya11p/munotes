from __future__ import annotations
from .format import check_nname
import numpy as np
from scipy import signal
import IPython.display as ipd
from typing import Union, Callable
import re



NUM_C0 = 12
NUM_A4 = 69
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class Note:
    def __init__(self, query: Union[str, int], octave: int = 4, A4: float = 440.):
        """
        Note class.

        Args:
            query (Union[str, int]): string of note name or midi note number.
            octave (int, optional): octave of the note. Defaults to 4.
            A4 (float, optional): tune. freqency of A4. Defaults to 440.
        """
        assert isinstance(query, (str, int)), "input must be a string or an integer"

        if isinstance(query, str):
            self.name = check_nname(query, return_nname=True)
            self.idx = self._return_idx()
            self.octave = octave
            self.num = NUM_C0 + 12*self.octave + self.idx
        else:
            assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
            self.num = query
            self.name = KEY_NAMES[(self.num - NUM_C0) % 12]
            self.idx = self._return_idx()
            self.octave = (self.num - NUM_C0) // 12

        self.exist_octave = self.octave != None
        self._A4 = A4
        self.freq = self._A4 * 2**((self.num - NUM_A4)/12)


    @property
    def A4(self) -> float:
        return self._A4

    @A4.setter
    def A4(self, value):
        raise Exception("A4 can not be changed. If you want to tune the note, use tune() method.")


    def transpose(self, n_semitones: int) -> None:
        """
        Transpose note.

        Args:
            n_semitones (int): number of semitones to transpose
        """
        self.idx = (self.idx + n_semitones) % 12
        self.name = KEY_NAMES[self.idx]
        self.num += n_semitones
        self.octave = (self.num - NUM_C0) // 12
        self.freq = self._A4 * 2**((self.num - NUM_A4)/12)


    def _return_time_axis(self, sec: float, sr: int) -> np.ndarray:
        """Generate time axis"""
        assert self.exist_octave, "octave is not defined"
        return np.linspace(0, 2*np.pi * self.freq * sec, int(sr*sec))


    def sin(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate sin wave of the note.

        Args:
            sec (float, optional): duration in seconds. Defaults to 1.0.
            sr (int, optional): sampling rate. Defaults to 22050.

        Returns:
            np.ndarray: sin wave of the note
        """
        t = self._return_time_axis(sec, sr)
        return np.sin(t)


    def square(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate square wave of the note.

        Args:
            sec (float, optional): duration in seconds. Defaults to 1.0.
            sr (int, optional): sampling rate. Defaults to 22050.

        Returns:
            np.ndarray: square wave of the note
        """
        t = self._return_time_axis(sec, sr)
        return signal.square(t)


    def sawtooth(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate sawtooth wave of the note.

        Args:
            sec (float, optional): duration in seconds. Defaults to 1.0.
            sr (int, optional): sampling rate. Defaults to 22050.

        Returns:
            np.ndarray: sawtooth wave of the note
        """
        t = self._return_time_axis(sec, sr)
        return signal.sawtooth(t)


    def perform(self, waveform: Callable, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Perform note.

        Args:
            waveform (Callables): waveform function
            sec (float, optional): duration in seconds. Defaults to 1.
            sr (int, optional): sampling rate. Defaults to 22050.

        Returns:
            np.ndarray: wave of the note
        """
        t = self._return_time_axis(sec, sr)
        return waveform(t)


    def render(self, waveform: Union[str, Callable] = 'sin', sec: float = 1.,) -> ipd.Audio:
        """
        Render note as IPython.display.Audio object.

        Args:
            waveform (Union[str, Callables], optional): waveform type or waveform function. Defaults to 'sin'.
            sec (float, optional): duration in seconds. Defaults to 1.

        Returns:
            ipd.Audio: Audio object
        """
        sr = 22050
        if isinstance(waveform, str):
            assert waveform in ['sin', 'square', 'sawtooth'], "waveform string must be in ['sin', 'square', 'sawtooth']"
            wave = getattr(self, waveform)(sec, sr)
        else:
            wave = self.perform(waveform, sec, sr)
        return ipd.Audio(wave, rate=sr)


    def tune(self, A4_freq: float = 440.) -> None:
        """
        tune the sound of note.

        Args:
            A4_freq (float, optional): freqency of A4. Defaults to 440.
        """
        self._A4 = A4_freq
        self.freq = self._A4 * 2**((self.num - NUM_A4)/12)


    def _return_idx(self):
        idx = KEY_NAMES.index(self.name[0])
        idx = (idx + ('#' in self.name) - ('b' in self.name)) % 12
        return idx

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




class Notes:
    def __init__(self, *notes: Union[Note, Notes, Chord], A4: float = 440.):
        """
        Notes class.

        Args:
            *notes (Union[Note, Chord, Notes]): notes
            A4 (float, optional): Frequency of A4. Defaults to 440..
        """
        assert notes, "Notes must be input"
        self.notes = []
        for note in notes:
            if isinstance(note, Note):
                assert note.exist_octave, "Input Note must have octave"
                self.notes.append(note)
            else:
                self.notes += note.notes
        self.n_notes = len(self)
        self._A4 = A4
        self.tune(self.A4)

    @property
    def A4(self):
        return self._A4

    @A4.setter
    def A4(self, value):
        raise Exception("A4 can not be changed. If you want to tune the note, use tune() method.")


    def transpose(self, n_semitones: int) -> None:
        """
        Transpose notes.

        Args:
            n_semitones (int): number of semitones to transpose
        """
        for note in self.notes:
            note.transpose(n_semitones)


    def sin(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate sin wave of the notes.

        Args:
            sec (float): duration in seconds
            sr (int): sampling frequency

        Returns:
            np.ndarray: sin wave of the notes
        """
        return np.sum([note.sin(sec, sr) for note in self.notes], axis=0)


    def square(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate square wave of the notes.

        Args:
            sec (float): duration in seconds
            sr (int): sampling frequency

        Returns:
            np.ndarray: square wave of the notes
        """
        return np.sum([note.square(sec, sr) for note in self.notes], axis=0)


    def sawtooth(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate sawtooth wave of the notes.

        Args:
            sec (float): duration in seconds
            sr (int): sampling frequency

        Returns:
            np.ndarray: sawtooth wave of the notes
        """
        return np.sum([note.sawtooth(sec, sr) for note in self.notes], axis=0)


    def perform(self, waveform: Callable, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Perform note.

        Args:
            waveform (Callable): waveform function
            sec (float, optional): duration in seconds. Defaults to 1.
            sr (int, optional): sampling rate. Defaults to 22050.

        Returns:
            np.ndarray: wave of the note
        """
        return np.sum([note.perform(waveform, sec, sr) for note in self.notes], axis=0)


    def render(self, waveform: str = 'sin', sec: float = 1.) -> ipd.Audio:
        """
        Render note as IPython.display.Audio object.

        Args:
            waveform (Union[str, Callables], optional): waveform type or waveform function. Defaults to 'sin'.
            sec (float, optional): duration in seconds. Defaults to 1.

        Returns:
            ipd.Audio: Audio object
        """
        sr = 22050
        if isinstance(waveform, str):
            assert waveform in ['sin', 'square', 'sawtooth'], "waveform string must be in ['sin', 'square', 'sawtooth']"
            wave = getattr(self, waveform)(sec, sr)
        else:
            wave = self.perform(waveform, sec, sr)
        return ipd.Audio(wave, rate=sr)


    def tune(self, freq: float = 440.) -> None:
        """
        tune the sound of notes.

        Args:
            freq (float, optional): Freqency of A4. Defaults to 440.
        """
        self._A4 = freq
        for note in self.notes:
            note.tune(freq)


    def append(self, note: Union[Note, Notes, Chord]) -> None:
        """
        Append note.

        Args:
            note (Union[Note, Notes, Chord]): note
        """
        self = Notes(self, note)
        self.n_notes = len(self)


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
    def __init__(self, cname: str, octave: int = 4):
        """
        Chord class.

        Args:
            cname (str): chord name string
            octave (int, optional): root note octave of the sound.
        """
        cname = nname_formatting(cname)
        pitch_search = re.match(PITCH_PATTERN, cname)
        assert pitch_search, f"'{cname}' is an invalid string"

        border = pitch_search.end()
        root_name, type = cname[:border], cname[border:]
        root = Note(root_name, octave)
        name = root.name + type
        interval = chord_intervals[type]

        self.name = name
        self.root = root
        self.interval = interval
        self.bass = None
        self.type = type
        self.octave = octave
        self._compose()


    def transpose(self, n_semitones: int):
        """
        transpose chord

        Args:
            n_semitones (int): number of semitones to transpose
        """
        self.root.transpose(n_semitones)
        self._compose()


    def _compose(self):
        """Define other attributes based on note name"""
        self.name = self.root.name + self.type
        self.idx = [(self.root.idx + i) % 12 for i in self.interval]
        self.note_names = [KEY_NAMES[i] for i in self.idx]
        self.notes = [Note(self.root.num + i) for i in self.interval]


    def __repr__(self):
        return f'Chord {self.name}'

    def __str__(self):
        return self.name