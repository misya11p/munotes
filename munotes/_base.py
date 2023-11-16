from typing import Optional, Union, Callable
import numpy as np
import IPython.display as ipd


NUM_C0 = 12 # MIDI note number of C0
NUM_A4 = 69 # MIDI note number of A4
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
SPPORTED_UNITS = ["s", "ms", "ql"]


class BaseNotes:
    def _init_attr(
        self,
        waveform: Union[str, Callable] = 'sin',
        duration: Union[float, int] = 1.,
        unit: str = "s",
        bpm: Union[float, int] = 120,
        sr: int = 22050,
        A4: float = 440.
    ):
        if not hasattr(self, '_notes'):
            self._notes = [self]
        assert unit in SPPORTED_UNITS, f"unit must be in {SPPORTED_UNITS}"
        self.waveform = waveform
        self.duration = duration
        self.unit = unit
        self.bpm = bpm
        self._sr = sr
        self.sr = sr
        self._A4 = A4
        self.tuning(A4, stand_A4=True)

    @property
    def sr(self):
        return self._sr

    @sr.setter
    def sr(self, value):
        for note in self._notes:
            note._sr = value

    def transpose(self, n_semitones: int) -> None:
        """
        Transpose note.

        Args:
            n_semitones (int): number of semitones to transpose

        Examples:
            >>> note = mn.Note("C4")
            >>> note.transpose(1)
            >>> print(note)
            C#4
        """
        for note in self._notes:
            note._idx = (note.idx + n_semitones) % 12
            note.name = KEY_NAMES[note.idx]
            note._num += n_semitones
            note._octave = (note.num - NUM_C0) // 12
            note._freq = note._A4 * 2** ((note.num - NUM_A4) / 12)

    def tuning(self, freq: float = 440., stand_A4: bool = True) -> None:
        """
        Tuning.

        Args:
            freq (float, optional): freqency of note.
            stand_A4 (bool, optional):
                if True, the tuning standard is A4.

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
        if len(self._notes) == 1:
            note = self._notes[0]
            if stand_A4:
                note._A4 = freq
                note._freq = note._A4 * 2 ** ((note.num - NUM_A4) / 12)
            else:
                note._freq = freq
                note._A4 = note._freq / 2 ** ((note.num - NUM_A4) / 12)
        else:
            if not stand_A4:
                raise ValueError(
                    "``stand_A4=False`` is not supported when handling "
                    "multiple notes."
                )
            for note in self._notes:
                note.tuning(freq, stand_A4=True)

    def render(self):
        pass

    def sin(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
    ) -> np.ndarray:
        """
        Generate sin wave of the note. It is the same as 
        ``Note.render('sin')``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)

        Returns:
            np.ndarray: sin wave of the note
        """
        return self.render('sin', duration=duration, unit=unit, bpm=bpm)

    def square(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        duty: float = 0.5
    ) -> np.ndarray:
        """
        Generate square wave of the note. It is the same as
        ``Note.render('square')``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)
            duty (float, optional): duty cycle

        Returns:
            np.ndarray: square wave of the note
        """
        return self.render(
            'square',
            duration=duration,
            unit=unit,
            bpm=bpm,
            duty=duty
        )

    def sawtooth(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        width: float = 1.,
    ) -> np.ndarray:
        """
        Generate sawtooth wave of the note. It is the same as
        ``Note.render('sawtooth')``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)
            width (float, optional): width of sawtooth

        Returns:
            np.ndarray: sawtooth wave of the note
        """
        return self.render(
            'sawtooth',
            duration=duration,
            unit=unit,
            bpm=bpm,
            width=width
        )

    def triangle(
        self,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
    ) -> np.ndarray:
        """
        Generate triangle wave of the note. It is the same as
        ``Note.render('triangle')``, ``note.sawtooth(width=0.5)``.

        Args:
            duration (float, optional): duration
            unit (str, optional): unit of duration
            bpm (float, optional): BPM (beats per minute)

        Returns:
            np.ndarray: triangle wave of the note
        """
        return self.render('triangle', duration=duration, unit=unit, bpm=bpm)

    def play(
        self,
        waveform: Optional[Union[str, Callable]] = None,
        duration: Optional[float] = None,
        unit: Optional[str] = None,
        bpm: Optional[float] = None,
        **kwargs
    ) -> ipd.Audio:
        """
        Play note sound in IPython notebook. Return
        IPython.display.Audio object. This wave is generated by
        ``Note.render()``.

        Args:
            waveform (Union[str, Callables], optional): waveform type.
            duration (float, optional): duration.
            unit (str, optional): unit of duration.
            bpm (float, optional):BPM (beats per minute).

        Returns:
            ipd.Audio: IPython.display.Audio object.
        """
        y = self.render(
            waveform,
            duration=duration,
            unit=unit,
            bpm=bpm,
            **kwargs
        )
        return ipd.Audio(y, rate=self.sr)
