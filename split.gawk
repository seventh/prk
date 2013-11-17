# Copyright or © or Copr. Guillaume Lemaître (2013)
#
# guillaume.lemaitre@gmail.com
#
# This software is a computer program whose purpose is to help management
# of requirements'documentation with any SCM.
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

function build_id(n) {
    result = ""

    k = length(n)
    i = 1
    complement = ""
    while (i <= 3-k) {
        complement = "0" complement
        i = i + 1
    }

    result = "SPEC-REQ-" complement n
    return result
}


function reserve_id() {
    result = ""

    while (1) {
        result = build_id(N)
        N += 1
        if (! (result in USED)) {
            break
        }
    }

    USED[result] = 1
    return result
}


BEGIN {
    # Globals for automatic ID generation
    N = 0
    USED[0] = 1

    # Global used to select output file
    REQ = 0
}


# Either retrieve id or generate a new one

REQ == 0 && /^RMS-REQ$/ {
  REQ = 1

  LABEL_REQ = reserve_id()
}


REQ == 0 && /^RMS-REQ/ {
  REQ = 1

  LABEL_REQ = $0
  sub($1, "", LABEL_REQ)
  gsub("[[:blank:]]", "_", LABEL_REQ)
  sub("^_*", "", LABEL_REQ)

  if (LABEL_REQ in USED) {
      old = LABEL_REQ
      LABEL_REQ = reserve_id()
      print "warning: " old " ==> " LABEL_REQ > "/dev/stderr"
  }
  else {
      USED[LABEL_REQ] = 1
  }
}


# Transform output

REQ == 1 {
  SORTIE_REQ = LABEL_REQ ".tex"
  print "\\rmsinput{" LABEL_REQ "}"

  REQ = 2
  next
}


# Go back to normal parsing

REQ == 2 && /^-- RMS-REQ$/ {
  REQ = 0
  next
}


# Output, either on stdout or in a dedicated requirement file

REQ == 0 {
  print $0
}


REQ == 2 {
  print $0 > SORTIE_REQ
}
