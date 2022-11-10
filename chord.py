from note import Note, KEY_NAMES
import re


chords = {
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

chord_names = list(chords.keys())


PITCH_PATTERN = '[A-G][#, b]*'

class Chord:
    def __init__(
        self,
        cname: str,
    ):
        pitch_search = re.match(PITCH_PATTERN, cname)
        assert pitch_search, f"'{cname}' is an invalid string"

        # first = pitch_search.start()
        border = pitch_search.end()
        root_name, type = cname[:border], cname[border:]
        root = Note(root_name)
        name = root.name + type
        interval = chords[type]

        self.name = name
        self.root = root
        self.interval = interval
        self.bass = None
        self.type = type
        self._compose()


    def transpose(self, semitones: int):
        self.root.transpose(semitones)
        self._compose()


    def _compose(self):
        self.root_idx = self.root.idx
        self.idx = [(self.root_idx + i) % 12 for i in self.interval]
        self.note_names = [KEY_NAMES[i] for i in self.idx]
        self.notes = [Note(name) for name in self.note_names]


    def __repr__(self):
        return f'chord.Chord {self.name}'

    def __str__(self):
        return self.name