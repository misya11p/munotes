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
        self.tune(self._A4)

    @property
    def A4(self):
        return self._A4

    @A4.setter
    def A4(self, value):
        raise Exception("A4 can not be changed. If you want to tune the note, use tune() method.")


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
            return duration * 1000
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

    def tune(self, A4: float = 440) -> None:
        self._A4 = A4
        for note, _ in self.sequence:
            note.tune(A4)

    def transpose(self, semitone: int) -> None:
        for note, _ in self.sequence:
            note.transpose(semitone)

    def __len__(self) -> int:
        return len(self.sequence)



waveforms = List[Union[str, Callable]]

class Stream(Track):
    def __init__(self, tracks: List[Track], A4: float = 440):
        self.tracks = tracks
        self._A4 = A4
        self.tune(self._A4)


    def _gen_waveform(
        self,
        waveform_type: str,
        sr: int = 22050,
        release: int = 200,
        waveform_func: Optional[Callable] = None
    ) -> np.ndarray:
        y = np.array([])
        for track in self.tracks:
            y_ = track._gen_waveform(waveform_type, sr, release, waveform_func)
            y = np.append(y, y_)
        return y


    def perform(
        self,
        waveforms: waveforms,
        sr: int = 22050,
        release: int = 200
    ) -> np.array:
        y = np.array([])
        for waveform, track in zip(waveforms, self.tracks):
            if isinstance(waveform, str):
                assert waveform in ['sin', 'square', 'sawtooth'], "waveform string must be in ['sin', 'square', 'sawtooth']"
                y_ = getattr(track, waveform)(sr, release)
            else:
                y_ = track.perform(waveform, sr, release)
            y = np.append(y, y_)
        return y


    def play(self, waveform: Union[str, Callable, waveforms] = 'sin', release: int = 200) -> ipd.Audio:
        """
        Render note as IPython.display.Audio object.

        Args:
            waveform (Union[str, Callables], optional): 'waveform type' or 'waveform function' or 'list of waveform types or functions'. Defaults to 'sin'.
            # TODO: release

        Returns:
            ipd.Audio: Audio object
        """
        sr = 22050
        if isinstance(waveform, str):
            assert waveform in ['sin', 'square', 'sawtooth'], "waveform string must be in ['sin', 'square', 'sawtooth']"
            y = getattr(self, waveform)(sr, release)
        elif hasattr(waveform, '__iter__'):
            y = self.perform(waveform, sr, release)
        else:
            y = self.render(waveform, sr, release)
        return ipd.Audio(y, rate=sr)


    def tune(self, A4: float = 440) -> None:
        self._A4 = A4
        for track in self.tracks:
            track.tune(A4)

    def transpose(self, semitone: int) -> None:
        for track in self.tracks:
            track.transpose(semitone)