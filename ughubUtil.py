################################################################################
# Copyright 2015 G-CSC, Goethe University Frankfurt
# Author: Sebastian Reiter <sreiter@gcsc.uni-frankfurt.de>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Goethe-Center for Scientific Computing nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
################################################################################

import json
import sys

class NestedTableEntryNotFoundError(LookupError) : pass
class NestedTableTraversalError(Exception) : pass

# Traverses a directory or a list of directories recursively using the specified key.
# key has to be a string. You may request a nested key by separating
# nested keys with '.'
# Instead of a dictionary one may also pass a list of dictionaries. Each
# dictionary in that list has to contain a "name" key. If the value of
# that "name" key matches the current sub-key, that dictionary is used for the
# lookup of the next nested key or is simply returned if no more nested keys were specified.
#
# throws a NestedTableEntryNotFoundError if the requested entry was not found
# throws a NestedTableTraversalError if the nested table could not be traversed
def get_from_nested_table(nested_table, key):
    d = nested_table
    try:
        key_path = ""
        for k in key.split("."):
            if type(d) == dict:
                d = d[k]
            elif type(d) == list:
                got_one = False
                for e in d:
                #    e has to be a dict again
                    name = e["name"]
                    if (type(name) == str and name == k) or (type(name) == list and k in name):
                        d = e
                        got_one = True
                        break
                if not got_one:
                    raise NestedTableEntryNotFoundError("key '{0}' in table '{1}'".format(k, key_path))
            else:
                raise NestedTableTraversalError(key_path)
            key_path = key_path.join((".", k))
    except LookupError as e:
        raise NestedTableEntryNotFoundError(e)

    return d

def nested_table_to_string(table):
    return json.dumps(table, indent=4, sort_keys=True)

# returns True if one of the specified options was found
def has_commandline_option(args, options):
    return any(opt in args for opt in options)

# returns None if no option was found
def get_commandline_option_value(args, options):
    for i in range(len(args)):
        if args[i] in options:
            if i + 1 < len(args):
                return args[i+1]
    return None

# returns a new list that contains all entries from args which do not start with a '-'
def remove_options(args):
    filtered_args = []
    for arg in args:
        if len(arg) > 0 and arg[0] != "-":
            filtered_args.append(arg)
    return filtered_args

def write(string):
    sys.stdout.write(string)
    sys.stdout.flush()