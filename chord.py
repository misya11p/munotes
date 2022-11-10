import re
from note import nname_formatting


INTERVALS = {
    "": (0,4,7),
    "m": (0,3,7),
    "7": (0,4,7,10),
    "m7": (0,3,7,10),
    "M7": (0,4,7,11),
    "mM7": (0,3,7,11),
    "sus4": (0,5,7),
    "dim": (0,3,6),
    "dim7": (0,3,6,9),
    "aug": (0,4,8),
    "6": (0,4,7,9),
    "m6": (0,3,7,9),
    "sus2": (0,2,7)
}

chord_names = list(INTERVALS.keys())


PITCH_PATTERN = '[A-G][#, b]*'

class Chord(str):
    def __init__(
        self,
        cname: str,
    ):
        pitch_search = re.match(PITCH_PATTERN, cname)
        assert pitch_search, f"'{cname}' is an invalid string"
    
        # first = pitch_search.start()
        border = pitch_search.end()
        root, type = cname[:border], cname[border:]
    
        root = nname_formatting(root)
        name = root + type
        interval = INTERVALS[type]

        self.name = name
        self.root = root
        # self.notes = []
        self.interval = interval
        self.bass = None
        self.type = type