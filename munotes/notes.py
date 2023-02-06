from __future__ import annotations

from .note import Note, KEY_NAMES, nname_formatting
import numpy as np
import IPython.display as ipd
from typing import Union
import re


class Notes:
    def __init__(self, *notes: Union[Note, Notes, Chord]):
        """
        Notes class.

        Args:
            *notes (Union[Note, Chord, Notes]): notes
        """
        self.notes = []
        for note in notes:
            if isinstance(note, Note):
                assert note.exist_octave, "Input Note must have octave"
                self.notes.append(note)
            else:
                self.notes += note.notes
        self.n_notes = len(self.notes)


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


    def render(self, sec: float = 1., wave_type: str = 'sin') -> ipd.Audio:
        """
        Render notes as IPython.display.Audio object.

        Args:
            sec (float, optional): duration in seconds. Defaults to 1..
            wave_type (str, optional): wave type. Defaults to 'sin'.

        Returns:
            ipd.Audio: Audio object
        """
        assert wave_type in ['sin', 'square', 'sawtooth'], "wave_type must be in ['sin', 'square', 'sawtooth']"
        sr = 22050
        wave = getattr(self, wave_type)(sec, sr)
        return ipd.Audio(wave, rate=sr)


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