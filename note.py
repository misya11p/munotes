from typing import Optional, Union


def check_nname(nname: str, return_nname: bool = False) -> Optional[str]:
    """
    Check if the note name string is valid.
        if valid: return None or formatted note name
        if invalid: return error

    Args:
        nname (str): note name
        return_nname (bool, optional): Whether to return formatted note name.

    Returns:
        Optional[str]: formatted note name
    """
    assert nname, "Note name is empty"
    assert len(nname) <= 2, "Note name is too long"
    nname = nname_formatting(nname)

    if len(nname) == 1:
        assert nname in "ABCDEFG", f"One letter note name must be in {list('ABCDEFG')}"

    elif len(nname) == 2:
        assert nname[0] in "ABCDEFG", f"First letter of note name must be in {list('ABCDEFG')}"
        assert nname[1] in "♭♯", f"Second letter of note name must be in {list('+-b♭♯')}"

    if return_nname:
        return nname


def nname_formatting(nname: str) -> str:
    nname = nname.upper()
    nname = nname.replace('-', '♭')
    nname = nname.replace('b', '♭')
    nname = nname.replace('+', '♯')
    return nname


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
        query: Union[str, int],
        octave: Optional[int] = None,
        A4: float = 440.,
    ):
        assert isinstance(query, (str, int)), "input must be a string or an integer"

        if isinstance(query, str):
            notename = shaping_note_name(query)
            check_note_name(notename)
            notenum = _name2num(notename, octave) if octave else None
        else:
            assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
            notename = _num2name(query)
            octave = _num2octave(query)

        self.name = notename
        self.num = notenum
        self.ocatave = octave
        self.freq = _num2freq(notenum, A4) if notenum else None
        self.A4 = A4
