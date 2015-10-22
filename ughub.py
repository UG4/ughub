#! /usr/bin/env python

# copyright 2015 Sebastian Reiter (G-CSC Frankfurt)

# standard library imports
import json
import os
import re
import subprocess
import sys

import ughubHelp
import ughubUtil

class NoRootDirectoryError(Exception) : pass
class InvalidSourceError(Exception) : pass

def GetRootDirectory():
	curDir = os.getcwd()
	while True:
		if os.path.isdir(os.path.join(curDir, ".ughub")):
			return curDir
		nextDir = os.path.dirname(curDir)
		if nextDir == curDir:
			raise NoRootDirectoryError()
		curDir = nextDir


def GetUGHubDirectory():
	return os.path.join(GetRootDirectory(), ".ughub")


def InitializeDirectory(args):
	force = any(opt in args for opt in ("-f", "--force"))

	if os.path.isdir(".ughub"):
		print("Directory has been initialized already. Aborting.")
	else:
		try:
			rootDir = GetRootDirectory()
			if not force:
				print("Warning: Found ughub root path at: {0}".format(rootDir))
				print("call 'ughub init -f' to force initialization in this path.")
				return

		except NoRootDirectoryError:
			pass

		# this is actually the expected case
		os.mkdir(".ughub")
		# create a dictionary that stores the default source-urls
		sources = 	[{	"name": "UG4",
						"url": "/home/sreiter/projects/ug4-packages",
						"branch": "master"}]

		with open(os.path.join(".ughub", "sources.json"), "w") as outfile:
			json.dump(sources, outfile, indent = 4)


def LoadSources(path):
	return json.loads(file(os.path.join(path, "sources.json")).read())


def ValidateSourceNames(sources):
	try:
		names = []
		for src in sources:
			srcName = src["name"]
			if srcName in names:
				raise InvalidSourceError("duplicate source name: {0}".format(srcName))
			else:
				names.append(srcName)
	except LookupError as e:
		raise InvalidSourceError("lookup of field '{0}' failed.".format(e.message))


def Refresh(args):
	ughubDir = GetUGHubDirectory()
	sources = LoadSources(ughubDir)
	ValidateSourceNames(sources)

	sourcesDir = os.path.join(ughubDir, "sources")
	if not os.path.isdir(sourcesDir):
		os.mkdir(sourcesDir)

	# check for each source whether it was already installed. if that's the case,
	# perform git pull on that directory. If not, perform git clone.
	try:
		for src in sources:
			name = src["name"]
			url = src["url"]
			branch = src["branch"]

			srcDir = os.path.join(sourcesDir, name)

			if not os.path.isdir(srcDir):
				print("Cloning source '{0}' from branch '{1}' at '{2}'".
					  format(name, branch, url))
				proc = subprocess.Popen(["git", "clone", "--branch", branch, url, name], cwd = sourcesDir)
				if proc.wait() != 0:
					raise InvalidSourceError("Couldn't check out source '{0}' from branch '{1}' at '{2}'"
											 .format(name, branch, url))
			else:
				print("Updating source '{0}' from branch '{1}' at '{2}'".
					  format(name, branch, url))
				proc = subprocess.Popen(["git", "pull"], cwd = srcDir)
				if proc.wait() != 0:
					raise InvalidSourceError("Couldn't pull from branch '{0}' at '{1}' for source '{2}'"
											 .format(branch, url, name))

	except LookupError as e:
		raise InvalidSourceError("lookup of field '{0}' failed.".format(e.message))



def ParseArguments(args):
	try:
		if args == None or len(args) == 0:
			ughubHelp.PrintUsage()
			return

		cmd = args[0]
		
		if cmd == "help":
			print("")
			if len(args) == 1:
				ughubHelp.PrintHelp()
			else:
				ughubHelp.PrintCommandHelp(args[1])
			print("")

		elif cmd == "init":
			InitializeDirectory(args[1:])

		elif cmd == "refresh":
			Refresh(args[1:])

		else:
			ughubHelp.PrintUsage()

	except NoRootDirectoryError:
		print(	"Couldn't find ughub root directory.\n"
				"Make sure to use 'ughub init' before executing other ughub commands")
	except InvalidSourceError as e:
		print("ERROR (invalid source) --- {0}".format(e.message))


ParseArguments(sys.argv[1:])
