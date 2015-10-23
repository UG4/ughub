
# local imports
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
