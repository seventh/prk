#!/usr/bin/env python3

# Copyright or © or Copr. Guillaume Lemaître (2013, 2014, 2018, 2019)
#
# guillaume.lemaitre@gmail.com
#
# This software is a computer program whose purpose is to help management
# of software requirements with any SCM.
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software. You can use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading, using, modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean that it is complicated to manipulate, and that also
# therefore means that it is reserved for developers and experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and, more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
"""(PeRKy) Management of software requirements with any SCM

When editing a document, it is best seen as a whole, in a single file. But,
in order to verify its evolution, it is best stored split, a requirement
per directory. Finally, additional formatting or treatments may be required on
final output. PeRKy provides developers with the minimum functionalities to
go from one view to another, and thus edit efficiently a requirements
documentation.
"""

import collections
import configparser
import getopt
import hashlib
import logging
import os
import re
import sys

# Tags associated to PeRKy delimiters
TAG_BRB = "PRK-REQ"
TAG_BTB = "PRK-TAG"
TAG_DLN = "PRK-DLN"
TAG_DRM = "PRK-DER"
TAG_DTM = "PRK-MTX"
TAG_ERB = "-- PRK-REQ"
TAG_ETB = "-- PRK-TAG"
TAG_IPR = "PRK-INC"
TAG_LNK = "PRK-LNK"
TAG_RRI = "PRK-MEM"
TAG_RTM = "PRK-XTM"
TAG_TOC = "PRK-TOC"
TAG_TRB = "PRK-REF"

# Configurable input/output features
IDENTIFIER_REGEX = "^[_0-9A-Za-z-]+$"

PUBLISH_FORMAT = """.. _{req_id}:

**[{req_id}]**

{req_content}

**-- End of requirement**
"""

##############################################################################
# Utilities
##############################################################################


class IdFactory(object):
    """Generator of identifiers for requirement blocks
    """

    # minimum length of the numerical part
    _N = 4

    # format string used to generate new identifiers
    _FORMAT = "REQ-{}"

    def __init__(self):
        self._reserved_ids = set()

    def add(self, req_id):
        """Add requirement identifier to the list of the already reserved ones
        """
        self._reserved_ids.add(req_id)

    def configure(self, pattern="REQ-%N", width=4):
        """Change pattern used for next generations

        requirement identifier in pattern argument is identified by "%N"
        string. Every "%" character shall be escaped by another "%" in pattern
        argument in order to obtain a single "%" in the generated identifier
        """
        if int(width) > 0:
            self._N = int(width)

        valid_format = False
        escape_mark = False
        proposed_format = ""
        for c in pattern:
            if escape_mark:
                if c == "N":
                    proposed_format += "{0:}"
                    valid_format = True
                else:
                    proposed_format += c
                escape_mark = False
            elif c == "%":
                escape_mark = True
            else:
                proposed_format += c

        if not valid_format:
            logging.error(
                "Pattern '{}' does not contain any valid '%N' mark".format(
                    pattern))
        else:
            if escape_mark:
                logging.warning(
                    "Pattern '{}' ends with extraneous %".format(pattern))
            self._FORMAT = proposed_format

    def generate(self, content):
        """Generate a new requirement identifier from its content
        """
        result = 0

        # Generate a new identifier from requirement content
        hashed_content = self._hash_value(content)
        result = self._extract_new_id(hashed_content)

        # Declare, then return it
        self.add(result)
        return result

    def __iter__(self):
        """Iterates over the set of already reserved ids
        """
        for req_id in self._reserved_ids:
            yield req_id

    def _hash_value(self, string):
        """Hash string with MD5 algorithm
        """
        result = None

        hash_as_string_b16 = hashlib.md5(string.encode("utf-8")).hexdigest()
        hash_as_string_b10 = str(int(hash_as_string_b16, 16))

        # Revert it to equilibrate distribution of values
        result = hash_as_string_b10[::-1]

        return result

    def _extract_new_id(self, footprint):
        """Generate shortest available requirement id from an hash value
        """
        result = None

        for extract in self._iter_footprint(footprint):
            result = self._FORMAT.format(extract)
            if result not in self._reserved_ids:
                break
        else:
            result = None

        if result is not None:
            self.add(result)
        else:
            logging.error("Cannot generate a new unique identifier")

        return result

    def _iter_footprint(self, footprint):
        # First try: search for an identifier of exactly N characters. In this
        # case, it can start by any number of '0' characters
        for offset in range(len(footprint) - self._N + 1):
            yield footprint[offset:offset + self._N]

        # Second try: search for shortest identifier possible. In this case,
        # it cannot start by a '0' character
        for length in range(self._N + 1, len(footprint) + 1):
            for offset in range(len(footprint) - length + 1):
                if footprint[offset] != '0':
                    yield footprint[offset:offset + length]


def preprocess(lines):
    """First pass to analyze various points from document stored line by line:
    - load traceability (if any) from TAG_LNK marks
    - load used requirement identifiers from TAG_BRB and TAG_RRI marks
    - load document structure from reST formatting
    """
    result = {
        "identifiers": IdFactory(),
        "structure": list(),
        "traceability": collections.defaultdict(set),
    }

    codes = list()

    # Three analysis at the price of one!
    for i, line in enumerate(lines):
        line_num = i + 1

        # Identifiers
        if line.startswith(TAG_RRI):
            req_id = line[len(TAG_RRI):].lstrip()
            result["identifiers"].add(req_id)

        elif line.startswith(TAG_BRB):
            req_id = _isolate_id(line, line_num)
            if req_id in result["identifiers"]:
                logging.error("line {}: '{}' identifier is not unique".format(
                    line_num, req_id))
            elif req_id is not None:
                result["identifiers"].add(req_id)

        # Traceability
        elif line.startswith(TAG_LNK):
            req_ids = line[len(TAG_LNK):].split()
            result["traceability"][req_ids[0]].add(req_ids[1])

        elif line.startswith(TAG_DLN):
            req_id = line[len(TAG_DLN):].split()[0]
            result["traceability"][req_id].add(None)

        elif line.startswith(TAG_IPR):
            req_id = line[len(TAG_IPR):].split()[0]
            result["traceability"][req_id].update(set())

        # Structure
        if line_num > 1:
            prefix = line[:4]
            if len(prefix) == 4:
                code = prefix[0]
                if prefix.count(code) == 4 \
                   and code in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~":
                    if code not in codes:
                        codes.append(code)
                    level = codes.index(code)

                    result["structure"].append((level, lines[i - 1]))

    return result


class Requirement(dict):
    """A requirement is like a dictionary, with a required entry called "text"

    Only "text" is a reserved key. As requirement identifier is not an
    attribute of the dictionary itself, no key is reserved in order to store it
    """

    def __init__(self):
        self["text"] = list()
        self._id = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def get_field_as_block(self, field):
        lines = self[field]

        # Sanitation
        for i in range(len(lines)):
            lines[i] = lines[i].rstrip()
        while len(lines) > 0 and len(lines[0]) == 0:
            del lines[0]
        while len(lines) > 0 and len(lines[-1]) == 0:
            del lines[-1]

        # Output
        return "\n".join(lines)

    def as_inline_text(self):
        blocks = list()

        blocks.append(self.get_field_as_block("text"))
        for k in sorted(self):
            if k != "text":
                v = self.get_field_as_block(k)
                if len(v) == 0:
                    blocks.append("{} {}".format(TAG_BTB, k))
                elif "\n" in v:
                    blocks.append("{} {}\n{}\n{}".format(
                        TAG_BTB, k, v, TAG_ETB))
                else:
                    blocks.append("{} {} {}".format(TAG_BTB, k, v))

        return "\n\n".join(blocks)

    def as_plain_text(self, configuration, used_ids):
        if self.id is None:
            self.id = used_ids.generate(self.get_field_as_block("text"))

        with open(os.path.join(configuration["output_root"], self.id + ".prk"),
                  "wt") as output_file:
            output_file.write(self.as_inline_text() + "\n")

    def as_directory(self, configuration, used_ids):
        if self.id is None:
            self.id = used_ids.generate(self.get_field_as_block("text"))

        path = os.path.join(configuration["output_root"], self.id)
        os.makedirs(path, exist_ok=True)
        for field in self:
            with open(os.path.join(path, field), "wt") as output_file:
                output_file.write(self.get_field_as_block(field))

    @staticmethod
    def from_directory_content(path):
        result = Requirement()

        root, dirs, files = next(os.walk(path))
        for f in files:
            with open(os.path.join(root, f), "rt") as input_file:
                result[f] = input_file.read().split("\n")

        return result

    @staticmethod
    def from_file_content(path):
        """No parsing -- all file content is considered requirement itself
        """
        result = Requirement()

        with open(path, "rt") as input_file:
            result["text"] = input_file.read().split("\n")

        return result


##############################################################################
# 'boost', 'cross' and 'track' commands implementation
##############################################################################


def boost(configuration):
    """Boost command outputs the list of requirement identifiers defined by
    the input document itself
    """
    # Load main input and replace if with a list of lines
    configuration["input"] = _load_file(configuration["input"])

    # Load traceability matrix, if any
    linked_ids = preprocess(configuration["input"])["traceability"]

    # Output the list of defined requirements
    for req_id in sorted(linked_ids):
        configuration["output"].write("{}\n".format(req_id))


def cross(configuration):
    """Cross command outputs the direct traceabilty matrix, a pair of
    requirements per line
    """
    # Load main input and replace if with a list of lines
    configuration["input"] = _load_file(configuration["input"])

    # Load traceability matrix, if any
    linked_ids = preprocess(configuration["input"])["traceability"]

    # Output the list of defined requirements
    matrix = _transpose_matrix(linked_ids)
    for ref_id in sorted(matrix):
        if ref_id is not None:
            for req_id in sorted(matrix[ref_id]):
                configuration["output"].write("{} {}\n".format(ref_id, req_id))


def track(configuration):
    """Track command outputs the list of requirement identifiers referenced by
    the input document
    """
    # Load main input and replace if with a list of lines
    configuration["input"] = _load_file(configuration["input"])

    # Load traceability matrix, if any
    linked_ids = preprocess(configuration["input"])["traceability"]

    # Output the list of defined requirements
    ref_ids = set()
    for req_id in linked_ids:
        ref_ids.update(linked_ids[req_id])

    ref_ids.discard(None)

    for ref_id in sorted(ref_ids):
        configuration["output"].write("{}\n".format(ref_id))


##############################################################################
# 'merge' command implementation
##############################################################################


def merge(configuration):
    """Merge command:

    - replace all IPR delimiter with corresponding requirement block
    - add a RRI delimiter for each IPR one
    - replace all LNK delimiter with a TRB delimiter in corresponding
      requirement block
    """
    # Currently used and obsolete requirement identifiers
    used_ids = IdFactory()

    # Load main input and replace it with a list of lines
    configuration["input"] = _load_file(configuration["input"])

    # Load traceability matrix, if any
    linked_ids = preprocess(configuration["input"])["traceability"]

    line_num = 0
    for line in configuration["input"]:
        line_num += 1

        if line.startswith(TAG_IPR):
            req_id = line[len(TAG_IPR):].lstrip()
            used_ids.add(req_id)

            configuration["output"].write("{} {}\n".format(TAG_BRB, req_id))

            if req_id in linked_ids:
                ref_ids = sorted(linked_ids[req_id])
                if None in ref_ids:
                    configuration["output"].write("{}\n".format(TAG_DRM))
                else:
                    for ref_id in sorted(linked_ids[req_id]):
                        configuration["output"].write("{} {}\n".format(
                            TAG_TRB, ref_id))

            # Give higher priority to requirement management with directory
            # than by file
            if os.path.isdir(req_id):
                requirement = Requirement.from_directory_content(
                    os.path.join(configuration["input_root"], req_id))
            else:
                requirement = Requirement.from_file_content(
                    os.path.join(configuration["input_root"], req_id + ".prk"))
            requirement.id = req_id

            configuration["output"].write("{}\n".format(
                requirement.as_inline_text()))
            configuration["output"].write("{}\n".format(TAG_ERB))

        elif line.startswith(TAG_RRI):
            req_id = line[len(TAG_RRI):].lstrip()
            used_ids.add(req_id)

        elif line.startswith(TAG_LNK):
            pass

        elif line.startswith(TAG_DLN):
            pass

        # Permissive transformations
        elif line.startswith(TAG_BRB):
            if not configuration["permissive"]:
                logging.warning(
                    "line {}: BRB tag should not be present in input".format(
                        line_num))
            else:
                pass

        elif line.startswith(TAG_ERB):
            pass

        # Normal output
        else:
            configuration["output"].write("{}\n".format(line))

    # Keep track of all requirements ids, in case some of them disappear
    # during editing
    for req_id in sorted(used_ids):
        configuration["output"].write("{} {}\n".format(TAG_RRI, req_id))


##############################################################################
# 'split' command implementation
##############################################################################


def split(configuration):
    """Split command:

    - replace each BRB/ERB delimiter pair with corresponding IRB delimiter
    - replace all TRB delimiter with corresponding LNK one
    - remove all superfluous RRI delimiter
    """

    # Referenced identifiers by traceability
    linked_ids = dict()

    # Requirement identifiers actually used in current version of the document
    cited_ids = set()

    # Load main input and replace it with a list of lines
    configuration["input"] = _load_file(configuration["input"])

    # Parse file in order to collect already used requirement identifiers,
    # even obsolete ones
    used_ids = preprocess(configuration["input"])["identifiers"]
    used_ids.configure(pattern=configuration["format"],
                       width=configuration["width"])

    # Actually split the file
    output = configuration["output"]

    def output_requirement(requirement, configuration, used_ids, cited_ids,
                           linked_ids):
        if configuration["storage"] == 0:
            requirement.as_plain_text(configuration, used_ids)
        else:
            requirement.as_directory(configuration, used_ids)
        cited_ids.add(requirement.id)
        linked_ids[requirement.id] = references

        configuration["output"].write("{} {}\n".format(TAG_IPR,
                                                       requirement.id))

    requirement = None
    field = "text"
    require_etb = 0  # 3-state variable (0: no, 1: maybe, 2: yes)

    line_num = 0
    for line in configuration["input"]:
        line_num += 1

        if line.startswith(TAG_BRB):
            if requirement is not None:
                output_requirement(requirement, configuration, used_ids,
                                   cited_ids, linked_ids)

            requirement = Requirement()
            field = "text"
            require_etb = 0
            requirement.id = _isolate_id(line, line_num)
            references = set()

        elif line.startswith(TAG_ERB):
            output_requirement(requirement, configuration, used_ids, cited_ids,
                               linked_ids)
            requirement = None

        elif line.startswith(TAG_TRB):
            if requirement is None:
                logging.warning(
                    "line {}: TRB tag outside of any requirement block".format(
                        line_num))
            else:
                ref_id = line[len(TAG_TRB):].lstrip()
                references.add(ref_id)
                field = "text"
                require_etb = 0

        elif line.startswith(TAG_DRM):
            if requirement is None:
                logging.warning(
                    "line {}: DRM tag outside of any requirement block".format(
                        line_num))
            else:
                references.add(None)
                field = "text"
                require_etb = 0

        elif line.startswith(TAG_BTB):
            if requirement is None:
                logging.warning(
                    "line {}: TAG tag outside of any requirement block".format(
                        line_num))
            else:
                m = re.match(r"{}\s+(\S+)\s*(.*)".format(TAG_BTB), line)
                if not m:
                    logging.warning(
                        "line {}: TAG requires an identifier right after it".
                        format(line_num))
                else:
                    field = m.group(1)
                    if field in requirement:
                        logging.warning(
                            "line {}: TAG {!r} is present twice in requirement"
                            .format(line_num, field))

                    if len(m.group(2)) == 0:
                        require_etb = 1  # maybe
                        requirement[field] = list()
                    else:
                        require_etb = 0  # not required
                        requirement[field] = [m.group(2)]

        elif line.startswith(TAG_ETB):
            if requirement is None:
                logging.warning(
                    "line {}: end of TAG tag outside of any requirement block".
                    format(line_num))
            else:
                field = "text"
                require_etb = 0

        elif not line.startswith(TAG_RRI):
            if requirement is None:
                output.write("{}\n".format(line))
            elif field == "text":
                requirement[field].append(line)
            else:
                if require_etb == 2:
                    requirement[field].append(line)
                elif require_etb == 1:
                    if len(line) == 0:
                        field = "text"
                    else:
                        if len(requirement[field]) == 0:
                            require_etb = 2
                        requirement[field].append(line)
                else:  # require_etb == 0
                    if len(line) == 0:
                        field = "text"
                    else:
                        requirement[field].append(line)

    if requirement is not None:
        output_requirement(requirement, configuration, used_ids, cited_ids,
                           linked_ids)

    # Keep memory only of unused requirement identifiers
    for req_id in sorted(set(used_ids).difference(cited_ids)):
        output.write("{} {}\n".format(TAG_RRI, req_id))

    # Keep memory of linked requirement identifiers
    for req_id in sorted(linked_ids):
        ref_ids = sorted(linked_ids[req_id])
        if None in ref_ids:
            output.write("{} {}\n".format(TAG_DLN, req_id))
        else:
            for other_id in ref_ids:
                output.write("{} {} {}\n".format(TAG_LNK, req_id, other_id))


def _isolate_id(line, line_num):
    result = line[len(TAG_BRB):].lstrip()

    if len(result) == 0:
        result = None
    elif not re.match(IDENTIFIER_REGEX, result):
        logging.error("line {}: '{}' identifier is ill formed".format(
            line_num, result))
        result = None

    return result


##############################################################################
# 'usage' command implementation
##############################################################################


def usage(configuration):
    print("""Usage: {cmd} boost|cross|merge|split|track|yield [OPTIONS] [FILE]
       transform input FILE on standard output

$> {cmd} split FILE > FILE.out
search for each '{req}' mark and output it in a different file

$> {cmd} merge FILE > FILE.out
search for each '{inp}' mark and merge it with normal output

$> {cmd} yield FILE > FILE.out
search for each '{inp}' mark, merge and format it with normal output

$> {cmd} boost FILE > FILE.out
output all requirements introduced by the document, one per line

$> {cmd} cross FILE > FILE.out
output direct traceability matrix, one per of requirements per line

$> {cmd} track FILE > FILE.out
output all requirements referenced by the document, one per line
""".format(cmd="prk", req=TAG_BRB, inp=TAG_IPR))


##############################################################################
# 'yield' command implementation
##############################################################################


def yield_cmd(configuration):
    # Load main input and replace it with a list of lines
    configuration["input"] = _load_file(configuration["input"])

    additional_data = preprocess(configuration["input"])
    linked_ids = additional_data["traceability"]
    structure = additional_data["structure"]

    line_num = 0
    for line in configuration["input"]:
        line_num += 1
        if line.startswith(TAG_IPR):
            req_id = line[len(TAG_IPR):].lstrip()

            # Give higher priority to requirement management with directory
            # than by file
            if os.path.isdir(req_id):
                requirement = Requirement.from_directory_content(
                    os.path.join(configuration["input_root"], req_id))
            else:
                requirement = Requirement.from_file_content(
                    os.path.join(configuration["input_root"], req_id + ".prk"))
            requirement.id = req_id

            req_content = requirement.as_inline_text()
            configuration["output"].write(
                PUBLISH_FORMAT.format(req_id=req_id, req_content=req_content))

        # Traceability matrices
        elif line.startswith(TAG_DTM):
            _output_traceability_matrix(True, linked_ids, configuration)

        elif line.startswith(TAG_RTM):
            _output_traceability_matrix(False, linked_ids, configuration)

        # Table of contents
        elif line.startswith(TAG_TOC):
            if len(structure) > 0:
                _output_table_of_contents(structure, configuration)

        # Technical informations shall be removed from final document
        elif line.startswith(TAG_RRI):
            pass

        elif line.startswith(TAG_LNK):
            pass

        elif line.startswith(TAG_DLN):
            pass

        # Permissive transformations
        elif line.startswith(TAG_BRB):
            if not configuration["permissive"]:
                logging.warning(
                    "line {}: BRB tag should not be present in input".format(
                        line_num))
            else:
                pass

        elif line.startswith(TAG_ERB):
            pass

        # Normal output
        else:
            configuration["output"].write("{}\n".format(line))


def _output_traceability_matrix(is_direct, matrix, configuration):
    derived_txt = "Derived requirement"

    if is_direct:
        header_key, header_value = "Requirement", "Reference"
        key_suffix, value_suffix = "_", ""
    else:
        header_value, header_key = "Requirement", "Reference"
        value_suffix, key_suffix = "_", ""
        matrix = _transpose_matrix(matrix)

    # Determine formatting parameters
    key_length = len(header_key)
    value_length = len(header_value)

    for key in matrix:
        if configuration["sparse"] or len(matrix[key]) > 0:
            if len(key + key_suffix) > key_length:
                key_length = len(key + key_suffix)
            for value in matrix[key]:
                if value is None:
                    value = derived_txt
                if len(value + value_suffix) > value_length:
                    value_length = len(value + value_suffix)

    horizontal_line = "+" + ("-" * (key_length + 2)) \
        + "+" + ("-" * (value_length + 2)) + "+" + "\n"
    formatting = ("| {{key: <{klen}}} " + "| {{value: <{vlen}}} " +
                  "|\n").format(klen=key_length, vlen=value_length)

    # Header
    output = configuration["output"]

    output.write(horizontal_line)
    output.write(formatting.format(key=header_key, value=header_value))
    output.write(horizontal_line)

    for req_id in sorted(matrix):
        values = sorted(matrix[req_id])

        if len(values) == 0:
            if configuration["sparse"]:
                output.write(
                    formatting.format(key=req_id + key_suffix, value=""))
                output.write(horizontal_line)

        elif len(values) == 1:
            if values[0] is None:
                txt = derived_txt
            else:
                txt = values[0]

            output.write(
                formatting.format(key=req_id + key_suffix,
                                  value=txt + value_suffix))
            output.write(horizontal_line)

        else:  # if len(values) > 1:
            output.write(
                formatting.format(key=req_id + key_suffix,
                                  value=values[0] + value_suffix))
            for i in range(1, len(values)):
                output.write(
                    formatting.format(key="", value=values[i] + value_suffix))
            output.write(horizontal_line)


def _transpose_matrix(matrix):
    result = collections.defaultdict(set)

    for key in matrix:
        for value in matrix[key]:
            if value is not None:
                result[value].add(key)

    return result


def _output_table_of_contents(structure, configuration):
    output = configuration["output"]
    entries = list()

    for entry in structure:
        level, title = entry
        entries.append(2 * level * " " + "+ `" + title + "`_\n")

    output.write("\n".join(entries))


# Other functions


def load_user_configuration(tokens):
    """Command-line options parser
    """
    result = dict()
    error_encountered = False

    # Parse command name
    if len(tokens) < 1:
        logging.critical("A command (among 'boost', 'merge', 'split', " +
                         "'track' or 'yield') shall be provided")
        error_encountered = True
    elif tokens[0] == "boost":
        result["command"] = boost
    elif tokens[0] == "cross":
        result["command"] = cross
    elif tokens[0] == "merge":
        result["command"] = merge
    elif tokens[0] == "split":
        result["command"] = split
    elif tokens[0] == "track":
        result["command"] = track
    elif tokens[0] == "yield":
        result["command"] = yield_cmd
    else:
        logging.critical("Unknown command - first argument shall either be " +
                         "'boost', 'cross', 'merge', 'split', 'track' or " +
                         "'yield'")
        error_encountered = True

    # Parse remaining tokens as options and arguments
    opts = list()
    args = list()
    if not error_encountered:
        try:
            opts, args = getopt.getopt(tokens[1:], "i:o:", [
                "input=", "output=", "compact", "permissive", "quiet",
                "sparse", "strict", "verbose"
            ])
        except getopt.GetoptError as e:
            logging.error(e)
            error_encountered = True

    # Any argument is taken as input
    if not error_encountered:
        if len(args) == 1:
            try:
                result["input"] = open(args[0], "rt")
                result["input_root"] = os.path.dirname(args[0])
            except OSError as e:
                logging.critical(e)
                error_encountered = True
        elif len(args) > 1:
            logging.critical("Wrong number of arguments")
            error_encountered = True

    # Parse options
    for opt, val in opts:
        if opt == "--sparse":
            result["sparse"] = True
        elif opt == "--compact":
            result["sparse"] = False

        elif opt in ["-i", "--input"]:
            try:
                result["input"] = open(val, "rt")
                result["input_root"] = os.path.dirname(val)
            except OSError as e:
                logging.critical(e)
                error_encountered = True

        elif opt in ["-o", "--output"]:
            try:
                result["output"] = open(val, "wt")
                result["output_root"] = os.path.dirname(val)
            except OSError as e:
                logging.critical(e)
                error_encountered = True

        elif opt == "--quiet":
            result["log_level"] = 0

        elif opt == "--verbose":
            result["log_level"] = 2

        elif opt == "--strict":
            result["strict"] = True

        elif opt == "--permissive":
            result["permissive"] = True

    #
    if error_encountered:
        result["command"] = usage

    return result


def _load_file(input_file):
    """Load file as a list of lines.
    """
    result = list()

    if type(input_file) == type(str):
        input_file = open(input_file, "rt")

    for line in input_file:
        result.append(line.rstrip())

    return result


def load_static_configuration(input_root):
    result = dict()
    config_file = configparser.RawConfigParser()

    # First, find adequate configuration file:
    for location in iterate_configuration_file_locations(input_root):
        if os.path.exists(location):
            config_file.read(location)
            logging.info("Loaded configuration file: '{}'".format(location))
            break
    else:
        logging.info("No configuration file is available.")

    # Then, read it
    for section in config_file:
        if section == "merge":
            pass

        elif section == "split":
            for option in config_file.options(section):
                if option == "format":
                    result["format"] = config_file[section][option]
                elif option == "storage":
                    result["storage"] = int(config_file[section][option])
                elif option == "width":
                    result["width"] = int(config_file[section][option])
                else:
                    logging.warning(
                        "Unknown option '{}' in '{}' section of" +
                        " configuration file".format(option, section))

        elif section == "yield":
            for option in config_file.options(section):
                if option == "sparse":
                    result["sparse"] = eval(config_file[section][option])
                elif option == "compact":
                    result["sparse"] = not eval(config_file[section][option])
                else:
                    logging.warning(
                        "Unknown option '{}' in '{}' section of" +
                        " configuration file".format(option, section))
            pass

        # Section created by configparser: should be empty
        elif section == "DEFAULT":
            if len(config_file.defaults()) != 0:
                logging.warning(
                    "No default option is authorized in configuration file.")

        # Other sections created by user himself
        else:
            logging.warning(
                "Unknown section '{}' in configuration file.".format(section))

    return result


def iterate_configuration_file_locations(input_root):
    # Directory hosting input argument, or current directory if stdin
    yield os.path.join(input_root, "prkrc.ini")

    # User's home directory
    yield os.path.join(os.environ["HOME"], ".prkrc")

    # Systemwide configuration directory
    yield "/etc/prkrc"


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)

    # Default configuration
    DEFAULT_CONFIGURATION = {
        "command": usage,
        "format": "REQ-%N",
        "input": sys.stdin,
        "input_root": os.getcwd(),
        "log_level": 1,
        "output": sys.stdout,
        "output_root": os.getcwd(),
        "permissive": False,
        "sparse": False,
        "storage": 1,
        "strict": False,
        "width": 4,
    }

    USER_CONFIGURATION = load_user_configuration(sys.argv[1:])

    # This configuration can only be loaded once INPUT argument is known, but
    # its eventual effectual effects shall be applied prior to any
    # command-line argument!

    input_root = None
    if "input_root" in USER_CONFIGURATION:
        input_root = USER_CONFIGURATION["input_root"]
    else:
        input_root = DEFAULT_CONFIGURATION["input_root"]

    STATIC_CONFIGURATION = load_static_configuration(input_root)

    # Calculate actual configuration
    CONFIGURATION = dict(DEFAULT_CONFIGURATION)
    CONFIGURATION.update(STATIC_CONFIGURATION)
    CONFIGURATION.update(USER_CONFIGURATION)

    # Execute requested transformation
    CONFIGURATION["command"](CONFIGURATION)
