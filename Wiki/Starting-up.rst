Starting up!
============

Table of contents
-----------------

1) `Create a new document`_

2) `Update an already existing document`_

3) `Render your masterpiece`_

Introduction
------------

You've just got the new idea that will help technology reach singularity_.
It's necessarily too important to not writing all this down, for posterity.

.. _singularity: http://en.wikipedia.org/wiki/Technological_singularity

In this tutorial, we will consider that the SCM_ you use is git_.
Nevertheless, if your preference goes to another SCM, like subversion_ or
mercurial_, switching from git commands to your favorite one should be quite
easy.

.. _SCM: http://en.wikipedia.org/wiki/Software_configuration_management
.. _git: http://www.git-scm.com
.. _subversion: http://subversion.tigris.org/
.. _mercurial: http://mercurial.selenic.com/

Create a new document
---------------------

Open a new file named *killer_app.rst*, and start typing your requirements
documentation like you would in reStructuredText_::

  Great killer app
  ================

  This document defines my new killer app.

  PRK-REQ
  My killer app shall be great enough to rule the world.
  -- PRK-REQ

  I just need to find a new idea.

.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html

Each requirement shall be isolated between ``PRK-REQ`` and ``-- PRK-REQ``
marks; all the remainging lines are considered to be normal text. At this time
being, you only have a single requirement, but hey! what a great start!

Seems like it is time to immortalize this technological breakthrough, doesn't
it? For that, you need to convert the document you've just edited into a format
more suitable to track down evolution of requirements.

In your favorite shell, type::

  $> prk split killer_app.rst > killer_app.prk

then check that PeRKy actually split your initial document into two::

  $> ls *.prk
  killer_app.prk  REQ-6174.prk

PeRKy uses the *.prk* suffix to identify the different part of your original
document. *killer_app.prk* contains the regular text, and *REQ-6174.prk*
contains your first requirement. Associating an identifier to each requirement
is mandatory, not only for PeRKy, but also for every developper to know what
they're talking about. If you don't provide any identifier to your requirement
(like we just did), PeRKY determines one for you.

Check the content of your sole requirement file::

  $> cat REQ-6174.prk
  My killer app shall be great enough to rule the world.

Now, add the PeRKy files to your repository, then commit::

  $> git add *.prk
  $> git commit -m "The beginning of a new era"

**IMPORTANT NOTE:** To be truely efficient, never store your edited file, but
only the PeRKy ones (which end with *.prk*). The goal of PeRKy is to use the
regular SCM commands to understand how your requirements evolve, by isolating each
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
you remove your initial requirement while editing.

As a survival guide, just ignore lines that start with ``PRK-...`` at the end
of the document. Don't edit them neither.

Now, edit *killer_app.rst* to update your first requirement, and add a new
one::

  ...
  PRK-REQ REQ-6174
  KillerApp shall be great enough to rule the universe.
  -- PRK-REQ

  PRK-REQ
  KillerApp shall be able to determine one's age at any time, provided that
  date of birth had been given.
  -- PRK-REQ
  PRK-MEM REQ-6174

Satisfying, isn't it? Store it!

::

  $> prk split killer_app.rst > killer_app.prk
  $> git status
  # On branch master
  # Changes not staged for commit:
  #   (use "git add <file>..." to update what will be committed)
  #   (use "git checkout -- <file>..." to discard changes in working directory)
  #
  #       modified:   REQ-6174.prk
  #       modified:   killer_app.prk
  #
  # Untracked files:
  #   (use "git add <file>..." to include in what will be committed)
  #
  #       REQ-4086.prk
  #       killer_app.rst
  $> git add *.prk
  $> git commit -m "I got the idea"

Now, you can ask ``git`` to tell you about updates in your requirement
document, with ``git log -p`` or ``git diff --name-only``.

Render your masterpiece
-----------------------

Nowadays, economy is mainly oriented towards shortening time to market. You
**must** share your ideas to start the technological revolution you're
proposing.

For that, clearly non of the form of your documentation is suitable. That is
why PeRKy offers you a third command, to produce a final version of the
document. It is similar to rendering an image, or processing a TeX entry.

In your terminal, type::

  $> prk yield killer_app.prk > output.rst

You should obtain someting like this::

  $> cat output.rst
  Great killer app
  ================

  This document defines my new killer app.

  **[REQ-6174]**

  My killer app shall be great enough to rule the world.

  **-- End of requirement**

  **[REQ-4086]**

  KillerApp shall be able to determine one's age at any time, provided that
  date of birth had been given.

  **-- End of requirement**

Fancy, isn't it? You can convert it to various formats thanks to docutils_ or
pandoc_. For example::

  $> rst2html output.rst > output.html

produces an html document from your final version of the document.

::

  $> pandoc output.rst -o output.odt

procudes an OpenOffice document from your final version of the document.

::

  $> pandoc output.rst -o output.tex
  $> pdflatex output.tex

converts your document into a LaTeX script, then render it in pdf format. The
result is called *output.pdf*.

.. _docutils: http://docutils.sourceforge.net/
.. _pandoc: http://johnmacfarlane.net/pandoc/
