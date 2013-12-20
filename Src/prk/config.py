# Copyright or © or Copr. Guillaume Lemaître (2013)
#
# guillaume.lemaitre@gmail.com
#
# This software is a computer program whose purpose is to manage efficiently
# software configuration options, by considering on the same time
# command-line options, configuration file (project, user or system one) and
# default configuration.
#
# This software is governed by the CeCILL-C license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL-C
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
# knowledge of the CeCILL-C license and that you accept its terms.

"""Global management of configuration options

An option value can be set :
- as a command-line argument, in short and/or long form.
- in a static configuration file, either locally, in user's home directory,
  or in a systemwide directory.
- from a default value.
"""

import collections


Option = collections.namedtuple(["documentation",
                                 "short", "long",
                                 "domain", "name",
                                 "default",
                                 "validator",
                                 "value"])

# Nullable fields: documentation, short, long, domain, name, validator

# 'documentation' as it will be output on command line
# 'short' is 1-character long
# 'default' shall fit 'validator'
