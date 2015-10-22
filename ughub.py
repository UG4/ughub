#! /usr/bin/env python

# standard library imports
import json
import os
import re
import sys

# local imports
import ughubHelp


# Traverses a directory or list using the specified key.
# key has to be a string. You may request a nested key by separating
# nested keys with '.'
# Instead of a dictionary one may also pass a list of dictionaries. Each
# dictionary in that list has to contain a "name" key. If the value of
# that "name" key matches the current key, that dictionary is used for the
# lookup of the next key.
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


def GetHelpEntry(entry):
	return GetFromDict(ughubHelp.content, entry)


def GetCommandsInHelp():
	d = GetHelpEntry("commands")
	out = []

	if type(d) == list:
		for e in d:
			out.append(e["name"])
	else:
		raise LookupError()
	return out


def PrintUsage():
	try:
		print(GetHelpEntry("usage"))
	except LookupError:
		print("ERROR: Requested help-key not found: usage")


def PrintCommandHelp(cmdName):
	try:
		cmdDict = GetHelpEntry("commands.{0}".format(cmdName))
		print("Usage: ughub {0}".format(cmdDict["usage"]))
		print("")
		for line in cmdDict["description"].splitlines():
			print("  {0}".format(line))
		print("")

		try:
			options = GetFromDict(cmdDict, "options")
			print("Valid options:")
			for opt in options:
				name = opt["name"]
				sep = ":"
				for line in opt["description"].splitlines():
					print("  {0:20}{1} {2}").format(name, sep, line)
					name = ""
					sep = " "
			print("")
		except LookupError:
			pass

	except LookupError:
		print("ERROR: Requested command '{0}' not found in help database"
			  .format(cmdName))


def PrintCommands():
	try:
		for cmd in GetCommandsInHelp():
			print("  {0}".format(cmd))
	except LookupError:
		print("ERROR: Requested command list not found in help database")


def PrintHelp(args):
	print("")
	if args == None or len(args) == 0:
		PrintCommandHelp("help")
		print("available commands:")
		PrintCommands()
		print("")
	else:
		PrintCommandHelp(args[0])


def ParseArguments(args):
	if args == None or len(args) == 0:
		PrintUsage()
		return

	cmd = args[0]
	
	if cmd == "help":
		PrintHelp(args[1:])

	else:
		PrintUsage()

ParseArguments(sys.argv[1:])
