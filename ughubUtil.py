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
