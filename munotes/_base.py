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
        amp: Optional[float] = 1.,
        sr: int = 22050,
        A4: float = 440.,
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
        self.amp = amp
        self._sr = sr
        self.sr = sr
        self._A4 = A4
        self.tuning(A4)

        self.envelope = envelope
        if self.envelope:
            self.envelope.sr = self.sr

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

    @property
    def A4(self) -> float:
        return self._A4

    @A4.setter
    def A4(self, value):
        raise Exception("A4 is read only")

    def transpose(self, n_semitones: int) -> None:
        """
        Transpose notes. All notes are transposed by the same number of
        semitones.

        Args:
            n_semitones (int): Number of semitones to transpose.

        Examples:
            >>> notes = mn.Notes(["C4", "D4", "E4"])
            >>> notes.transpose(1)
            >>> print(notes)
            C#4 D#4 F4
        """
        for note in self._notes:
            note.transpose(n_semitones)

    def tuning(self, freq: float = 440.) -> None:
        """
        Tuning with A4.

        Args:
            freq (float, optional):
                Freqency of A4. Defaults to 440..

        Examples:
            >>> note = mn.Notes(["C4", "D4", "E4"])
            >>> print(notes.A4)
            >>> note.tuning(450.)
            >>> print(notes.A4)
            440.0
            450.0
        """
        for note in self._notes:
            note.tuning(freq)

    def render(self):
        pass

    def sin(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        amp: Optional[float] = None,
    ) -> np.ndarray:
        """
        Generate sin wave of the object. It is the same as
        ``obj.render('sin')``.

        Args:
            duration (float, optional): Duration.
            unit (str, optional): Unit of duration.
            bpm (float, optional): BPM (beats per minute).
            envelope (Envelope, optional): Envelope.
            amp (float, optional): Amplitude.

        Returns:
            np.ndarray: Sin wave of the object.
        """
        return self.render(
            'sin',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            amp=amp,
        )

    def square(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        duty: float = 0.5,
        amp: Optional[float] = None,
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
            amp (float, optional): Amplitude.

        Returns:
            np.ndarray: Square wave of the object.
        """
        return self.render(
            'square',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            duty=duty,
            amp=amp,
        )

    def sawtooth(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        width: float = 1.,
        amp: Optional[float] = None,
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
            amp (float, optional): Amplitude.

        Returns:
            np.ndarray: Sawtooth wave of the object.
        """
        return self.render(
            'sawtooth',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            width=width,
            amp=amp,
        )

    def triangle(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        envelope: Optional[Envelope] = None,
        amp: Optional[float] = None,
    ) -> np.ndarray:
        """
        Generate triangle wave of the object. It is the same as
        ``obj.render('triangle')``, ``obj.sawtooth(width=0.5)``.

        Args:
            duration (float, optional): Duration.
            unit (str, optional): Unit of duration.
            bpm (float, optional): BPM (beats per minute).
            envelope (Envelope, optional): Envelope.
            amp (float, optional): Amplitude.

        Returns:
            np.ndarray: Triangle wave of the object.
        """
        return self.render(
            'triangle',
            duration=duration,
            unit=unit,
            bpm=bpm,
            envelope=envelope,
            amp=amp,
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
        amp: Optional[float] = None,
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
            amp (float, optional): Amplitude.

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
            width=width,
            amp=amp,
        )
        return ipd.Audio(y, rate=self.sr)
