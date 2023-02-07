from __future__ import annotations

from .note import Note, KEY_NAMES, nname_formatting
import numpy as np
import IPython.display as ipd
from typing import Union, Callable
import re


class Notes:
    def __init__(self, *notes: Union[Note, Notes, Chord], A4: float = 440.):
        """
        Notes class.

        Args:
            *notes (Union[Note, Chord, Notes]): notes
            A4 (float, optional): Frequency of A4. Defaults to 440..
        """
        self.notes = []
        for note in notes:
            if isinstance(note, Note):
                assert note.exist_octave, "Input Note must have octave"
                self.notes.append(note)
            else:
                self.notes += note.notes
        self.n_notes = len(self.notes)
        self._A4 = A4

    @property
    def A4(self):
        return self._A4

    @A4.setter
    def A4(self, value):
        raise ValueError("A4 can not be changed. If you want to tuning the note, use tune() method.")


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


    def tuning(self, freq: float = 440.) -> None:
        """
        Tuning the sound of notes.

        Args:
            freq (float, optional): Freqency of A4. Defaults to 440.
        """
        for note in self.notes:
            note.tuning(freq)



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