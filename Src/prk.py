#!/usr/bin/env python3

# Copyright or © or Copr. Guillaume Lemaître (2013)
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
per file. Finally, additional formatting or treatments may be required on
final output. PeRKy provides developers with the minimum functionalities to
go from one view to another, and thus edit efficiently a requirements
documentation.
"""

import collections
import configparser
import getopt
import hashlib
import io
import logging
import os
import re
import sys

# Tags associated to PeRKy delimiters
TAG_BRB = "PRK-REQ"
TAG_DTM = "PRK-MTX"
TAG_ERB = "-- PRK-REQ"
TAG_IPR = "PRK-INC"
TAG_LNK = "PRK-LNK"
TAG_RRI = "PRK-MEM"
TAG_RTM = "PRK-XTM"
TAG_TRB = "PRK-REF"

# Configurable input/output features
IDENTIFIER_REGEX = "^[0-9A-Za-z-]+$"

PUBLISH_FORMAT = """**[{req_id}]**

{req_content}

**-- End of requirement**
"""

##############################################################################
# Utility classes
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


    def configure(self, pattern = "REQ-%N", width = 4):
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
            logging.error("Pattern '{}' does not contain any valid '%N' mark".format(pattern))
        else:
            if escape_mark:
                logging.warning("Pattern '{}' ends with extraneous %".format(pattern))
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
        # First try: only the first N characters
        result = self._FORMAT.format(footprint[:self._N])

        # Second try: extract as short prefix as possible
        if result in self._reserved_ids:
            footprint = footprint.strip("0")
            for n in range(self._N, len(footprint) + 1):
                result = self._FORMAT.format(footprint[:n])
                if result not in self._reserved_ids:
                    break
            else:
                result = None

        if result is not None:
            self.add(result)
        else:
            logging.error("Cannot generate a new unique identifier")

        return result



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
    linked_ids = _read_traceability(configuration)

    line_num = 0
    for line in configuration["input"]:
        line_num += 1

        if line.startswith(TAG_IPR):
            req_id = line[len(TAG_IPR) + 1:-1]
            used_ids.add(req_id)

            configuration["output"].write("{} {}\n".format(TAG_BRB, req_id))

            if req_id in linked_ids:
                for other_id in sorted(linked_ids[req_id]):
                    configuration["output"].write("{} {}\n".format(TAG_TRB,
                                                                   other_id))

            with open(req_id + ".prk", "rt") as req:
                for line_req in req:
                    configuration["output"].write(line_req)
            configuration["output"].write("{}\n".format(TAG_ERB))

        elif line.startswith(TAG_RRI):
            req_id = line[len(TAG_RRI) + 1:-1]
            used_ids.add(req_id)

        elif line.startswith(TAG_LNK):
            pass

        # Permissive transformations
        elif line.startswith(TAG_BRB):
            if not configuration["permissive"]:
                logging.warning(
                    "line {}: BRB tag should not be present in input"
                    .format(line_num))
            else:
                pass

        elif line.startswith(TAG_ERB):
            pass

        # Normal output
        else:
            configuration["output"].write(line)

    # Keep track of all requirements ids, in case some of them disappear
    # during editing
    for req_id in sorted(used_ids):
        configuration["output"].write("{} {}\n".format(TAG_RRI, req_id))


def _read_traceability(configuration):
    result = collections.defaultdict(set)

    for line in configuration["input"]:
        if line.startswith(TAG_LNK):
            fields = line.split()
            result[fields[1]].add(fields[2])

    return result


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
    used_ids = _collect_ids(configuration)

    # Actually split the file
    output = configuration["output"]
    in_requirement_block = False

    def output_requirement():
        nonlocal output, req_id, cited_ids, linked_ids, in_requirement_block

        output.seek(0)
        content = output.read()

        if req_id is None:
            req_id = used_ids.generate(content)
        cited_ids.add(req_id)
        linked_ids[req_id] = references

        output_file = open(req_id + ".prk", "wt")
        output_file.write(content)
        output_file.close()

        output = configuration["output"]
        output.write("{} {}\n".format(TAG_IPR, req_id))

        in_requirement_block = False

    line_num = 0
    for line in configuration["input"]:
        line_num += 1

        if line.startswith(TAG_BRB):
            if in_requirement_block:
                output_requirement()

            in_requirement_block = True
            req_id = _isolate_id(line, line_num)
            references = set()
            output = io.StringIO()

        elif line.startswith(TAG_ERB):
            output_requirement()

        elif line.startswith(TAG_TRB):
            if not in_requirement_block:
                logging.warning(
                    "line {}: TRB tag outside of any requirement block"
                    .format(line_num))
            else:
                other_id = line[len(TAG_TRB) + 1:-1]
                references.add(other_id)

        elif not line.startswith(TAG_RRI):
            output.write(line)

    if in_requirement_block:
        output_requirement()

    # Keep memory only of unused requirement identifiers
    for req_id in sorted(set(used_ids).difference(cited_ids)):
        output.write("{} {}\n".format(TAG_RRI, req_id))

    # Keep memory of linked requirement identifiers
    for req_id in sorted(linked_ids):
        for other_id in sorted(linked_ids[req_id]):
            output.write("{} {} {}\n".format(TAG_LNK, req_id,
                                             other_id))


def _collect_ids(configuration):
    result = IdFactory()

    line_num = 0
    for line in configuration["input"]:
        line_num += 1
        if line.startswith(TAG_RRI):
            req_id = line[len(TAG_RRI) + 1:-1]
            result.add(req_id)

        elif line.startswith(TAG_BRB):
            req_id = _isolate_id(line, line_num)
            if req_id in result:
                logging.error(
                    "line {}: '{}' identifier is not unique".format(
                        line_num, req_id))
            elif req_id is not None:
                result.add(req_id)

    return result


def _isolate_id(line, line_num):
    result = line[len(TAG_BRB):].strip()

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
    print("""Usage: {cmd} merge|split|yield [OPTIONS] [FILE]
       transform input FILE on standard output

$> {cmd} split FILE > FILE.out
search for each '{req}' mark and output it in a different file

$> {cmd} merge FILE > FILE.out
search for each '{inp}' mark and merge it with normal output

$> {cmd} yield FILE > FILE.out
search for each '{inp}' mark, merge and format it with normal output
""".format(cmd = "prk", req = TAG_BRB, inp = TAG_IPR))


##############################################################################
# 'yield' command implementation
##############################################################################

def yield_cmd(configuration):
    # Load main input and replace it with a list of lines
    configuration["input"] = _load_file(configuration["input"])

    # Load traceability matrix, if any
    linked_ids = _read_traceability(configuration)

    line_num = 0
    for line in configuration["input"]:
        line_num += 1
        if line.startswith(TAG_IPR):
            req_id = line[len(TAG_IPR) + 1:-1]

            content = io.StringIO()
            with open(req_id + ".prk", "rt") as req:
                for line_req in req:
                    content.write(line_req)

            content.seek(0)
            req_content = content.read().strip("\n")
            configuration["output"].write(PUBLISH_FORMAT.format(
                req_id = req_id,
                req_content = req_content))

            if configuration["sparse"] and req_id not in linked_ids:
                linked_ids[req_id] = set()

        # Traceability matrices
        elif line.startswith(TAG_DTM):
            _output_traceability_matrix(linked_ids,
                                        "Requirement",
                                        "Reference",
                                        configuration)

        elif line.startswith(TAG_RTM):
            _output_traceability_matrix(_transpose_matrix(linked_ids),
                                        "Reference",
                                        "Requirement",
                                        configuration)

        # Technical informations shall be removed from final document
        elif line.startswith(TAG_RRI):
            pass

        elif line.startswith(TAG_LNK):
            pass

        # Permissive transformations
        elif line.startswith(TAG_BRB):
            if not configuration["permissive"]:
                logging.warning(
                    "line {}: BRB tag should not be present in input"
                    .format(line_num))
            else:
                pass

        elif line.startswith(TAG_ERB):
            pass

        # Normal output
        else:
            configuration["output"].write(line)


def _output_traceability_matrix(matrix, header_key, header_value,
                                configuration):
    # Determine formatting parameters
    key_length = len(header_key)
    value_length = len(header_value)

    for key in matrix:
        if len(key) > key_length:
            key_length = len(key)
        for value in matrix[key]:
            if len(value) > value_length:
                value_length = len(value)

    horizontal_line = "+" + ("-" * (key_length + 2)) \
        + "+" + ("-" * (value_length + 2)) + "+" + "\n"
    formatting = ("| {{key: <{klen}}} " \
                      + "| {{value: <{vlen}}} " \
                      + "|\n").format(klen = key_length,
                                      vlen = value_length)

    # Header
    output = configuration["output"]

    output.write(horizontal_line)
    output.write(formatting.format(key = header_key, value = header_value))
    output.write(horizontal_line)

    for req_id in sorted(matrix):
        values = sorted(matrix[req_id])

        if len(values) == 0:
            output.write(formatting.format(key = req_id, value = ""))
            output.write(horizontal_line)

        elif len(values) == 1:
            output.write(formatting.format(key = req_id, value = values[0]))
            output.write(horizontal_line)

        else: # if len(values) > 1:
            output.write(formatting.format(key = req_id, value = values[0]))
            for i in range(1, len(values)):
                output.write(formatting.format(key = "", value = values[i]))
            output.write(horizontal_line)


def _transpose_matrix(matrix):
    result = collections.defaultdict(set)

    for key in matrix:
        for value in matrix[key]:
            result[value].add(key)

    return result


# Other functions

def parse(tokens, configuration):
    """Command-line options parser
    """
    error_encountered = False

    # Parse command name
    if len(tokens) < 1:
        logging.critical("A command ('merge', 'split' or 'yield') shall be " \
                         "provided")
        error_encountered = True
    elif tokens[0] == "merge":
        configuration["command"] = merge
    elif tokens[0] == "split":
        configuration["command"] = split
    elif tokens[0] == "yield":
        configuration["command"] = yield_cmd
    else:
        logging.critical("Unknown command - first argument shall either be " \
                      + "'merge', 'split' or 'yield'")
        error_encountered = True

    # Parse remaining tokens as options and arguments
    opts = list()
    args = list()
    if not error_encountered:
        try:
            opts, args = getopt.getopt(tokens[1:],
                                       "i:o:",
                                       ["input=", "output=",
                                        "compact", "permissive", "quiet",
                                        "sparse", "strict", "verbose"])
        except getopt.GetoptError as e:
            logging.error(e)
            error_encountered = True

    # Any argument is taken as input
    if not error_encountered:
        if len(args) == 1:
            try:
                configuration["input"] = open(args[0], "rt")
            except OSError as e:
                logging.critical(e)
                error_encountered = True
        elif len(args) > 1:
            logging.critical("Wrong number of arguments")
            error_encountered = True

    # Parse options
    for opt, val in opts:
        if opt == "--sparse":
            configuration["sparse"] = True
        elif opt == "--compact":
            configuration["sparse"] = False

        elif opt in ["-i", "--input"]:
            try:
                configuration["input"] = open(val, "rt")
            except OSError as e:
                logging.critical(e)
                error_encountered = True

        elif opt in ["-o", "--output"]:
            try:
                configuration["output"] = open(val, "wt")
            except OSError as e:
                logging.critical(e)
                error_encountered = True

        elif opt == "--quiet":
            configuration["log_level"] = 0

        elif opt == "--verbose":
            configuration["log_level"] = 2

        elif opt == "--strict":
            configuration["strict"] = True

        elif opt == "--permissive":
            configuration["permissive"] = True

    #
    if error_encountered:
        configuration["command"] = usage


def _load_file(input_file):
    """Load file as a list of lines.
    """
    result = None

    if type(input_file) == type(str):
        input_file = open(input_file, "rt")

    result = list(input_file)

    return result


def load_configuration():
    result = dict()
    config_file = configparser.ConfigParser()

    # First, find adequate configuration file:
    for location in iterate_configuration_file_locations():
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
        elif section == "yield":
            for option in config_file.options(section):
                if option == "sparse":
                    pass
                else:
                    logging.warning("Unknown option '{}' in '{}' section of configuration file".format(option, section))
            pass
        elif section == "split":
            pass

        # Section created by configparser: should be empty
        elif section == "DEFAULT":
            if len(config_file.defaults()) != 0:
                logging.warning("No default option is authorized in configuration file.")

        # Other sections created by user himself
        else:
            logging.warning("Unknown section '{}' in configuration file.".format(section))


def iterate_configuration_file_locations():
    # Current directory
    yield ".prkrc"

    # User's home directory
    yield os.path.join(os.environ["HOME"], ".prkrc")

    # Systemwide configuration directory
    yield "/etc/prkrc"



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    CONFIGURATION = {
        "command": usage,
        "input": sys.stdin,
        "log_level": 1,
        "output": sys.stdout,
        "permissive": False,
        "sparse": False,
        "strict": False,
    }

    parse(sys.argv[1:], CONFIGURATION)

    # load_configuration()

    # Execute requested transformation
    CONFIGURATION["command"](CONFIGURATION)
