from .notes import Note, Notes
import numpy as np
import IPython
from typing import List, Tuple, Union, Optional, Callable
import warnings

PLAY_SR = 22050 # sample rate for play()
SPPORTED_UNITS = ["s", "ms", "ql"]



NotesSequence = List[Tuple[Union[Note, Notes], float]]

class Track:
    def __init__(
        self,
        sequence: NotesSequence,
        unit: str = "s",
        bpm: Optional[float] = None,
        A4: float = 440,
    ):
        """
        Track class.
        Input notes and durations to manage multiple notes as a track.

        Args:
            sequence (NotesSequence):
                sequence of notes and durations.
            unit (str, optional):
                unit of duration.
                supported units:
                    - 's': second
                    - 'ms': millisecond
                    - 'ql': quarter length (bpm is required)
                Defaults to "s".
            bpm (Optional[float], optional):
                BPM (beats per minute). Required when unit is 'ql'.
                Defaults to None.
            A4 (float, optional):
                tuning. frequency of A4. Defaults to 440.
        """
        assert unit in SPPORTED_UNITS, f"unit must be in {SPPORTED_UNITS}"
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
        raise Exception("A4 can not be changed. If you want to tuning the note, use tuning() method.")


    def sin(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        """Generate sin wave of the note"""
        return self._gen_y("sin", sr, release)

    def square(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        """Generate square wave of the note"""
        return self._gen_y("square", sr, release)

    def sawtooth(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        """Generate sawtooth wave of the note"""
        return self._gen_y("sawtooth", sr, release)

    def render(
        self,
        waveform: Union[str, Callable] = 'sin',
        sr: int = 22050,
        release: int = 200
    ) -> np.ndarray:
        """
        Rendering waveform of the note.

        Args:
            waveform (Union[str, Callables], optional):
                waveform type or waveform function. Defaults to 'sin'.
            sr (int, optional):
                sampling rate. Defaults to 22050.
            release (int, optional):
                release time in samples. Wavefrom will be multiplied
                by a linear window from 1 to 0 in the last {release}
                samples to connect sounds smoothly. Defaults to 200.

        Returns:
            np.ndarray: waveform of the note
        """
        return self._gen_y(waveform, sr, release)

    def _gen_y(
        self,
        waveform: Union[str, Callable],
        sr: int = 22050,
        release: int = 200,
    ) -> np.ndarray:
        """
        Generate waveform of the note from various query types.

        Args:
            waveform (Union[str, Callable]): waveform type. str or callable object.
            sr (int, optional): sampling rate. Defaults to 22050.
            release (int, optional): release time in samples. Defaults to 200.

        Returns:
            np.ndarray: waveform of the note
        """
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
        """Transform duration to second based on unit"""
        if self.unit == "s":
            return duration
        elif self.unit == "ms":
            return duration * 1000
        elif self.unit == "ql":
            return duration * 60 / self.bpm


    def play(
        self,
        waveform: Union[str, Callable] = 'sin',
        release: int = 200
    ) -> IPython.display.Audio:
        """
        Play note sound.
        Return IPython.display.Audio object.

        Args:
            waveform (Union[str, Callables], optional):
                waveform type or waveform function. Defaults to 'sin'.
            release (int, optional):
                release time in samples. Wavefrom will be multiplied
                by a linear window from 1 to 0 in the last {release}
                samples to connect sounds smoothly. Defaults to 200.

        Returns:
            IPython.display.Audio: audio object
        """
        y = self.render(waveform, PLAY_SR, release)
        return IPython.display.Audio(y, rate=PLAY_SR)


    def tuning(self, A4_freq: float = 440) -> None:
        """Tuning sound"""
        self._A4 = A4_freq
        for note, _ in self.sequence:
            note.tuning(A4_freq)

    def transpose(self, semitone: int) -> None:
        """Transpose notes"""
        for note, _ in self.sequence:
            note.transpose(semitone)

    def __len__(self) -> int:
        return len(self.sequence)



Waveforms = List[Union[str, Callable]]

class Stream(Track):
    def __init__(self, tracks: List[Track], A4: float = 440.):
        """
        Stream class. Manage multiple tracks as a stream.

        Args:
            tracks (List[Track]): tracks
            A4 (float, optional): frequency of A4. Defaults to 440.0.
        """
        self.tracks = tracks
        self.n_tracks = len(tracks)
        self._A4 = A4
        self.tuning(self._A4)


    def _gen_y(
        self,
        waveform: Union[str, Callable, Waveforms] = 'sin',
        sr: int = 22050,
        release: int = 200
    ) -> np.array:
        """
        Generate waveform of the note from various query types.

        Args:
            waveform (Union[str, Callables, Waveforms], optional):
                waveform. Defaults to 'sin'.
            sr (int, optional):
                sampling rate. Defaults to 22050.
            release (int, optional):
                release time in samples. Defaults to 200.

        Returns:
            np.ndarray: waveform of the note
        """
        if isinstance(waveform, str):
            waveforms = [waveform] * self.n_tracks
        elif hasattr(waveform, '__iter__'):
            assert len(waveform) == self.n_tracks, \
                f"If input multiple waveforms, its length must have the same as the number of tracks: {self.n_tracks}"
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
        """
        Rendering waveform of the note.

        Args:
            waveform (Union[str, Callables, Waveforms], optional):
                waveform.
                supported types:
                    - str: waveform type
                    - callable: waveform function
                    - list of str or callable: multiple waveforms
                Defaults to 'sin'.
            sr (int, optional):
                sampling rate. Defaults to 22050.
            release (int, optional):
                release time in samples. Wavefrom will be multiplied
                by a linear window from 1 to 0 in the last {release}
                samples to connect sounds smoothly. Defaults to 200.

        Returns:
            np.ndarray: waveform of the note
        """
        return self._gen_y(waveform, sr, release)

    def play(
        self,
        waveform: Union[str, Callable, Waveforms] = 'sin',
        release: int = 200
    ) -> IPython.display.Audio:
        """
        Play note sound.
        Return IPython.display.Audio object.

        Args:
            waveform (Union[str, Callables, Waveforms], optional):
                waveform.
                supported types:
                    - str: waveform type
                    - callable: waveform function
                    - list of str or callable: multiple waveforms
                Defaults to 'sin'.
            release (int, optional):
                release time in samples. Wavefrom will be multiplied
                by a linear window from 1 to 0 in the last {release}
                samples to connect sounds smoothly. Defaults to 200.

        Returns:
            IPython.display.Audio: audio object
        """
        y = self.render(waveform, PLAY_SR, release)
        return IPython.display.Audio(y, rate=PLAY_SR)


    def tuning(self, A4_freq: float = 440.) -> None:
        """Tuning sound"""
        self._A4 = A4_freq
        for track in self.tracks:
            track.tuning(A4_freq)

    def transpose(self, semitone: int) -> None:
        """Transpose notes"""
        for track in self.tracks:
            track.transpose(semitone)


    def __len__(self) -> int:
        return self.n_tracks