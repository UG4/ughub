################################################################################
# Copyright 2015 Sebastian Reiter (G-CSC, University Frankfurt am Main)
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

class NestedTableEntryNotFoundError(LookupError) : pass
class NestedTableTraversalError(Exception) : pass

# Traverses a directory or a list of directories recursively using the specified key.
# key has to be a string. You may request a nested key by separating
# nested keys with '.'
# Instead of a dictionary one may also pass a list of dictionaries. Each
# dictionary in that list has to contain a "name" key. If the value of
# that "name" key matches the current sub-key, that dictionary is used for the
# lookup of the next nested key or is simply returned if no more nested keys were specified..
#
# throws a NestedTableEntryNotFoundError if the requested entry was not found
# throws a NestedTableTraversalError if the nested table could not be traversed
def GetFromNestedTable(nestedTable, key):
	d = nestedTable
	try:
		keyPath = ""
		for k in key.split("."):
			if type(d) == dict:
				d = d[k]
			elif type(d) == list:
				gotOne = False
				for e in d:
				#	e has to be a dict again
					if e["name"] == k:
						d = e
						gotOne = True
						break
				if gotOne == False:
					raise NestedTableEntryNotFoundError("key '{0}' in table '{1}'".format(k, keyPath))
					break
			else:
				raise NestedTableTraversalError(keyPath)
			keyPath = keyPath.join((".", k))
	except LookupError as e:
		raise NestedTableEntryNotFoundError(e.message)

	return d


def NestedTableToString(table):
	return json.dumps(table, indent=4, sort_keys=True)


# returns True if one of the specified options was found
def HasCommandlineOption(args, options):
	return any(opt in args for opt in options)


# returns None if the no option was found
def GetCommandlineOptionValue(args, options):
	for i in range(0, len(args)):
		if args[i] in options:
			if i + 1 < len(args):
				return args[i+1]
	return None

# returns a new list that contains all entries from args which do not start with a '-'
def RemoveOptions(args):
	filteredArgs = []
	for a in args:
		if len(a) > 0 and a[0] != "-":
			filteredArgs.append(a)
	return filteredArgs
