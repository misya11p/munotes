from typing import List, Tuple, Union, Optional, Callable, Iterable
import numpy as np
from ._base import BaseNotes
from .notes import Note
from .envelope import Envelope


def flatten_notes(notes: List[Note]) -> List[Note]:
    flat_notes = []
    for notes_ in notes:
        flat_notes.extend(notes_._notes)
    return flat_notes


class Track(BaseNotes):
    def __init__(
        self,
        sequence: List[Note],
        waveform: Optional[Union[str, Callable]] = None,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        sr: int = 22050,
        A4: float = 440,
    ):
        """
        Track class. Manage multiple notes as a sequence. If inputed
        specific arguments or set default attributes, these apply to all
        notes in the sequence when rendering. If not, each note will be
        rendered with its own attributes.

        Args:
            sequence (List[Note]): sequence of notes.

        \Attributes:
            - sequence (List[Note]): sequence of notes.
            - waveform, duration, unit, bpm, A4:
                Default attributes for rendering waveform

        Main Methods:
            **These methods is the same as in the ``Note``.**

            - sin: Generate sin wave of the notes
            - square: Generate square wave of the notes
            - sawtooth: Generate sawtooth wave of the notes
            - triangle: Generate triangle wave of the notes
            - render: Rendering waveform of the note
            - play: Play note sound
            - transpose: Transpose notes
            - tuning: Sound tuning

        Note:
            There are some changes regarding methods that handle
            waveforms (``sin()``, ``render()``, etc.).

            1. Remove ``sec`` argument.
            2. Add ``release: int = 200`` argument. It is release time
               in samples. Wavefrom will be multiplied by a linear
               window from 1 to 0 in the last ``release`` samples to
               connect sounds smoothly.

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
        assert sequence, "sequence must not be empty"
        self.sequence = sequence
        self._notes = flatten_notes(self.sequence)
        self._init_attrs(
            waveform=waveform,
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            sr=sr,
            A4=A4
        )

    _default_envelope = Envelope(
        attack=0.,
        decay=0.,
        sustain=1.,
        release=0.01,
        hold=0.,
    )

    def render(
        self,
        waveform: Optional[Union[str, Callable]] = None,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        **kwargs
    ) -> np.ndarray:
        """Rendering waveform of the track"""
        y = np.array([])
        for note in self:
            y_note = note.render(
                waveform=waveform or self.waveform,
                duration=duration or self.duration,
                unit=unit or self.unit,
                bpm=bpm or self.bpm,
                envelope=envelope or self.envelope,
                **kwargs
            )
            if len(y):
                release = int(self.sr * self.release)
                y = np.append(y, np.zeros(len(y_note) - release))
                y[-len(y_note):] += y_note
            else:
                y = y_note
        y = self._normalize(y)
        return y

    def append(self, *notes: Note) -> None:
        """
        Append notes to the track.

        Args:
            *notes (Note): notes to append

        Example:
            >>> track = mn.Track([
            >>>     ("C4", 1),
            >>>     ("D4", 1),
            >>> ])
            >>> track.append(("E4", 1))
            >>> track
            Track [(C4, 1), (D4, 1), (E4, 1)]
        """
        self.sequence.extend(notes)
        self._notes = flatten_notes(self.sequence)

    def __len__(self) -> int:
        return len(self.sequence)

    def __iter__(self) -> Iterable:
        return iter(self.sequence)

    def __getitem__(self, index: int) -> Tuple[Note, float]:
        return self.sequence[index]

    def __repr__(self) -> str:
        return f"Track {self.sequence}"


class Stream(BaseNotes):
    def __init__(
        self,
        tracks: List[Track],
        waveform: Optional[Union[str, Callable]] = None,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        sr: int = 22050,
        A4: float = 440,
    ):
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
            - triangle: Generate triangle wave of the notes
            - render: Rendering waveform of the note
            - play: Play note sound
            - transpose: Transpose notes
            - tuning: Sound tuning

        Note:
            In ``render()`` and ``play()``, waveforms can be specified
            for each track by inputting as many waveforms as there are
            tracks.

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
            >>> ])
            array([ 1.        ,  1.83660002,  2.64969075, ..., -0.05431521,
                   -0.02542138,  0.        ])
        """
        self.tracks = tracks
        self._notes = flatten_notes(self.tracks)
        self._init_attrs(
            waveform=waveform,
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            sr=sr,
            A4=A4
        )

    def render(
        self,
        waveform: Optional[Union[str, Callable]] = None,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        **kwargs
    ) -> np.ndarray:
        """
        Rendering waveform of the stream. Spported multiple waveforms.

        Args:
            waveform (Union[str, Callable, Waveforms], optional):
                waveform or list of waveforms.

        Note:
            Basic usage is the same as in the other classes. But in
            kwargs, only 'duty' for 'square' and 'width' for 'sawtooth'
            are supported if input multiple waveforms.
        """
        y = np.array([])
        for track in self:
            y_track = track.render(
                waveform=waveform,
                duration=duration,
                unit=unit,
                bpm=bpm,
                envelope=envelope,
                **kwargs
            )
            if len(y_track) > len(y):
                y = np.append(y, np.zeros(len(y_track) - len(y)))
            else:
                y_track = np.append(y_track, np.zeros(len(y) - len(y_track)))
            y += y_track
        y = self._normalize(y)
        return y

    def append(self, *tracks: Track) -> None:
        self.tracks.extend(tracks)
        self._notes = flatten_notes(self.tracks)

    def __len__(self) -> int:
        return len(self.tracks)

    def __iter__(self) -> Iterable:
        return iter(self.tracks)

    def __getitem__(self, index: int) -> Track:
        return self.tracks[index]

    def __repr__(self) -> str:
        return f"Stream {self.tracks}"
