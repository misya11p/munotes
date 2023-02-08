.. munotes documentation master file, created by
   sphinx-quickstart on Wed Feb  8 19:47:20 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

munotes
===================================

*musical-notes*

A library for handling notes and chords and their sounds in Python.
An object can be created by inputting the name of a note or chord.
From the object, various waveforms can be generated and sounds can be played back on the notebook.
They can also be managed as a sequence of objects.

Supported classes:

- `notes <#module-munotes.notes>`_
   - `mn.Note <#munotes.notes.Note>`_
   - `mn.Rest <#munotes.notes.Rest>`_
   - `mn.Notes <#munotes.notes.Notes>`_
   - `mn.Chord <#munotes.notes.Chord>`_
- `sequence <#module-munotes.sequence>`_
   - `mn.Track <#munotes.sequence.Track>`_
   - `mn.Stream <#munotes.sequence.Stream>`_

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   munotes


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
