#!/usr/bin/env python3

# Copyright or © or Copr. Guillaume Lemaître (2014)
#
# guillaume.lemaitre@gmail.com
#
# This software is a computer program whose purpose is to reformat text files.
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

import re
import sys

MAX_WIDTH=78

def redistribute(filename):
    # Read file
    content = ""
    with open(filename, "rt") as flow:
        content = " ".join(flow)
        content = re.sub("\s+", " ", content)
        content = content.strip()

    # Write file
    with open(filename, "wt") as flow:
        while len(content) > 0:
            if len(content) <= MAX_WIDTH + 1:
                i = len(content) + 1
            else:
                for i in range(MAX_WIDTH + 1, 0, -1):
                    if content[i] == " ":
                        break
                else:
                    for i in range(MAX_WIDTH, len(content) + 1):
                        if content[i] == " ":
                            break
            flow.write(content[:i] + "\n")
            content = content[i + 1:]


if __name__ == "__main__":
    for filename in sys.argv[1:]:
        redistribute(filename)
