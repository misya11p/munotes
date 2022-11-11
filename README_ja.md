# munotes

musical-notes

Pythonで音符やコードを扱うためのライブラリ。

## Note

Noteクラス。音符を扱う。

初期化時に音名とオクターブの高さを入力して使用する。

```python
from munotes import Note
note = Note("A", octave=4)
print(note) # A4
```

`Note`クラスには以下の属性が定義されている。

```python
print(note.name)   # A
print(note.idx)    # 9
print(note.octave) # 4
print(note.num)    # 69
print(note.freq)   # 440.0
```

- `Note.name: str`  音名
- `Note.idx: int`  Cを0とした時の音名のインデックス
- `Note.octave: int`  オクターブ
- `Note.num: int` : midiノートナンバー
- `Note.freq: float`  周波数

初期化時にオクターブを指定しないことも可能だが、その場合は`name`と`idx`以外の属性は`None`になる。



`Note.transpose()`で移調ができる

```python
note.transpose(5)
print(note)        # D5
print(note.name)   # D
print(note.idx)    # 2
print(note.octave) # 5
print(note.num)    # 74
print(note.freq)   # 587.3295358348151
```



初期化時に0 ~ 127の整数を入れるとそれをmidiノートナンバーし、それを元にその他の属性が初期化される。

```python
note = Note(40)
print(note) # E2
```



## Chord

Chordクラス。コードを扱う。

初期化時にコード名を入力して使用する。

```python
from munotes import Chord
chord = Chord("A#m7")
print(chord) # A#m7
```

`Chord`クラスには以下の属性が定義されている。

```python
print(chord.name)       # A#m7
print(chord.root)       # A#
print(chord.type)       # m7
print(chord.interval)   # (0, 3, 7, 10)
print(chord.notes)      # [Note A#, Note C#, Note F, Note G#]
print(chord.note_names) # ['A#', 'C#', 'F', 'G#']
print(chord.idx)        # [10, 1, 5, 8]
```

- `Chord.name: str`  コード名
- `Chord.root: munotes.Note`  根音
- `Chord.type: str`  コードの種類
- `Chord.interval: Tuple[int]`  根音を0とした時の音の高さ
- `Chord.notes: List[munotes.Note]`  コードを構成している音のリスト
- `Chord.note_names: List[str]`  コードを構成している音名のリスト
- `Chord.idx: List[int]`   コードを構成している音のインデックス(`munotes.Note.idx`)のリスト



`Note`同様、`Chord.transpose()`で移調ができる

```python
chord.transpose(3)
print(chord)            # C#m7
print(chord.note_names) # ['C#', 'E', 'G#', 'B']
```

