
# Traverses a directory or list using the specified key.
# key has to be a string. You may request a nested key by separating
# nested keys with '.'
# Instead of a dictionary one may also pass a list of dictionaries. Each
# dictionary in that list has to contain a "name" key. If the value of
# that "name" key matches the current key, that dictionary is used for the
# lookup of the next key.
#
# todo: throw more meaningful errors
def GetFromDict(dictionary, key):
	d = dictionary
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
				raise LookupError()
				break
		else:
			raise LookupError()
	return d

