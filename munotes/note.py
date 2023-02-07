import numpy as np
from scipy import signal
import IPython.display as ipd
from typing import Optional, Union
# import warnings

def check_nname(nname: str, return_nname: bool = False) -> Optional[str]:
    """
    Check if the note name string is valid.
        if valid: return None or formatted note name
        if invalid: return error

    Args:
        nname (str): note name
        return_nname (bool, optional): Whether to return formatted note name.

    Returns:
        Optional[str]: formatted note name
    """
    assert nname, "Note name is empty"
    assert len(nname) <= 2, "Note name is too long"
    nname = nname_formatting(nname)

    if len(nname) == 1:
        assert nname in "ABCDEFG", f"One letter note name must be in {list('ABCDEFG')}"

    elif len(nname) == 2:
        assert nname[0] in "ABCDEFG", f"First letter of note name must be in {list('ABCDEFG')}"
        assert nname[1] in "#b", f"Second letter of note name must be in {list('+♯#-♭b')}"

    if return_nname:
        return nname


def nname_formatting(nname: str) -> str:
    """
    Format note name string.

    Args:
        nname (str): note name

    Returns:
        str: formatted note name
    """
    nname = nname[0].upper() + nname[1:]
    nname = nname.replace('+', '#')
    nname = nname.replace('♯', '#')
    nname = nname.replace('-', 'b')
    nname = nname.replace('♭', 'b')
    return nname


NUM_C0 = 12
NUM_A4 = 69
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class Note:
    def __init__(
        self,
        query: Union[str, int],
        octave: int = 4,
        A4: float = 440.,
    ):
        """
        Note class.

        Args:
            query (Union[str, int]): string of note name or midi note number.
            octave (int, optional): octave of the note. Defaults to 4.
            A4 (float, optional): tuning. freqency of A4. Defaults to 440.
        """
        assert isinstance(query, (str, int)), "input must be a string or an integer"

        if isinstance(query, str):
            self.name = check_nname(query, return_nname=True)
            self.idx = self._return_idx()
            self.octave = octave
            self.num = NUM_C0 + 12*self.octave + self.idx
        elif isinstance(query, int):
            assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
            self.num = query
            self.name = KEY_NAMES[(self.num - NUM_C0) % 12]
            self.idx = self._return_idx()
            self.octave = (self.num - NUM_C0) // 12
        else:
            raise ValueError("query must be a string or an integer")

        self.exist_octave = self.octave != None
        self._A4 = A4
        self.freq = self._A4 * 2**((self.num - NUM_A4)/12)


    @property
    def A4(self) -> float:
        return self._A4

    @A4.setter
    def A4(self, value):
        raise ValueError("A4 can not be changed. If you want to tuning the note, use tune() method.")


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
            sec (float): duration in seconds
            sr (int): sampling rate

        Returns:
            np.ndarray: sin wave
        """
        t = self._return_time_axis(sec, sr)
        return np.sin(t)


    def square(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate square wave of the note.

        Args:
            sec (float): duration in seconds
            sr (int): sampling rate

        Returns:
            np.ndarray: square wave
        """
        t = self._return_time_axis(sec, sr)
        return signal.square(t)


    def sawtooth(self, sec: float = 1., sr: int = 22050) -> np.ndarray:
        """
        Generate sawtooth wave of the note.

        Args:
            sec (float): duration in seconds
            sr (int): sampling rate

        Returns:
            np.ndarray: sawtooth wave
        """
        t = self._return_time_axis(sec, sr)
        return signal.sawtooth(t)


    def render(self, sec: float = 1., wave_type: str = 'sin') -> ipd.Audio:
        """
        Render note as IPython.display.Audio object.

        Args:
            sec (float, optional): duration in seconds. Defaults to 1.
            wave_type (str, optional): wave type. Defaults to 'sin'.

        Returns:
            ipd.Audio: Audio object
        """
        assert wave_type in ['sin', 'square', 'sawtooth'], "wave_type must be in ['sin', 'square', 'sawtooth']"
        sr = 22050
        wave = getattr(self, wave_type)(sec, sr)
        return ipd.Audio(wave, rate=sr)


    def tuning(self, A4_freq: float = 440.) -> None:
        """
        Tuning the sound of note.

        Args:
            A4_freq (float, optional): freqency of A4. Defaults to 440.
        """
        self._A4 = A4_freq
        self.freq = self._A4 * 2**((self.num - NUM_A4)/12)


    def _return_idx(self):
        idx = KEY_NAMES.index(self.name[0])
        idx = (idx + ('#' in self.name) - ('b' in self.name)) % 12
        return idx


    def __str__(self) -> str:
        return f'{self.name}{self.octave}' if self.octave else self.name

    def __repr__(self):
        return f'Note {self.name}{self.octave}' if self.octave else f'Note {self.name}'

    def __int__(self) -> int:
        return self.num
