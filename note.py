from typing import Optional, Union
import warnings

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
        assert nname[1] in "#b", f"Second letter of note name must be in {list('+♯#-♭b')}"

    if return_nname:
        return nname


def nname_formatting(nname: str) -> str:
    """
    Format note name string.

    Args:
        nname (str): note name

    Returns:
        str: formatted note name
    """
    nname = nname.upper()
    nname = nname.replace('+', '#')
    nname = nname.replace('♯', '#')
    nname = nname.replace('-', 'b')
    nname = nname.replace('♭', 'b')
    return nname


NUM_C0 = 12
NUM_A4 = 69
KEY_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

class Note:
    def __init__(
        self,
        query: Union[str, int],
        octave: Optional[int] = None,
        A4: float = 440.,
    ):
        """
        Note class.

        Args:
            query (Union[str, int]): string of note name or midi note number.
            octave (Optional[int], optional): octave.
            A4 (float, optional): tuning. freqency of A4. Defaults to 440.
        """
        assert isinstance(query, (str, int)), "input must be a string or an integer"

        if isinstance(query, str):
            notename = check_nname(query, return_nname=True)
            notenum = self._name2num(notename, octave) if octave else None
        else:
            if octave:
                warnings.warn("octave is ignored when query is an integer")
            assert 0 <= query <= 127, "MIDI note number must be in 0 ~ 127"
            notenum = query
            notename = self._num2name(query)
            octave = self._num2octave(query)
        freq = self._num2freq(notenum, A4) if notenum else None

        self.name = notename
        self.num = notenum
        self.ocatave = octave
        self.freq = freq
        self.A4 = A4


    def transpose(self, semitone: int) -> None:
        """
        transpose note by semitone.

        Args:
            semitone (int): semitone
        """
        self.num += semitone
        self.name = self._num2name(self.num)
        self.ocatave = self._num2octave(self.num)
        self.freq = self._num2freq(self.num, self.A4)


    def _name2num(self, name: str, octave: int) -> int:
        idx = KEY_NAMES.index(name[0])
        pitch = idx + ('#' in name) - ('b' in name)
        num = NUM_C0 + 12*octave + pitch
        return num

    def _num2name(self, num: int) -> str:
        name = KEY_NAMES[(num - NUM_C0) % 12]
        return name

    def _num2octave(self, num: int) -> int:
        return (num - NUM_C0) // 12

    def _num2freq(self, num: int, FREQ_A4: float) -> float:
        return FREQ_A4 * 2**((num - NUM_A4)/12)


    def __str__(self) -> str:
        return f'{self.name}{self.ocatave}'

    def __repr__(self):
        return f'note.Note {self.name}{self.ocatave}'

    def __int__(self) -> int:
        return self.num
