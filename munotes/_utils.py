import re
from typing import Optional, Tuple
from .chord_names import chord_names


NUM_C0 = 12 # MIDI note number of C0
NUM_A4 = 69 # MIDI note number of A4
KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SUPPORTED_WAVEFORMS = ["sin", "square", "sawtooth", "triangle"]
SUPPORTED_UNITS = ["s", "ms", "ql"]

NOTE_NAME_PATTERN = "[A-G][#b]?"
NOTE_PATTERN = f"{NOTE_NAME_PATTERN}\d*"
VALID_NOTE_PATTERN = r"[A-Ga-g][#♯+b♭-]?\d*"
LIM_REPR_NOTES = 6


def note_name_formatting(
    note_name: str,
    octave: Optional[int]
) -> Tuple[str, int]:
    """
    Format note name string and return it with octave.
    'octave' argument is ignored if it is specified in the note_name_string.

    Args:
        note_name (str): string of note name
        octave (Optional[int]): octave

    Returns:
        Tuple[str, int]: formatted note name and octave
    """
    form_note_name = string_formatting(note_name)
    assert re.match(NOTE_PATTERN, form_note_name), \
        f"'{note_name}' is invalid. Valid string: {VALID_NOTE_PATTERN}"
    border = 2 if ('#' in form_note_name or 'b' in form_note_name) else 1
    pitch_name = form_note_name[:border]
    octave_str = form_note_name[border:]
    if not octave_str:
        assert octave, "Octave is not specified."
        assert isinstance(octave, int), \
            "Octave must be an integer. Input octave: {octave}"
    else:
        octave = int(octave_str)
    return pitch_name, octave


def chord_name_formatting(
    chord_name: str,
    type: Optional[str]
) -> Tuple[str, str]:
    """
    Format chord name string and return it with chord type.

    Args:
        chord_name (str):
            string of chord name. Chord type in the string is ignored
            if 'type' argument is specified.
        type (Optional[str]):
            chord type. Ex. '', 'm7', '7', 'sus4'.

    Returns:
        Tuple[str, str]: formatted chord name and chord type
    """
    form_chord_name = string_formatting(chord_name)
    note_search = re.match(NOTE_NAME_PATTERN, form_chord_name)
    assert note_search, f"'{chord_name}' is an invalid string"
    border = note_search.end()
    root_name = form_chord_name[:border]
    type = type if type != None else form_chord_name[border:]
    assert isinstance(type, str) and type in chord_names, \
        f"'{type}' is an invalid chord type"
    return root_name, type


def string_formatting(name_string: str) -> str:
    """
    Format note name or chord name string.

    Args:
        name (str): note name or chord name string

    Returns:
        str: formatted note name or chord name string
    """
    name_string = name_string[0].upper() + name_string[1:]
    name_string = name_string.replace('+', '#')
    name_string = name_string.replace('♯', '#')
    name_string = name_string.replace('-', 'b')
    name_string = name_string.replace('♭', 'b')
    return name_string


def get_repr_notes(obj, name: str = "", sep=", ") -> str:
    """
    Get string representation that can be used in __repr__ method.

    Args:
        obj: Object that has '_notes' attribute
        name (str, optional): Object name.
        sep (str, optional): Separator. Defaults to ", ".

    Returns:
        str: String representation of notes.
    """
    repr_obj = name + " (notes: "
    notes = [repr(note) for note in obj._notes]
    n = len(notes)
    if n > LIM_REPR_NOTES:
        repr_obj += sep.join(notes[:LIM_REPR_NOTES])
        repr_obj += " ... "
    else:
        repr_obj += sep.join(notes)
    repr_obj += ")"
    return repr_obj
