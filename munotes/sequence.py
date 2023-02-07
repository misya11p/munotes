from .notes import Note, Notes
import numpy as np
import IPython.display as ipd
from typing import List, Tuple, Union, Optional, Callable
import warnings



NotesSequence = List[Tuple[Union[Note, Notes], float]]

class Track:
    def __init__(
        self,
        sequence: NotesSequence,
        unit: str = "s",
        bpm: Optional[float] = None,
        A4: float = 440,
    ):
        assert unit in ["s", "ms", "ql"], "unit must be in ['s', 'ms', 'ql']"
        if bpm == None:
            if unit == "ql":
                raise Exception("bpm is required when unit is 'ql'")
        else:
            if unit != "ql":
                warnings.warn("bpm is not required when unit is not 'ql'")
            assert bpm > 0, "bpm must be greater than 0"

        self.sequence = sequence
        self.unit = unit
        self.bpm = bpm
        self._A4 = A4
        self.tuning(self._A4)

    @property
    def A4(self):
        return self._A4

    @A4.setter
    def A4(self, value):
        raise Exception("A4 can not be changed. If you want to tuning the note, use tune() method.")


    def sin(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        return self._gen_waveform("sin", sr, release)

    def square(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        return self._gen_waveform("square", sr, release)

    def sawtooth(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        return self._gen_waveform("sawtooth", sr, release)

    def perform(self, waveform: Callable, sr: int = 22050, release: int = 200) -> np.ndarray:
        return self._gen_waveform("perform", sr, release, waveform)


    def _to_sec(self, duration: float) -> float:
        if self.unit == "s":
            return duration
        elif self.unit == "ms":
            return duration / 1000
        elif self.unit == "ql":
            return duration * 60 / self.bpm

    def _gen_waveform(
        self,
        waveform_type: str,
        sr: int = 22050,
        release: int = 200,
        waveform_func: Optional[Callable] = None
    ) -> np.ndarray:
        y = np.array([])
        for note, duration in self.sequence:
            sec = self._to_sec(duration)
            if waveform_type == "perform":
                y_ = getattr(note, "perform")(waveform_func, sec, sr)
            else:
                y_ = getattr(note, waveform_type)(sec, sr)
            release = min(len(y_), release)
            if release:
                window = np.linspace(1, 0, release)
                y_[-release:] *= window
            y = np.append(y, y_)
        return y


    def render(self, waveform: str = 'sin', release: int = 200) -> ipd.Audio:
        """
        Render note as IPython.display.Audio object.

        Args:
            waveform (Union[str, Callables], optional): waveform type or waveform function. Defaults to 'sin'.

        Returns:
            ipd.Audio: Audio object
        """
        sr = 22050
        if isinstance(waveform, str):
            assert waveform in ['sin', 'square', 'sawtooth'], "waveform string must be in ['sin', 'square', 'sawtooth']"
            wave = getattr(self, waveform)(sr, release)
        else:
            wave = self.perform(waveform, sr, release)
        return ipd.Audio(wave, rate=sr)


    def tuning(self, A4: float = 440) -> None:
        for note, _ in self.sequence:
            note.tuning(A4)
