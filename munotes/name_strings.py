from typing import Optional

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
    nname = nname[0].upper() + nname[1:]
    nname = nname.replace('+', '#')
    nname = nname.replace('♯', '#')
    nname = nname.replace('-', 'b')
    nname = nname.replace('♭', 'b')
    return nname