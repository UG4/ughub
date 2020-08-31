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

import ughubUtil
import ughubHelpContents

class MalformedHelpContentsError(Exception) : pass

def GetHelpEntry(entry):
	return ughubUtil.GetFromNestedTable(ughubHelpContents.content, entry)


def GetCommandsInHelp():
	try:
		d = GetHelpEntry("commands")
		out = []

		if type(d) == list:
			for e in d:
				name = e["name"]
				if type(name) == str:
					out.append(name)
				elif type(name) == list and len(name) > 0:
					s = name[0]
					for i in range(1, len(name)):
						s = s + ", " + name[i]
					out.append(s)
		else:
			raise MalformedHelpContentsError("'commands' entry has to be a list")
	except ughubUtil.NestedTableEntryNotFoundError as e:
		raise MalformedHelpContentsError("'commands' list required in help contents")

	return out

def IsCommandInHelp(command):
	try:
		d = GetHelpEntry("commands")
		if type(d) == list:
			for e in d:
				name = e["name"]
				if type(name) == str and name == command:
					return True
				elif type(name) == list and command in name:
					return True						
		else:
			raise MalformedHelpContentsError("'commands' entry has to be a list")
	except ughubUtil.NestedTableEntryNotFoundError as e:
		raise MalformedHelpContentsError("'commands' list required in help contents")
	return False

def PrintUsage():
	try:
		print(GetHelpEntry("usage"))
	except ughubUtil.NestedTableEntryNotFoundError as e:
		raise MalformedHelpContentsError(e)


def PrintCommands():
	for cmd in GetCommandsInHelp():
		print("  {0}".format(cmd))

def PrintCommandNames():
	result = ""
	for cmd in GetCommandsInHelp():		
		for c in cmd.split(","):
			result += c.strip() + "\n"			
	print(result[:-1], end ="")

# Prints help for the command specified in 'cmd'.
def PrintCommandHelp(cmdName, args=[]):

	shortdesc = ughubUtil.HasCommandlineOption(args, ("--shortdescription",))

	try:
		cmdDict = GetHelpEntry("commands.{0}".format(cmdName))

	except ughubUtil.NestedTableEntryNotFoundError:
		raise MalformedHelpContentsError("Requested command '{0}' not found in help database"
			  							 .format(cmdName))

	if shortdesc:
		if "shortdescription" in cmdDict:
			print(cmdDict["shortdescription"], end="")
		return

	print("Usage: ughub {0}".format(cmdDict["usage"]))
	print("")
	for line in cmdDict["description"].splitlines():
		print("  {0}".format(line))

	try:
		options = ughubUtil.GetFromNestedTable(cmdDict, "options")
	except ughubUtil.NestedTableEntryNotFoundError:
		pass

	print("")
	print("Valid options:")
	for opt in options:
		name = opt["name"]
		sep = ":"
		for line in opt["description"].splitlines():
			print("  {0:20}{1} {2}".format(name, sep, line))
			name = ""
			sep = " "
	

	

def GetOptionStringsForCommand(cmdName):
	result = ""
	try:
		cmdDict = GetHelpEntry("commands.{0}".format(cmdName))
		
		try:
			options = ughubUtil.GetFromNestedTable(cmdDict, "options")
			
			for opt in options:
				optionstrings = opt["name"]

				# filter out [ ]			
				optionstrings = optionstrings.replace("[", "").replace("]", "")

				# split
				optionstrings = optionstrings.split(" ")

				# which of those start with - or --?
				optionstrings = list(filter(lambda s: s.startswith('-') or s.startswith('--'), optionstrings))

				for s in optionstrings:
					result += s + "\n"
				
		except ughubUtil.NestedTableEntryNotFoundError:
			pass

	except ughubUtil.NestedTableEntryNotFoundError:
		raise MalformedHelpContentsError("Requested command '{0}' not found in help database"
			  							 .format(cmdName))

	return result[:-1]

# Prints help on how to use the help command and a list of all available commands
def PrintHelp():
	PrintCommandHelp("help")
	print("")
	print("available commands:")
	PrintCommands()
