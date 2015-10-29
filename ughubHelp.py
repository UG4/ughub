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
				out.append(e["name"])
		else:
			raise MalformedHelpContentsError("'commands' entry has to be a list")
	except ughubUtil.NestedTableEntryNotFoundError as e:
		raise MalformedHelpContentsError("'commands' list required in help contents")

	return out


def PrintUsage():
	try:
		print(GetHelpEntry("usage"))
	except ughubUtil.NestedTableEntryNotFoundError as e:
		raise MalformedHelpContentsError(e.message)


def PrintCommands():
	for cmd in GetCommandsInHelp():
		print("  {0}".format(cmd))

# Prints help for the command specified in 'cmd'.
def PrintCommandHelp(cmdName):
	try:
		cmdDict = GetHelpEntry("commands.{0}".format(cmdName))
		print("Usage: ughub {0}".format(cmdDict["usage"]))
		print("")
		for line in cmdDict["description"].splitlines():
			print("  {0}".format(line))

		try:
			options = ughubUtil.GetFromNestedTable(cmdDict, "options")
			print("")
			print("Valid options:")
			for opt in options:
				name = opt["name"]
				sep = ":"
				for line in opt["description"].splitlines():
					print("  {0:20}{1} {2}").format(name, sep, line)
					name = ""
					sep = " "
		except ughubUtil.NestedTableEntryNotFoundError:
			pass

	except ughubUtil.NestedTableEntryNotFoundError:
		raise MalformedHelpContentsError("Requested command '{0}' not found in help database"
			  							 .format(cmdName))

# Prints help on how to use the help command and a list of all available commands
def PrintHelp():
	PrintCommandHelp("help")
	print("")
	print("available commands:")
	PrintCommands()
