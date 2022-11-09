from typing import Optional, Union


def check_note_name(text: str) -> None:
    assert text, "Note name is empty"
    assert len(text) <= 2, "Note name is too long"

    if len(text) == 1:
        text = text.upper()
        assert text in "ABCDEFG", f"One letter note name must be in {list('ABCDEFG')}"

    elif len(text) == 2:
        assert text[0] in "ABCDEFG", f"First letter of note name must be in {list('ABCDEFG')}"
        assert text[1] in "♭♯", f"Second letter of note name must be in {list('+-b♭♯')}"


def shaping_note_name(name: str) -> str:
    name = name.upper()
    name = name.replace('-', '♭')
    name = name.replace('b', '♭')
    name = name.replace('+', '♯')
    return name


NUM_C0 = 12
NUM_A4 = 69
KEY_NAMES = ['C', 'C♯', 'D', 'D♯', 'E', 'F', 'F♯', 'G', 'G♯', 'A', 'A♯', 'B']
def _name2num(name: str, octave: int) -> int:
    idx = KEY_NAMES.index(name[0])
    pitch = idx + ('♯' in name) - ('♭' in name)
    num = NUM_C0 + 12*octave + pitch
    return num

def _num2name(num: int) -> str:
    name = KEY_NAMES[(num - NUM_C0) % 12]
    return name

def _num2octave(num: int) -> int:
    return (num - NUM_C0) // 12

def _num2freq(num: int, FREQ_A4: float) -> float:
    return FREQ_A4 * 2**((num - NUM_A4)/12)


class Note:
    def __init__(
        self,
        name: Optional[str] = None,
        num: Optional[int] = None,
        octave: Optional[int] = None,
        A4: float = 440.,
    ):
        self.name = name
        self.num = num
        self.ocatave = octave
        self.freqency = _num2freq(num, A4) if num else None


def note(query: Union[str, int], octave: Optional[int] = None, A4: float = 440.) -> Note:
    assert isinstance(query, (str, int)), "input must be a string or an integer"

    if isinstance(query, str):
        notename = shaping_note_name(query)
        check_note_name(notename)
        notenum = _name2num(notename, octave) if octave else None
        return Note(
            name=notename,
            num=notenum,
            octave=octave,
            A4=A4,
            )

    else:
        assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
        notename = _num2name(query)
        octave = _num2octave(query)
        return Note(
            name=notename,
            num=query,
            octave=octave,
            A4=A4,
            )