from .notes import Note, Notes
import numpy as np
import IPython
from typing import List, Tuple, Union, Optional, Callable, Iterable
import warnings

PLAY_SR = 22050 # sample rate for play()
SPPORTED_UNITS = ["s", "ms", "ql"]



class Track:
    def __init__(
        self,
        sequence: List[Tuple[Union[Note, str, int], float]],
        unit: str = "s",
        bpm: Optional[float] = None,
        A4: float = 440,
    ):
        """
        Track class.
        Input notes and durations to manage multiple notes as a track.

        Args:
            sequence (List[Tuple[Note, float]]):
                sequence of notes and durations.
            unit (str, optional):
                unit of duration.
                supported units:
                    - 's': second
                    - 'ms': millisecond
                    - 'ql': quarter length (bpm is required)
            bpm (Optional[float], optional):
                BPM (beats per minute). Required when unit is 'ql'.
            A4 (float, optional):
                tuning. frequency of A4.

        \Attributes:
            - sequence (List[Tuple[Note, float]]): sequence of notes and durations.
            - unit (str): unit of duration.
            - bpm (Optional[float]): BPM (beats per minute).
            - A4 (float): tuning. frequency of A4.

        Main Methods:
            **These methods is the same as in the mn.Notes.**

            - sin: Generate sin wave of the notes
            - square: Generate square wave of the notes
            - sawtooth: Generate sawtooth wave of the notes
            - render: Rendering waveform of the note
            - play: Play note sound
            - transpose: Transpose notes
            - tuning: Sound tuning

        Note:
            There are some changes regarding methods that handle waveforms
            (``sin()``, ``render()``, etc.).

            1. Remove ``sec`` argument.
            2. Add ``release: int = 200`` argument. It is release time in samples.
               Wavefrom will be multiplied by a linear window from 1 to 0 in the
               last ``release`` samples to connect sounds smoothly.

        Examples:
            >>> import munotes as mn
            >>> track = mn.Track([
            >>>     (mn.Note("C4"), 1),
            >>>     (mn.Note("D4"), 1),
            >>>     (mn.Note("E4"), 1),
            >>>     (mn.Chord("C", 1),
            >>> ])
            >>> track
            Track [(Note C4, 1), (Note E4, 1), (Note G4, 1), (Chord C, 1)]

            >>> track.sin()
            array([ 0.        ,  0.07448499,  0.14855616, ..., -0.01429455,
                -0.00726152, -0.        ])

            You can also input notes as str or int directly.

            >>> track = mn.Track([
            >>>     ("C4", 1),
            >>>     ("D4", 1),
            >>>     ("E4", 1),
            >>> ])
            >>> track
            Track [(Note C4, 1), (Note E4, 1), (Note G4, 1)]
        """
        assert unit in SPPORTED_UNITS, f"unit must be in {SPPORTED_UNITS}"
        if bpm == None:
            if unit == "ql":
                raise Exception("bpm is required when unit is 'ql'")
        else:
            if unit != "ql":
                warnings.warn("bpm is not required when unit is not 'ql'")
            assert bpm > 0, "bpm must be greater than 0"

        sequence_ = []
        for note, duration in sequence:
            if isinstance(note, (str, int)):
                note = Note(note)
            elif isinstance(note, Note):
                pass
            else:
                raise ValueError("note must be Note, str or int")
            sequence_.append((note, duration))

        self._sequence = sequence_
        self._unit = unit
        self.bpm = bpm
        self.A4 = A4

    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, value):
        raise Exception("Cannot set sequence directly")

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        raise Exception("unit can not be changed.")

    @property
    def A4(self):
        return self._A4

    @A4.setter
    def A4(self, value):
        self._A4 = value
        for note, _ in self.sequence:
            note.A4 = value


    def sin(self, sr: int = 22050, release: int = 200) -> np.ndarray:
        """Generate sin wave of the track"""
        return self._gen_y("sin", sr, release)

    def square(
        self,
        sr: int = 22050,
        release: int = 200,
        duty: float = 0.5
    ) -> np.ndarray:
        """Generate square wave of the note with scipy.signal.square"""
        return self._gen_y("square", sr, release, duty=duty)

    def sawtooth(
        self,
        sr: int = 22050,
        release: int = 200,
        width: float = 1.
    ) -> np.ndarray:
        """Generate sawtooth wave of the note"""
        return self._gen_y("sawtooth", sr, release, width=width)

    def render(
        self,
        waveform: Union[str, Callable] = 'sin',
        sr: int = 22050,
        release: int = 200,
        **kwargs
    ) -> np.ndarray:
        """Rendering waveform of the track"""
        return self._gen_y(waveform, sr, release, **kwargs)

    def _gen_y(
        self,
        waveform: Union[str, Callable],
        sr: int = 22050,
        release: int = 200,
        **kwargs
    ) -> np.ndarray:
        """
        Generate waveform of the note from various query types.

        Args:
            waveform (Union[str, Callable]): waveform type. str or callable object.
            sr (int, optional): sampling rate.
            release (int, optional): release time in samples.
            **kwargs: keyword arguments for waveform function.

        Returns:
            np.ndarray: waveform of the note
        """
        y = np.array([])
        for note, duration in self.sequence:
            sec = self._to_sec(duration)
            y_note = note.render(waveform, sec, sr, **kwargs)
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
        release: int = 200,
        **kwargs
    ) -> IPython.display.Audio:
        """Play note sound in IPython notebook"""
        y = self.render(waveform, PLAY_SR, release, **kwargs)
        return IPython.display.Audio(y, rate=PLAY_SR)


    def tuning(self, A4_freq: float = 440.) -> None:
        """Tuning"""
        self.A4 = A4_freq

    def transpose(self, semitone: int) -> None:
        """Transpose notes"""
        for note, _ in self.sequence:
            note.transpose(semitone)


    def append(self, *note: Tuple[Union[Note, str, int], float]) -> None:
        """
        Append notes.

        Args:
            *note (Tuple[Note, float]): note

        Example:
            >>> track = mn.Track([
            >>>     ("C4", 1),
            >>>     ("D4", 1),
            >>> ])
            >>> track.append(("E4", 1))
            >>> track
            Track [(C4, 1), (D4, 1), (E4, 1)]
        """
        self._sequence += Track(note, self.unit, self.bpm, self.A4).sequence

    def __len__(self) -> int:
        return len(self.sequence)

    def __iter__(self) -> Iterable:
        return iter(self.sequence)

    def __getitem__(self, index: int) -> Tuple[Note, float]:
        return self.sequence[index]

    def __repr__(self) -> str:
        return f"Track {self.sequence}"



Waveforms = List[Union[str, Callable]]

class Stream(Track):
    def __init__(self, tracks: List[Track], A4: float = 440.):
        """
        Stream class. Manage multiple tracks as a stream.

        Args:
            tracks (List[Track]): tracks
            A4 (float, optional): frequency of A4.

        Inherited Methods:
            **These methods is the same as in the mn.Note**

            - sin: Generate sin wave of the notes
            - square: Generate square wave of the notes
            - sawtooth: Generate sawtooth wave of the notes
            - render: Rendering waveform of the note
            - play: Play note sound
            - transpose: Transpose notes
            - tuning: Sound tuning

        Note:
            In ``render()`` and ``play()``, waveforms can be specified for
            each track by inputting as many waveforms as there are tracks.

        Example:
            >>> melody = mn.Track([
            >>>     ("C4", 1),
            >>>     ("D4", 1),
            >>>     ("E4", 1)
            >>> ])
            >>> chords = mn.Track([(mn.Chord("C"), 3)])
            >>> stream = mn.Stream([melody, chords])
            >>> stream
            Stream [Track [(Note C4, 1), (Note D4, 1), (Note E4, 1)], Track [(Chord C, 3)]]

            >>> stream.render('sin')
            array([ 0.        ,  0.35422835,  0.70541282, ..., -0.02489362,
                   -0.01173826,  0.        ])

            >>> stream.render([
            >>>     'square',
            >>>     lambda t: np.sin(t) + np.sin(2*t)
            >>>     ])
            array([ 1.        ,  1.83660002,  2.64969075, ..., -0.05431521,
                   -0.02542138,  0.        ])
        """
        self._tracks = tracks
        self.A4 = A4

    @property
    def tracks(self):
        return self._tracks

    @tracks.setter
    def tracks(self, value):
        raise Exception("Cannot set tracks directly")

    @property
    def A4(self):
        return self._A4

    @A4.setter
    def A4(self, value):
        self._A4 = value
        for track in self.tracks:
            track.A4 = value


    def render(
        self,
        waveform: Union[str, Callable, Waveforms] = 'sin',
        sr: int = 22050,
        release: int = 200,
        **kwargs
    ) -> np.ndarray:
        """
        Rendering waveform of the stream. Spported multiple waveforms.

        Args:
            waveform (Union[str, Callable, Waveforms], optional):
                waveform or list of waveforms.

        Note:
            Basic usage is the same as in the other classes. But in kwargs,
            only 'duty' for 'square' and 'width' for 'sawtooth' are supported
            if input multiple waveforms.
        """
        return super().render(waveform, sr, release, **kwargs)


    def _gen_y(
        self,
        waveform: Union[str, Callable, Waveforms],
        sr: int,
        release: int,
        **kwargs
    ) -> np.array:
        """Generate waveform of the note from various query types"""
        if isinstance(waveform, str) or callable(waveform):
            waveforms = [waveform] * len(self)
        elif hasattr(waveform, '__iter__'):
            assert len(waveform) == len(self), \
                f"If input multiple waveforms, its length must have the same as the number of tracks: {len(self)}"
            if kwargs:
                assert all(kwarg in ['duty', 'width'] for kwarg in kwargs), \
                    "If input multiple waveforms, only 'duty' for 'square' and 'width' for 'sawtooth' are supported for kwargs."
            waveforms = waveform
        else:
            raise Exception("Invalid waveform type. Must be str, callable, or list of str or callable.")

        y = np.array([])
        for track, waveform in zip(self.tracks, waveforms):
            if waveform == 'square':
                kwarg = {'duty': kwargs['duty']} if 'duty' in kwargs else {}
            elif waveform == 'sawtooth':
                kwarg = {'width': kwargs['width']} if 'width' in kwargs else {}
            else:
                kwarg = {}

            y_track = track.render(waveform, sr, release, **kwarg)
            if len(y_track) > len(y):
                y = np.append(y, np.zeros(len(y_track) - len(y)))
            else:
                y_track = np.append(y_track, np.zeros(len(y) - len(y_track)))
            y += y_track
        return y


    def transpose(self, semitone: int) -> None:
        """Transpose notes"""
        for note in self.tracks:
            note.transpose(semitone)


    def append(self, *track: Track) -> None:
        self._tracks += Stream(track, self.A4).tracks

    def __len__(self) -> int:
        return len(self.tracks)

    def __iter__(self) -> Iterable:
        return iter(self.tracks)

    def __getitem__(self, index: int) -> Track:
        return self.tracks[index]

    def __repr__(self) -> str:
        return f"Stream {self.tracks}"