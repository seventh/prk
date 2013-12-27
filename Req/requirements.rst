Introduction
============

PeRKy_ is a computer software dedicated to management of software requirements
with any `Source Control Manager`_ (abbreviated *SCM*) as storage layer, based
on a simple principle: **1 file per requirement**.

.. _PeRKy: http://www.github.com/seventh/prk
.. _`Source Control Manager`: http://en.wikipedia.org/wiki/Source_Control_Management

PeRKy helps users to keep documentation in sync with their developments by
using the same tools than the one they use for code. It also integrates
notions of distributed development and thus highly limitates the risk of
encountering conflicts when merging branches of development.

PeRKy relies on common SCM principles and commands for users to follow the
evolution of their software requirements, like *log*, *diff* or *tag*.

Dependencies
------------

PRK-REQ
PeRKy is written in `Python 3.x`_.

.. _`Python 3.x`: http://www.python.org
-- PRK-REQ

PRK-REQ
PeRKy is aimed at producing document structured with reStructuredText_ markup
language.

.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
-- PRK-REQ

*Note:* This is really important only for output format. Management of
document does not rely on any reST intrisics until production.

Licence
-------

PRK-REQ
PeRKy is distributed with CeCILL_ 2.1 licence.
-- PRK-REQ

.. _CeCILL: http://www.cecill.info

References
----------

Various tools can be used to convert reST_ formatted documents into more
common format, including:

- docutils_ themselves, which authorizes conversion to html, latex, man or odt
  formats for example.

- pandoc_, which provide the same kind of conversion, even if using different
  templates, and offer conversion to other markup languages (markdown,
  mediawiki) or usual document formats like doc or rtf.

.. _reST: reStructuredText_
.. _docutils: reStructuredText_
.. _pandoc: http://johnmacfarlane.net/pandoc/

rmtoo_ is a tool similar to PeRKy, although oriented towards internal
traceability and agile developments.

.. _rmtoo: http://www.flonatel.de/projekte/rmtoo/

Requirements
============

A document managed with PeRKy can be in three different states:

- EDITION state: in this format, the document is composed of a single and
  complete file, with specific PeRKy markup to isolate begin and end of
  requirements for example.

- STORAGE state: in this format, the document is composed of a main file and
  multiple requirement files. The main file uses PeRKy marks to tag inclusion
  points for requirement files. Each requirement file stores a single file,
  which name is the identifier of the requirement.

- PUBLICATION state: this format is very similar to EDITION one, but all PeRKy
  tags have been removed and some presentation treatments have been made, like
  generation of cross-references matrix between requirements and reference
  documents.

PRK-REQ
.. figure:: automaton.png
   :width: 15cm
   :align: center

Finite state automaton describing allowed transformations between states.
-- PRK-REQ

Structure of a document
-----------------------

.. _delimiter:
.. _delimiters:

Without any loss of genericity, a document is defined as a list of lines, even
empty ones. A line can either be a PeRKy **delimiter**, or plain text, i.e.
content that will not be altered by the various PeRKy transformations.

PRK-REQ
PeRKy delimiters_ are not part of the final document.
-- PRK-REQ

PRK-REQ
All lines but PeRKy delimiters_ shall be conserved as is in the final document.
-- PRK-REQ

.. _iff:
.. _tag:
.. _tags:

In order to avoid any ambiguity about PeRKy delimiters_, a line is considered
a PeRKy delimiter_ **if and only if** (abbreviated *iff*) it begins with one of
the **tags** reserved by PeRKy.

PRK-REQ
PeRKy delimiters shall start with a PeRKy tag_.
-- PRK-REQ

Requirement block
-----------------

PRK-REQ
In a document, software requirements are expressed within requirement blocks.
-- PRK-REQ

.. _BRB:

Begin of Requirement Block delimiter
''''''''''''''''''''''''''''''''''''

PRK-REQ
A **BRB** delimiter_ marks the Beginning of a new Requirement Block.
-- PRK-REQ

PRK-REQ
The tag_ associated with BRB_ delimiter is "``PRK-REQ``".
-- PRK-REQ

PRK-REQ
An optional requirement identifier can be added right after the BRB_ tag.
-- PRK-REQ

.. _`requirement identifier`:
.. _`requirement identifiers`:

PRK-REQ
A **requirement identifier** is composed of one or more characters taken in the
following character set : [0-9A-Za-z-].
-- PRK-REQ

*Note:* This definition is very likely to change in order to suppress its
limitation.

.. _ERB:

End of Requirement Block delimiter
''''''''''''''''''''''''''''''''''

PRK-REQ
An **ERB** delimiter_ marks the End of a Requirement Block.
-- PRK-REQ

Even if not mandatory, usage of ERB delimiter_ is highly recommended to
tightly control the content of a requirement.

PRK-REQ
The tag_ associated with ERB_ delimiter is "``-- PRK-REQ``".
-- PRK-REQ

.. _TRB:

Traceability inside a requirement block
'''''''''''''''''''''''''''''''''''''''

PRK-REQ
A **TRB** delimiter_ allows expression of requirement traceability within a
requirement block.
-- PRK-REQ

PRK-REQ
The tag_ associated with TRB_ delimiter is "``PRK-REF``".
-- PRK-REQ

*Note:* The fact that BRB_ and TRB_ tags only differ of a single character is
an issue, considering that each occurence of a BRB_ delimiter starts a new
requirement block. It is then easy to mispell a BRB_ tag and replace it
accidentaly with a TRB_ tag, and mess the document. So, the value of the TRB_
tag may change in a near future.

PRK-REQ
A mandatory `requirement identifier`_ shall be added right after the TRB_ tag.
-- PRK-REQ

Traceability tables
'''''''''''''''''''

In order to verify dependencies between documents, traceability tables, or
matrices, are often used. A traceability table is in fact a dictionary which
associates requirement identifiers of a document with the ones of another
document. So, the set of requirement identifiers of the edited document can
either compose the key set or the value set of a traceability table, depending
on it is a **direct** traceability table or a **reversed** one.

.. _DTM:

Direct Traceability Matrix
``````````````````````````

PRK-REQ
A **DTM** delimiter_ marks the location of the Direct Traceability Matrix in
the final document.
-- PRK-REQ

PRK-REQ
The tag_ associated with DTM_ delimiter is "``PRK-MTX``".
-- PRK-REQ

.. _RTM:

Reversed Traceability Matrix
````````````````````````````

PRK-REQ
A **RTM** delimiter_ marks the location of the Reversed Traceability Matrix in
the final document.
-- PRK-REQ

PRK-REQ
The tag_ associated with RTM_ delimiter is "``PRK-XTM``".
-- PRK-REQ

Internal delimiters
-------------------

Additional delimiters may be added into the document by PeRKY itself, for
internal use. For example, in order to avoid the accidental reuse of an
already reserved requirement identifier, while the associated requirement has
disappeared a long time ago.

.. _RRI:

Reserved requirement identifiers
''''''''''''''''''''''''''''''''

PRK-REQ
A **RRI** delimiter_ keeps memory of a Reserved `requirement identifier`_.
-- PRK-REQ

PRK-REQ
The tag_ associated with RRI_ delimiter is "``PRK-MEM``".
-- PRK-REQ

PRK-REQ
A mandatory `requirement identifier`_ shall be added right after the RRI_ tag.
-- PRK-REQ

.. _LNK:

Traceability link
'''''''''''''''''

PRK-REQ
A **LNK** delimiter_ keeps memory of a traceability link outside of a
requirement block.
-- PRK-REQ

PRK-REQ
The tag_ associated with LNK_ delimiter is "``PRK-LNK``".
-- PRK-REQ

PRK-REQ
Two mandatory `requirement identifiers`_ shall be added right after the LNK_
tag.
-- PRK-REQ

.. _IPR:

Inclusion point of a requirement
''''''''''''''''''''''''''''''''

PRK-REQ
An **IPR** delimiter_ marks the exact place of the referenced requirement in
the final document.
-- PRK-REQ

PRK-REQ
The tag_ associated with IPR_ delimiter is "``PRK-INC``".
-- PRK-REQ

PRK-REQ
A mandatory `requirement identifier` shall be added right after the IPR_ tag.
-- PRK-REQ

Document transformations
------------------------

PRK-REQ
A transformation is successful iff_ all of its input files can be read and all
of its output files can be written.
-- PRK-REQ

Split transformation
''''''''''''''''''''

When ``split`` command is run, the following treatments do occur:

PRK-REQ
An identifier is reserved and assigned to each requirement block that is not
already associated with one.
-- PRK-REQ

PRK-REQ
A file is created for each requirement block, using the requirement identifier
as the name of the file. All lines that are not PeRKy delimiters are dumped
into it.
-- PRK-REQ

PRK-REQ
Requirement blocks are replaced by a corresponding IPR_ delimiter.
-- PRK-REQ

PRK-REQ
TRB_ delimiters which are actually inside a requirement block are replaced by
LNK_ ones at the end of the document. The other ones are filtered out and
provoke a *WARNING*.
-- PRK-REQ

PRK-REQ
RRI_ delimiters which reference the same tag than any IPR_ or TRB_ one are
removed from the output.
-- PRK-REQ

Merge transformation
''''''''''''''''''''

PRK-REQ
``merge`` command may optionally remove each included file from storage.
-- PRK-REQ

Summary
'''''''

In the following table, a *Yes* entry corresponds to a mandatory input
transformation, a *No* entry to a forbidden one. In all other cases, behaviour
depends on implementation.

+----------------------------------------------------+-------+-------+-------+
| Transformation                                     | merge | split | yield |
+====================================================+=======+=======+=======+
| Assign identifier to BRB/ERB block                 |       |  Yes  |No [#]_|
+----------------------------------------------------+-------+-------+-------+
| Replace BRB/ERB block with formated requirement    |  No   |  No   |       |
+----------------------------------------------------+-------+-------+-------+
| Replace BRB/ERB block with IPR delimiter           |  No   |  Yes  |  No   |
+----------------------------------------------------+-------+-------+-------+
| Replace DTM delimiter with traceability matrix     |  No   |  No   |  Yes  |
+----------------------------------------------------+-------+-------+-------+
| Add RRI delimiter for each IPR delimiter           |  Yes  |  No   |  No   |
+----------------------------------------------------+-------+-------+-------+
| Replace IPR delimiter with BRB/ERB block           |  Yes  |  No   |  No   |
+----------------------------------------------------+-------+-------+-------+
| Replace IPR delimiter with formated requirement    |  No   |  No   |  Yes  |
+----------------------------------------------------+-------+-------+-------+
| Remove LNK delimiter from output                   |  No   |  No   |  Yes  |
+----------------------------------------------------+-------+-------+-------+
| Replace LNK delimiter with TRB one                 |  Yes  |  No   |  No   |
+----------------------------------------------------+-------+-------+-------+
| Remove BRB/ERB identifier from RRI delimiters set  |  No   |  Yes  |  No   |
+----------------------------------------------------+-------+-------+-------+
| Remove RRI delimiter from output                   |  No   |  No   |  Yes  |
+----------------------------------------------------+-------+-------+-------+
| Replace RTM delimiter with traceability matrix     |  No   |  No   |  Yes  |
+----------------------------------------------------+-------+-------+-------+
| Remove TRB delimiter from output                   |  No   |  No   |  Yes  |
+----------------------------------------------------+-------+-------+-------+
| Replace TRB delimiter with LNK one                 |  No   |  Yes  |  No   |
+----------------------------------------------------+-------+-------+-------+

.. [#] Otherwise requirement identifiers are very likely to be lost

Configuration
-------------

PRK-REQ
PeRKy shall accept a ``QUIET`` option to limitate the output on standard error
channel to error messages
-- PRK-REQ

PRK-REQ
PeRKy shall accept a ``VERBOSE`` option to enlarge the scope of messages
produced on standard error channel to informational ones.
-- PRK-REQ

PRK-REQ
PeRKy shall accept a ``SPARSE`` option for ``yield`` command to produce direct
traceability matrix which keyset is composed of all the requirements of the
document.
-- PRK-REQ

PRK-REQ
PeRKy shall accept a ``COMPACT`` option for ``yield`` command to produce
direct traceability matrix which keyset is composed of only tracked
requirements.
-- PRK-REQ

PRK-REQ
PeRKy shall accept a ``PERMISSIVE`` option to support optional input
transformations.
-- PRK-REQ

PRK-REQ
PeRKy shall accept a ``STRICT`` option to ensure that any warning message on
standard error channel provokes script failure.
-- PRK-REQ

PRK-REQ
PeRKy shall accept an ``INPUT`` option to describe its main input.
-- PRK-REQ

PRK-REQ
PeRKy shall accept an ``OUTPUT`` option to describe its main output.
-- PRK-REQ

PRK-REQ
PeRKy shall accept a ``CLEAN`` option for ``merge`` command to remove all
files corresponding to IPR_ delimiters.
-- PRK-REQ

PRK-REQ
PeRKy allows user to specify all of the configuration options as command-line
options.
-- PRK-REQ

PRK-REQ
PeRKy allows user to specify some of the configuration options in a static
configuration file.
-- PRK-REQ

PRK-REQ
PeRKy shall define a default configuration for the option set it supports.
-- PRK-REQ

PRK-REQ
PeRKy considers only the options given the following way, in decreasing order
of preference:

1) Command-line options

2) Static configuration

3) Default configuration
-- PRK-REQ

Command-line options
''''''''''''''''''''

PRK-REQ
Use of the ``--quiet`` command-line option corresponds to setting the
``QUIET`` option.
-- PRK-REQ

PRK-REQ
Use of the ``--verbose`` command-line option corresponds to setting the
``VERBOSE`` option.
-- PRK-REQ

PRK-REQ
Use of the ``--compact`` command-line option corresponds to setting the
``COMPACT`` option.
-- PRK-REQ

PRK-REQ
Use of the ``--sparse`` command-line option corresponds to setting the
``SPARSE`` option.
-- PRK-REQ

PRK-REQ
Use of the ``--permissive`` command-line option corresponds to setting the
``PERMISSIVE`` option.
-- PRK-REQ

PRK-REQ
Use of the ``--strict`` command-line option corresponds to setting the
``STRICT`` option.
-- PRK-REQ

PRK-REQ
Use of the ``--input`` command-line option corresponds to setting the
``INPUT`` option value.
-- PRK-REQ

PRK-REQ
Use of the ``-i`` command-line option corresponds to setting the
``INPUT`` option value.
-- PRK-REQ

PRK-REQ
Use of the ``--output`` command-line option corresponds to setting the
``OUTPUT`` option value.
-- PRK-REQ

PRK-REQ
Use of the ``-o`` command-line option corresponds to setting the
``OUTPUT`` option value.
-- PRK-REQ

PRK-REQ
PeRKy accepts the following set of command-line options:

-i FILE, --input=FILE   name of the main input file
-o FILE, --output=FILE  name of the main output file

--quiet    no status message is produced on standard error
--verbose  additional messages are produced on standard error

--permissive  support optional input transformations
--strict      any warning provokes script failure

--compact  direct traceability matrix references only tracked requirements
--sparse   direct traceability matrix references all requirements (default)
-- PRK-REQ

Static configuration
''''''''''''''''''''

PRK-REQ
PeRKy searches for static configuration files in the following directories,
in decreasing order of preference:

1) Current directory

2) User's home directory

3) Systemwide directory
-- PRK-REQ

PRK-REQ
PeRKy does not support setting the ``INPUT`` option value in static
configuration file.
-- PRK-REQ

PRK-REQ
PeRKy does not support setting the ``OUTPUT`` option value in static
configuration file.
-- PRK-REQ

PRK-REQ
Any unexpected option in static configuration file shall produce a warning
message.
-- PRK-REQ

PRK-REQ
All warning messages concerning static configuration file shall be produced
before program failure.
-- PRK-REQ

Default configuration
'''''''''''''''''''''

PRK-REQ
By default, PeRKy considers that the ``SPARSE`` option is set, thus the
``COMPACT`` one is not.
-- PRK-REQ

PRK-REQ
By default, PeRKy considers that the ``QUIET`` option is not set.
-- PRK-REQ

PRK-REQ
By default, PeRKy considers that the ``VERBOSE`` option is not set.
-- PRK-REQ

PRK-REQ
By default, PeRKy considers that the ``STRICT`` option is set, thus the
``PERMISSIVE`` one is not.
-- PRK-REQ

PRK-REQ
By default, PeRKy considers that the ``INPUT`` option value is the standard
input.
-- PRK-REQ

PRK-REQ
By default, PeRKy considers that the ``OUTPUT`` option value is the standard
output.
-- PRK-REQ

PRK-REQ
PeRKy shall be able to output default configuration as a static configuration
file.
-- PRK-REQ
