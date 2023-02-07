from .notes import Note, Notes
import numpy as np
import IPython.display as ipd
from typing import List, Tuple, Union, Optional, Callable
import warnings

PLAY_SR = 22050



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
        return self._gen_y("sin", sr, release)

    def square(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        return self._gen_y("square", sr, release)

    def sawtooth(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        return self._gen_y("sawtooth", sr, release)

    def render(self, waveform: Union[str, Callable], sr: int = 22050, release: int = 200) -> np.ndarray:
        return self._gen_y(waveform, sr, release)

    def _gen_y(
        self,
        waveform: Union[str, Callable],
        sr: int = 22050,
        release: int = 200,
    ) -> np.ndarray:
        y = np.array([])
        for note, duration in self.sequence:
            sec = self._to_sec(duration)
            y_note = note.render(waveform, sec, sr)
            release = min(len(y_note), release)
            if release:
                window = np.linspace(1, 0, release)
                y_note[-release:] *= window
            y = np.append(y, y_note)
        return y

    def _to_sec(self, duration: float) -> float:
        if self.unit == "s":
            return duration
        elif self.unit == "ms":
            return duration * 1000
        elif self.unit == "ql":
            return duration * 60 / self.bpm


    def play(self, waveform: Union[str, Callable] = 'sin', release: int = 200) -> ipd.Audio:
        y = self.render(waveform, PLAY_SR, release)
        return ipd.Audio(y, rate=PLAY_SR)


    def tune(self, A4: float = 440) -> None:
        self._A4 = A4
        for note, _ in self.sequence:
            note.tune(A4)

    def transpose(self, semitone: int) -> None:
        for note, _ in self.sequence:
            note.transpose(semitone)

    def __len__(self) -> int:
        return len(self.sequence)



Waveforms = List[Union[str, Callable]]

class Stream(Track):
    def __init__(self, tracks: List[Track], A4: float = 440.):
        self.tracks = tracks
        self.n_tracks = len(tracks)
        self._A4 = A4
        self.tune(self._A4)


    def _gen_y(
        self,
        waveform: Union[str, Callable, Waveforms] = 'sin',
        sr: int = 22050,
        release: int = 200
    ) -> np.array:
        if isinstance(waveform, str):
            waveforms = [waveform] * self.n_tracks
        elif hasattr(waveform, '__iter__'):
            assert len(waveform) == self.n_tracks, f"If input multiple waveforms, its length must have the same as the number of tracks: {self.n_tracks}"
            waveforms = waveform
        else:
            waveforms = [waveform] * self.n_tracks

        y = np.array([])
        for track, waveform in zip(self.tracks, waveforms):
            y_track = track.render(waveform, sr, release)
            if len(y_track) > len(y):
                y = np.append(y, np.zeros(len(y_track) - len(y)))
            else:
                y_track = np.append(y_track, np.zeros(len(y) - len(y_track)))
            y += y_track
        return y

    def render(
        self,
        waveform: Union[str, Callable, Waveforms] = 'sin',
        sr: int = 22050,
        release: int = 200
    ) -> np.array:
        return self._gen_y(waveform, sr, release)

    def play(
        self,
        waveform: Union[str, Callable, Waveforms] = 'sin',
        release: int = 200
    ) -> ipd.Audio:
        y = self.render(waveform, PLAY_SR, release)
        return ipd.Audio(y, rate=PLAY_SR)


    def tune(self, A4_freq: float = 440.) -> None:
        self._A4 = A4_freq
        for track in self.tracks:
            track.tune(A4_freq)

    def transpose(self, semitone: int) -> None:
        for track in self.tracks:
            track.transpose(semitone)


    def __len__(self) -> int:
        return self.n_tracks