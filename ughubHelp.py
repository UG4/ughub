
# local imports
import ughubUtil
import ughubHelpContents


def GetHelpEntry(entry):
	return ughubUtil.GetFromDict(ughubHelpContents.content, entry)


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


def PrintCommands():
	try:
		for cmd in GetCommandsInHelp():
			print("  {0}".format(cmd))
	except LookupError:
		print("ERROR: Requested command list not found in help database")


# Prints help for the command specified in 'cmd'.
def PrintCommandHelp(cmdName):
	try:
		cmdDict = GetHelpEntry("commands.{0}".format(cmdName))
		print("Usage: ughub {0}".format(cmdDict["usage"]))
		print("")
		for line in cmdDict["description"].splitlines():
			print("  {0}".format(line))

		try:
			options = ughubUtil.GetFromDict(cmdDict, "options")
			print("")
			print("Valid options:")
			for opt in options:
				name = opt["name"]
				sep = ":"
				for line in opt["description"].splitlines():
					print("  {0:20}{1} {2}").format(name, sep, line)
					name = ""
					sep = " "
		except LookupError:
			pass

	except LookupError:
		print("ERROR: Requested command '{0}' not found in help database"
			  .format(cmdName))

# Prints help on how to use the help command and a list of all available commands
def PrintHelp():
	PrintCommandHelp("help")
	print("available commands:")
	PrintCommands()
