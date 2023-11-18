from typing import Union, Dict
import numpy as np


class Envelope:
    def __init__(
        self,
        attack: float = 0.,
        decay: float = 0.,
        sustain: float = 1.,
        release: float = 0.,
        hold: float = 0.,
        sr: int = 22050,
        trans_orders: Union[float, Dict[str, float]] = 1
    ):
        """
        Envelope for waveform. Get window of the envelope to apply to
        the waveform.

        Args:
            attack (float, optional):
                Attack time in seconds. Defaults to 0..
            decay (float, optional):
                Decay time in seconds. Defaults to 0..
            sustain (float, optional):
                Sustain level. Defaults to 1..
            release (float, optional):
                Release time in seconds. Defaults to 0..
            hold (float, optional):
                Hold time in seconds. Defaults to 0..
            sr (int, optional):
                Sampling rate. Defaults to 22050.
            trans_orders (Union[float, Dict[str, float]], optional):
                Transition orders of each envelope. If 1, the envelope
                is linear, if 2, the envelope is quadratic, and so on.
                Defaults to 1.
        """
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
        self.hold = hold
        self.sr = sr
        trans_orders = trans_orders or 1
        if isinstance(trans_orders, (int, float)):
            trans_orders = {
                "attack": trans_orders,
                "decay": trans_orders,
                "release": trans_orders
            }
        self.trans_orders = {
            "attack": trans_orders.get("attack", 1),
            "decay": trans_orders.get("decay", 1),
            "release": trans_orders.get("release", 1),
        }

    def get_window(self, sec: float) -> np.ndarray:
        """
        Get window of the envelope to apply to the waveform. The window
        is a numpy array of the same length as the waveform. It is
        used to multiply the waveform.

        If you specify the envelope to the Note class, the envelope is
        applied to the note's waveform.

        Args:
            sec (float): Length of the waveform in seconds.

        Returns:
            np.ndarray: Window of the envelope.

        Examples:
            >>> envelope = mn.Envelope(
            >>>     attack=0.1,
            >>>     decay=0.1,
            >>>     sustain=0.5,
            >>>     release=0.1,
            >>> )
            >>> note = mn.Note("C4", envelope=envelope)
            >>> note.play()
        """
        n = int(sec * self.sr)
        y = np.ones(n)

        # times
        at = min(int(self.sr * self.attack), n)
        ht = min(int(self.sr * self.hold), n - at)
        dt = min(int(self.sr * self.decay), n - at - ht)
        rt = int(self.sr * self.release)

        # orders
        ao = self.trans_orders["attack"]
        do = self.trans_orders["decay"]
        ro = self.trans_orders["release"]

        # windows
        aw = np.linspace(0, 1, at) ** ao
        dw = (np.linspace(1, 0, dt) ** do) * (1 - self.sustain) + self.sustain
        sw = self.sustain
        rw = (np.linspace(1, 0, rt) ** ro) * sw

        y[:at] *= aw
        y[at + ht:at + ht + dt] *= dw
        y[at + ht + dt:] *= sw
        y = np.append(y, rw)
        return y
