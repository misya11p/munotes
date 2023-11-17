from typing import Union, Dict
import numpy as np


class Envelope:
    def __init__(
        self,
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.5,
        release: float = 0.1,
        hold: float = 0.,
        sr: int = 22050,
        trans_orders: Union[float, Dict[str, float]] = 1
    ):
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

    def get_window(self, sec:float) -> np.ndarray:
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
