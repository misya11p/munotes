import numpy as np
import IPython.display as ipd
from .note import Note
from .chord import Chord
from typing import List, Union

class Notes:
    def __init__(self, notes: Union[List[Note], Chord], octave: int = 4):
        """
        Notes class.

        Args:
            notes (Union[List[Note], Chord]): list of Note or Chord
            octave (int, optional): octave of the root note. when notes is list of notes, this argument is ignored. Defaults to 4.
        """
        if isinstance(notes, Chord):
            root_num = Note(notes.root.name, octave).num
            notes = [Note(root_num + i) for i in notes.interval]
        else:
            assert all([note.exist_octave for note in notes]), "all notes must have octave"
        self.notes = notes
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