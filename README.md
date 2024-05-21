# munotes

*musical-notes*

[![PyPI version](https://badge.fury.io/py/munotes.svg)](https://badge.fury.io/py/munotes)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/munotes?style=plastic)

<br>

This library is for handling notes and chords in Python.

- [PyPI](https://pypi.org/project/munotes/)
- [API Reference](https://misya11p.github.io/munotes/)

## General Usage

### Note

Note class. Handling note.

This class is used by inputting the note name and octave height, or MIDI note number at initialization.

```python
import munotes as mn

note = mn.Note("A4")
print(note) # A4

note = mn.Note(69)
print(note) # A4
```

- `transpose()`

Transpose the note.

```python
note.transpose(2)
print(note) # B4

```


- `render()`

Get the waveform of the note.

```python
import matplotlib.pyplot as plt
y = note.render('sin')
plt.plot(y[:200])
```

![image](docs/images/sin.jpg)

`squere` and `sawtooth` are also sapported.

```python
y = note.render('squere')
plt.plot(y[:200])
```
![image](docs/images/square.jpg)

```python
y = note.render('sawtooth')
plt.plot(y[:200])
```
![image](docs/images/sawtooth.jpg)

Arbitrary waveforms are also supported.

```python
y = note.render(lambda t: np.sin(t) + np.sin(2*t))
plt.plot(y[:200])
```
![image](docs/images/sin2.jpg)


- `play()`

Get IPython.display.Audio object.

![image](docs/images/play.jpg)


### Notes

Notes class. Handling multiple notes.

This class is used by inputting the notes at initialization.

```python
notes = mn.Notes("C4", "E4", "G4")
print(notes) # C4 E4 G4

```

Methods are the same as `Note`. Ex: `transpose()`, `render()`, `play()`.



### Chord

Chord class. Handling chord.

This class generates a Notes object by inputting a chord name at initialization.

```python
from munotes import Chord
chord = Chord("A#m7")
print(chord) # A#m7
print(chord.names) # ['A#', 'C#', 'F', 'G#']
```

Methods are the same as `Note` (and `Notes`).  
Transpose is also supported by `transpose()`

```python
chord.transpose(3)
print(chord) # C#m7
print(chord.names) # ['C#', 'E', 'G#', 'B']
```


### Track

Track class. Handling multiple Notes as a sequence.

This class is used by inputting the notes with durations at initialization.


```python
track = mn.Track([
    mn.Note("C4", duration=1),
    mn.Note("E4", duration=1),
    mn.Note("G4", duration=1)
])
```

Methods are the same as other classes.  
But in methods that handling waveform (`render()`, `play()`, etc), generate the waveform as sequence of notes (like: C -> E -> G).


### Stream

Stream class. Handling multiple tracks.

This class is used by inputting the tracks at initialization.

```python
track = mn.Track([
    mn.Note("C4", duration=1),
    mn.Note("E4", duration=1),
    mn.Note("G4", duration=1)
])

chords = mn.Track([
    mn.Chord("C", duration=3),
])

stream = mn.Stream([melody, chords])
```

Methods are the same as other classes.

## Version History

### [0.1.0](https://pypi.org/project/munotes/0.1.0/) (2022-11-12, Beta-release)

- Add `Note` class
- Add `Chord` class

### [1.0.0](https://pypi.org/project/munotes/1.0.0/) (2023-02-09)

- Add `Notes` class
- Add `Track` class
- Add `Stream` class
- Add `Rest` class
- Add `sin()`, `square()`, `sawtooth()` methods
- Add `play()` method
- Add `render()` method

### [1.0.1](https://pypi.org/project/munotes/1.0.1/) (2023-02-12)

- Fix a bug that `Rest` could not be put into `Track`.

### [1.1.0](https://pypi.org/project/munotes/1.1.0/) (2023-02-16)

- Waveform parameters can be specified. Ex: `note.sawtooth(width=0.5)`
- Support for inputting octave with note names. Ex: `note = mn.Note("A4")`
- All supported chords can be seen in `mn.chord_names`.
- Arbitrary chords can be added.

### [2.0.0](https://pypi.org/project/munotes/2.0.0/) (2023-11-19)

- Add `Envelope` class
- Modify `sec` argument to `duration`
- Add default parameters for rendering that can be specified in initialization
    - `waveform`
    - `duration`
    - `unit`
    - `bpm`
    - `envelope`
    - `duty`
    - `width`
    - `amp`
- Remove function that change frequency of `A4` directly
- Modify input type of `Track` from `Tuple[Note, float]` to `List[Note]`
    - Note.duration is used to duration when rendering
- Remove `**kwargs` in `render()` method

### [2.0.1](https://pypi.org/project/munotes/2.0.1/) (2024-05-21, Latest)

- Fix a bug that chord names in `Track` ware not updated when transposed.
