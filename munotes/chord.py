from .note import Note, KEY_NAMES, nname_formatting
import re


chord_intervals = {
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

chords = list(chord_intervals.keys())


PITCH_PATTERN = '[A-G][#, b]*'

class Chord:
    def __init__(self, cname: str):
        """
        Chord class.

        Args:
            cname (str): chord name string
        """
        cname = nname_formatting(cname)
        pitch_search = re.match(PITCH_PATTERN, cname)
        assert pitch_search, f"'{cname}' is an invalid string"

        border = pitch_search.end()
        root_name, type = cname[:border], cname[border:]
        root = Note(root_name)
        name = root.name + type
        interval = chord_intervals[type]

        self.name = name
        self.root = root
        self.interval = interval
        self.bass = None
        self.type = type
        self._compose()


    def transpose(self, n_semitones: int):
        """
        transpose chord

        Args:
            n_semitones (int): number of semitones to transpose
        """
        self.root.transpose(n_semitones)
        self._compose()


    def _compose(self):
        """Define other attributes based on note name"""
        self.name = self.root.name + self.type
        self.idx = [(self.root.idx + i) % 12 for i in self.interval]
        self.note_names = [KEY_NAMES[i] for i in self.idx]
        self.notes = [Note(name) for name in self.note_names]


    def __repr__(self):
        return f'Chord {self.name}'

    def __str__(self):
        return self.name