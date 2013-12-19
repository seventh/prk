#!/usr/bin/env python3

# Copyright or © or Copr. Guillaume Lemaître (2013)
#
# guillaume.lemaitre@gmail.com
#
# This software is a computer program whose purpose is to help management
# of software requirements with any SCM.
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

"""(PeRKy) Software requirements management with any SCM

When editing a document, it is best seen as a whole, in a single file. But,
in order to verify its evolution, it is best stored split, a requirement per
file. Finally, additional formatting or treatments may be required on final
output. PeRKy provides developers with the minimum functionalities to go from
one view to another, and thus edit efficiently a requirements documentation.
"""

import collections
import getopt
import hashlib
import io
import logging
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
FORMAT_HEADER = "REQ-"
N = 3

PUBLISH_FORMAT = """**[{req_id}]**

{req_content}

**-- End of requirement**
"""

SPARSE_MATRIX = True

# Intermediate 'command' type
Command = collections.namedtuple("Command", ["function", "input_file"])


##############################################################################
# 'merge' command implementation
##############################################################################

def merge(input_file):
    """Merge command:

    - replace all IPR delimiter with corresponding requirement block
    - add a RRI delimiter for each IPR one
    - replace all LNK delimiter with a TRB delimiter in corresponding
      requirement block
    """
    # Currently used and obsolete requirement identifiers
    used_ids = set()

    # Load traceability matrix, if any
    linked_ids = _read_traceability(input_file)

    with open(input_file, "rt") as text:
        for line in text:
            if line.startswith(TAG_IPR):
                req_id = line[len(TAG_IPR) + 1:-1]
                used_ids.add(req_id)

                sys.stdout.write("{} {}\n".format(TAG_BRB, req_id))

                if req_id in linked_ids:
                    for other_id in sorted(linked_ids[req_id]):
                        sys.stdout.write("{} {}\n".format(TAG_TRB,
                                                          other_id))

                with open(req_id + ".prk", "rt") as req:
                    for line_req in req:
                        sys.stdout.write(line_req)
                sys.stdout.write("{}\n".format(TAG_ERB))

            elif line.startswith(TAG_RRI):
                req_id = line[len(TAG_RRI) + 1:-1]
                used_ids.add(req_id)

            elif line.startswith(TAG_LNK):
                pass

            else:
                sys.stdout.write(line)

        # Keep track of all requirements ids, in case some of them disappear
        # during editing
        for req_id in sorted(used_ids):
            sys.stdout.write("{} {}\n".format(TAG_RRI, req_id))


def _read_traceability(input_file):
    result = collections.defaultdict(set)

    with open(input_file, "rt") as text:
        for line in text:
            if line.startswith(TAG_LNK):
                fields = line.split()
                result[fields[1]].add(fields[2])

    return result


##############################################################################
# 'split' command implementation
##############################################################################

def split(input_file):
    """Split command:

    - replace each BRB/ERB delimiter pair with corresponding IRB delimiter
    - replace all TRB delimiter with corresponding LNK one
    - remove all superfluous RRI delimiter
    """

    # Referenced identifiers by traceability
    linked_ids = dict()

    # Requirement identifiers actually used in current version of the document
    cited_ids = set()

    # Parse file in order to collect already used requirement identifiers,
    # even obsolete ones
    used_ids = _collect_ids(input_file)

    # Actually split the file
    output = sys.stdout
    in_requirement_block = False

    with open(input_file, "rt") as text:
        line_num = 1
        for line in text:
            if line.startswith(TAG_BRB):
                in_requirement_block = True
                req_id = _isolate_id(line, line_num)
                references = set()
                output = io.StringIO()

            elif line.startswith(TAG_ERB):
                output.seek(0)
                content = output.read()

                if req_id is None:
                    req_id = _reserve_id_hash(used_ids, content)
                cited_ids.add(req_id)
                linked_ids[req_id] = references

                output_file = open(req_id + ".prk", "wt")
                output_file.write(content)
                output_file.close()

                output = sys.stdout
                output.write("{} {}\n".format(TAG_IPR, req_id))

                in_requirement_block = False

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

            line_num += 1

        # Keep memory only of unused requirement identifiers
        for req_id in sorted(used_ids.difference(cited_ids)):
            output.write("{} {}\n".format(TAG_RRI, req_id))

        # Keep memory of linked requirement identifiers
        for req_id in sorted(linked_ids):
            for other_id in sorted(linked_ids[req_id]):
                output.write("{} {} {}\n".format(TAG_LNK, req_id,
                                                 other_id))


def _collect_ids(input_file):
    result = set()

    line_num = 0
    with open(input_file, "rt") as text:
        for line in text:
            line_num += 1
            if line.startswith(TAG_RRI):
                req_id = line[len(TAG_RRI) + 1:-1]
                result.add(req_id)

            elif line.startswith(TAG_BRB):
                req_id = _isolate_id(line, line_num)
                if req_id in result:
                    logging.error(
                        "line {}: '{}' identifier is not unique".format(
                            line_num, result))
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


def _reserve_id_cont(used_ids, content):
    max_n = -1
    for used_id in used_ids:
        if used_id.startswith(FORMAT_HEADER):
            n = used_id[len(FORMAT_HEADER):]
            if n.isdigit():
                n = int(n)
                max_n = max(n, max_n)

    max_n += 1
    result = FORMAT_HEADER + ("{:0>" + str(N) + "d}").format(max_n)
    used_ids.add(result)

    return result


def _reserve_id_hash(used_ids, content):
    hashing = hashlib.md5()
    hashing.update(content.encode("utf-8"))
    footprint = str(int(hashing.hexdigest(), 16))[::-1]

    # First try: only the first N characters
    result = FORMAT_HEADER + footprint[:N]
    if result not in used_ids:
        used_ids.add(result)

    # Second try: extract as short prefix as possible
    else:
        footprint = footprint.strip("0")
        for n in range(N, len(footprint) + 1):
            result = FORMAT_HEADER + footprint[:n]
            if result not in used_ids:
                used_ids.add(result)
                break
        else:
            logging.error("Cannot generate a new unique identifier")
            result = None

    return result


##############################################################################
# 'usage' command implementation
##############################################################################

def usage(input_file):
    print("""
Usage: {cmd} [split|merge] FILE
       transform input FILE on standard output

$> {cmd} split FILE > FILE.out
search for each '{req}' mark and output it in a different file

$> {cmd} merge FILE > FILE.out
search for each '{inp}' mark and merge it with normal output

$> {cmd} yield FILE > FILE.out
search for each '{inp}' mark, merge and format it with normal output
""".format(cmd = input_file, req = TAG_BRB, inp = TAG_IPR))


##############################################################################
# 'yield' command implementation
##############################################################################

def yield_cmd(input_file):
    # Load traceability matrix, if any
    linked_ids = _read_traceability(input_file)

    with open(input_file, "rt") as text:
        for line in text:
            if line.startswith(TAG_IPR):
                req_id = line[len(TAG_IPR) + 1:-1]

                content = io.StringIO()
                with open(req_id + ".prk", "rt") as req:
                    for line_req in req:
                        content.write(line_req)

                content.seek(0)
                req_content = content.read().strip("\n")
                sys.stdout.write(PUBLISH_FORMAT.format(
                        req_id = req_id,
                        req_content = req_content))

                if SPARSE_MATRIX and req_id not in linked_ids:
                    linked_ids[req_id] = set()

            # Traceability matrices
            elif line.startswith(TAG_DTM):
                _output_traceability_matrix(linked_ids,
                                            "Requirement",
                                            "Reference")

            elif line.startswith(TAG_RTM):
                _output_traceability_matrix(_transpose_matrix(linked_ids),
                                            "Reference",
                                            "Requirement")

            # Technical informations shall be removed from final document
            elif line.startswith(TAG_RRI):
                pass

            elif line.startswith(TAG_LNK):
                pass

            # Normal output
            else:
                sys.stdout.write(line)


def _output_traceability_matrix(matrix, header_key, header_value):
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
    output = sys.stdout

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

def parse(args):
    result = Command(usage, "prk")

    if len(args) == 2:
        if args[0] == "merge":
            result = Command(merge, args[1])
        elif args[0] == "split":
            result = Command(split, args[1])
        elif args[0] == "yield":
            result = Command(yield_cmd, args[1])

    return result


def parse_command_line(command_line, configuration):
    error_found = False
    opts, args = getopt.getopt(command_line, "i:o:", ["sparse", "compact", "input=", "output="])

    # Parse arguments before options
    if not (1 <= len(args) <= 2):
        logging.error("Wrong number of arguments")
    else:
        if args[0] == "merge":
            configuration["command"] = merge
        elif args[0] == "split":
            configuration["command"] = split
        elif args[0] == "yield":
            configuration["command"] = yield_cmd

        if len(args) >= 2:
            try:
                configuration["input"] = open(args[1], "rt")
            except FileNotFoundError:
                logging.error("File " + args[1] + " does not exist")
                error_found = True

    # Parse options
    if not error_found:
        for opt, val in opts:
            if opt == "--sparse":
                configuration["sparse"] = True
            elif opt == "--compact":
                configuration["sparse"] = False

            elif opt in ["-i", "--input"]:
                try:
                    configuration["input"] = open(val, "rt")
                except FileNotFoundError:
                    logging.error("File " + args[1] + " does not exist")
                    error_found = True

            elif opt in ["-o", "--output"]:
                try:
                    configuration["output"] = open(val, "wt")
                except IOError:
                    logging.error("Cannot open file " + val + " for writing")
                    error_found = True

            else:
                logging.error("Unknown option " + opt)
                error_found = True

    if error_found:
        configuration["command"] = usage



if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)

    # Parse Command line arguments
    CONFIGURATION = {
        "command" : usage,
        "input" : sys.stdin,
        "output" : sys.stdout,

        "sparse" : False,
        }
    parse_command_line(sys.argv[1:], CONFIGURATION)
    print(CONFIGURATION)

    #
    COMMAND = parse(sys.argv[1:])
    COMMAND.function(COMMAND.input_file)
