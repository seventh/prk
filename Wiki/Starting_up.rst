Starting up!
============

Create a new document
---------------------

Open a new file named (for example) ``killer_app.rst`` and start typing your
requirements documentation like you would in reStructuredText::

  Great killer app
  ================

  This document defines my new killer app.

  PRK-REQ
  My killer app shall be great enough to rule the world.
  -- PRK-REQ

  I just need to find a new idea.

Each requirement shall be isolated between ``PRK-REQ`` and ``-- PRK-REQ``
marks. A document can hold as many requirements as you need.

Wah! What a great start. Seems like it is time to share such a structuring
information! For that, you need to convert the document you've just edited
into a format more suitable to track down evolution of requirements.

In your favorite shell, just type::

  $> prk split killer_app.rst > killer_app.prk

You can check that PeRKy actually split your initial document into two::

  $> ls
  killer_app.prk
  killer_app.rst
  REQ-6174.prk

The file ``REQ-6174.prk`` contains the text of your first requirement. PeRKy
associates an identifier with each requirement, if you don't provide one. You
can check the content of the file::

  $> cat REQ-6174.prk
  My killer app shall be great enough to rule the world.

Now, add the files suffixed ``.prk`` to your repository. We will here suppose
that you use ``git``, but you can use subversion, dracs, or whatever::

  $> git add *.prk
  $> git commit -m "The beginning of a new era"

**WARNING:** Make sure you don't store the file you were editing (in our
example, ``killer_app.rst``). The goal of PeRKy is to use the regular SCM
commands to understand how your requirements evolve, by isolating each
requirement into a different file.

Update an already existing document
-----------------------------------

Next time you'll want to update your requirement document, first compose back
an editable version::

  $> prk merge killer_app.prk > killer_app.rst
  $> cat killer_app.rst
  Great killer app
  ================

  This document defines my new killer app.

  PRK-REQ REQ-6174
  My killer app shall be great enough to rule the world.
  -- PRK-REQ

  I just need to find a new idea.
  PRK-MEM REQ-6174

The last line, which start with ``PRK-MEM``, should not be edited by hand and
is here to remember that the requirement identifier ``REQ-6174`` is already
in use, and cannot be attributed to another requirement you could add, even if
you remove your initial requirement.

Just ignore lines that start with ``PRK-...`` at the end of the document as a
survival guide for now.

Now, edit first requirement, and add a new one (in ``killer_app.rst``, of
course)::

  ...
  PRK-REQ REQ-6174
  KillerApp shall be great enough to rule the universe.
  -- PRK-REQ

  PRK-REQ
  KillerApp shall be able to determine your age at any time, provided you gave
  your date of birth.
  -- PRK-REQ
  PRK-MEM REQ-6174

Satisfying, isn't it? Store it!

::

  $> prk split killer_app.rst > killer_app.prk
  $> git status
  # On branch master
  # Changes not staged for commit:
  #
  #       modified:   REQ-6174.prk
  #       modified:   killer_app.prk
  #
  # Untracked files:
  #
  #       REQ-9482.prk
  #       killer_app.rst
  $> git add *.prk
  $> git commit -m "I got the idea"

Now, you can ask ``git`` to tell you about updates in your requirement
document, via ``git log -p`` for example.
