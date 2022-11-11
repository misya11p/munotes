# munotes

musical-notes

This library is for handling notes and chords in Python.

## Note

Note class. Handling note.

`Note` class is used by entering the note name and octave height at initialization.

```python
from munotes import Note
note = Note("A", octave=4)
print(note) # A4
```

`Note` class defines these attributes.

```python
print(note.name)   # A
print(note.idx)    # 9
print(note.octave) # 4
print(note.num)    # 69
print(note.freq)   # 440.0
```

- `Note.name: str`  Note name
- `Note.idx: int`  Index of note name with C as 0
- `Note.octave: int`  Octave
- `Note.num: int`  MIDI Note Number
- `Note.freq: float` Freqency

It is possible not to define octaves at initialization, in which case all attributes except for `name` and `idx` will be `None`.



This class can be transposed with `Note.transpose()`.

```python
note.transpose(5)
print(note)        # D5
print(note.name)   # D
print(note.idx)    # 2
print(note.octave) # 5
print(note.num)    # 74
print(note.freq)   # 587.3295358348151
```



If an integer between 0 and 127 is entered at initialization, it is used as the midi note number, and other attributes are initialized based on it.

```python
note = Note(40)
print(note) # E2
```



## Chord

Chord class. Handling chord.

This class is used by entering the chord name at initialization.

```python
from munotes import Chord
chord = Chord("A#m7")
print(chord) # A#m7
```

`Chord` class defines these attributes.

```python
print(chord.name)       # A#m7
print(chord.root)       # A#
print(chord.type)       # m7
print(chord.interval)   # (0, 3, 7, 10)
print(chord.notes)      # [Note A#, Note C#, Note F, Note G#]
print(chord.note_names) # ['A#', 'C#', 'F', 'G#']
print(chord.idx)        # [10, 1, 5, 8]
```

- `Chord.name: str`  Chord name
- `Chord.root: munotes.Note`  Root of a chord
- `Chord.type: str`  Chord Type
- `Chord.interval: Tuple[int]`  Height of the sound when the root as 0.
- `Chord.notes: List[munotes.Note]`  List of notes that make up the chord.
- `Chord.note_names: List[str]`  List of `munotes.Note.name`
- `Chord.idx: List[int]`   List of `munotes.Note.idx`



Like Note, This class can be transposed with `Chord.transpose()`.

```python
chord.transpose(3)
print(chord)            # C#m7
print(chord.note_names) # ['C#', 'E', 'G#', 'B']
```

