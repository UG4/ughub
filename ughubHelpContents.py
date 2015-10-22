
# copyright 2015 Sebastian Reiter (G-CSC Frankfurt)

content = {
	"usage": "type 'ughub help' for usage.",

	"commands": [
		{
			"name": "addsource",
			"usage": "addsource URL [BRANCH]",
			"description": "Adds a package-source (i.e. a git repository) from the given\n"
						   "URL. Such repositories have to contain a 'package.json' file,\n"
						   "and optionally 'build_scripts' and 'licenses' folders in their top-level\n"
						   "directory. The specified url has to be a valid git-url. A branch from\n"
						   "which to retrieve the repository may optionally be specified."
		},

		{
			"name": "help",
			"usage": "help [COMMAND]",
			"description": "Shows the help for the given COMMAND, or a list of all\n"
						   "available commands, if no COMMAND was specified."
		},

		{
			"name": "init",
			"usage": "init [BRANCH]",
			"description": "Initializes an empty path for use with ughub. To this end a .ughub folder,\n"
						   "is created in which information on available and installed packets will\n"
						   "be stored. It furthermore downloads the specified BRANCH (default: 'master')\n"
						   "of 'ugcore' and creates a CMakeLists.txt file, which can then be used to\n"
						   "build ug and all installed plugins."
		},

		{
			"name": "list",
			"usage": "list [CATEGORY_1 [CATEGORY_2 ...]]",
			"description": "Lists all available packets. Through CATEGORY_1,...,CATEGORY_N one\n"
						   "can limit the output to packets which belong to those categories.",
			"options": [
				{
					"name": "-c [--categories]",
					"description":	"Prints a list of all available categories\n"
									"and this is a second line"
				}
			]
		},

	]
}
