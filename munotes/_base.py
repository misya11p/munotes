from typing import Optional, Union, Callable

import numpy as np
import IPython.display as ipd

from .envelope import Envelope


NUM_C0 = 12 # MIDI note number of C0
NUM_A4 = 69 # MIDI note number of A4
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


class BaseNotes:
    def _init_attrs(
        self,
        waveform: Optional[Union[str, Callable]] = 'sin',
        duration: Optional[Union[float, int]] = 1.,
        unit: Optional[str] = "s",
        bpm: Optional[Union[float, int]] = 120,
        envelope: Optional[Envelope] = None,
        duty: Optional[float] = 0.5,
        width: Optional[float] = 1.,
        sr: int = 22050,
        A4: float = 440.
    ):
        """Initialize attributes of notes and sequence."""
        if not hasattr(self, '_notes'):
            self._notes = [self]
        self.waveform = waveform
        self.duration = duration
        self.unit = unit
        self.bpm = bpm
        self.duty = duty
        self.width = width
        self._sr = sr
        self.sr = sr
        self._A4 = A4
        self.tuning(A4, stand_A4=True)

        self.envelope = envelope or self._default_envelope
        self.envelope.sr = self.sr
        self._release = self.envelope.release

    _default_envelope = Envelope()

    @staticmethod
    def _normalize(y: np.ndarray):
        """Normalize waveform."""
        if np.max(np.abs(y)):
            return y / np.max(np.abs(y))
        else:
            return y

    @property
    def sr(self):
        return self._sr

    @sr.setter
    def sr(self, value):
        for note in self._notes:
            note._sr = value

    def transpose(self, n_semitones: int) -> None:
        """
        Transpose notes. If there are multiple notes, all notes are
        transposed by the same number of semitones.

        Args:
            n_semitones (int): Number of semitones to transpose.

        Examples:
            >>> note = mn.Note("C4")
            >>> note.transpose(1)
            >>> print(note)
            C#4
        """
        for note in self._notes:
            if not note.num:
                continue
            note._idx = (note.idx + n_semitones) % 12
            note.name = KEY_NAMES[note.idx]
            note._num += n_semitones
            note._octave = (note.num - NUM_C0) // 12
            note._freq = note._A4 * 2** ((note.num - NUM_A4) / 12)

    def tuning(self, freq: float = 440., stand_A4: bool = True) -> None:
        """
        Tuning.

        Args:
            freq (float, optional):
                Freqency of the note or A4. Defaults to 440..
            stand_A4 (bool, optional):
                If True, the tuning standard is A4. If False, the note
                frequency is changed to ``freq``, and it is only
                supported when handling a single note.

        Examples:
            >>> note = mn.Note("C4")
            >>> print(note.freq)
            >>> note.tuning(270.)
            >>> print(note.freq)
            261.6255653005986
            270.0

            >>> note = mn.Note("C4")
            >>> print(note.freq)
            >>> note.tuning(450., stand_A4=True)
            >>> print(note.freq)
            261.6255653005986
            267.5716008756122
        """
        for note in self._notes:
            if stand_A4:
                note._A4 = freq
                note._freq = note._A4 * 2 ** ((note.num - NUM_A4) / 12)
            else:
                if len(self._notes) > 1:
                    raise ValueError(
                        "``stand_A4=False`` is not supported when handling "
                        "multiple notes."
                    )
                note._freq = freq
                note._A4 = note._freq / 2 ** ((note.num - NUM_A4) / 12)

    def render(self):
        pass

    def sin(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None
    ) -> np.ndarray:
        """
        Generate sin wave of the object. It is the same as
        ``obj.render('sin')``.

        Args:
            duration (float, optional): Duration.
            unit (str, optional): Unit of duration.
            bpm (float, optional): BPM (beats per minute).
            envelope (Envelope, optional): Envelope.

        Returns:
            np.ndarray: Sin wave of the object.
        """
        return self.render(
            'sin',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope
        )

    def square(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        duty: float = 0.5
    ) -> np.ndarray:
        """
        Generate square wave of the object. It is the same as
        ``obj.render('square')``.

        Args:
            duration (float, optional): Duration.
            unit (str, optional): Unit of duration.
            bpm (float, optional): BPM (beats per minute).
            envelope (Envelope, optional): Envelope.
            duty (float, optional): Duty cycle.

        Returns:
            np.ndarray: Square wave of the object.
        """
        return self.render(
            'square',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            duty=duty
        )

    def sawtooth(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        width: float = 1.,
    ) -> np.ndarray:
        """
        Generate sawtooth wave of the object. It is the same as
        ``obj.render('sawtooth')``.

        Args:
            duration (float, optional): Duration.
            unit (str, optional): Unit of duration.
            bpm (float, optional): BPM (beats per minute).
            envelope (Envelope, optional): Envelope.
            width (float, optional): Width of sawtooth.

        Returns:
            np.ndarray: Sawtooth wave of the object.
        """
        return self.render(
            'sawtooth',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            width=width
        )

    def triangle(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None
    ) -> np.ndarray:
        """
        Generate triangle wave of the object. It is the same as
        ``obj.render('triangle')``, ``obj.sawtooth(width=0.5)``.

        Args:
            duration (float, optional): Duration.
            unit (str, optional): Unit of duration.
            bpm (float, optional): BPM (beats per minute).
            envelope (Envelope, optional): Envelope.

        Returns:
            np.ndarray: Triangle wave of the object.
        """
        return self.render(
            'triangle',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope
        )

    def play(
        self,
        waveform: Optional[Union[str, Callable]] = None,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        duty: Optional[float] = None,
        width: Optional[float] = None,
    ) -> ipd.Audio:
        """
        Play the object sound in IPython notebook. Return
        IPython.display.Audio object. This wave is generated by
        ``obj.render()``.

        Args:
            waveform (Union[str, Callables], optional): Waveform type.
            duration (float, optional): Duration.
            unit (str, optional): Unit of duration.
            bpm (float, optional):BPM (beats per minute).
            envelope (Envelope, optional): Envelope.
            duty (float, optional):
                Duty cycle for when waveform is 'square'.
            width (float, optional):
                Width for when waveform is 'sawtooth'.

        Returns:
            ipd.Audio: IPython.display.Audio object to IPython notebook.
        """
        y = self.render(
            waveform,
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            duty=duty,
            width=width
        )
        return ipd.Audio(y, rate=self.sr)
