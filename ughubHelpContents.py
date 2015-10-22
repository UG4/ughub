
# copyright 2015 Sebastian Reiter (G-CSC Frankfurt)

content = {
	"usage": "type 'ughub help' for usage.",

	"commands": [
		{
			"name": "addsource",
			"usage": "addsource NAME URL",
			"description": "Adds a package-source (i.e. a git repository) from the given\n"
						   "URL. The package may later be referenced by NAME in other commands.\n"
						   "Valid repositories have to contain a 'package.json' file,\n"
						   "and optionally 'build_scripts' and 'licenses' folders in their\n"
						   "top-level directory. The specified URL has to be a valid git-url.",
			"options": [
				{
					"name": "-b [--branch] ARG",
					"description":	"The branch specified by ARG of the git repository at URL\n"
									"will be used as source. The default branch is 'master'."
				},
				{
					"name": "-r [--rank] ARG",
					"description":	"The rank at which the source is added. If the same\n"
							"package is contained in multiple sources, the one with the\n"
							"lower rank is used by default."
				}
			]
		},

		{
			"name": "help",
			"usage": "help [COMMAND]",
			"description": "Shows the help for the given COMMAND, or a list of\n"
						   "all available commands if no COMMAND was specified."
		},

		{
			"name": "init",
			"usage": "init",
			"description": "Initializes a path for use with ughub. To this end a .ughub folder,\n"
						   "is created in which information on available and installed packages will\n"
						   "be stored. It also creates a CMakeLists.txt file, which can later be used\n"
						   "to build ug and all installed plugins.",
			"options": [
				{
					"name": "-f [--force]",
					"description":	"Forces initialization in the current directory, even if a parent\n"
									"directory already contains a '.ughub' subdirectory."
				}
			]
		},

		{
			"name": "install",
			"usage": "install PACKAGE",
			"description":	"Installs the specified PACKAGE",
			"options": [
				{
					"name": "-b [--branch] ARG",
					"description":	"The branch ARG of the associated PACKAGE repository will be installed.\n"
									"If not specified, the default branch of the package is used\n"
									"(see 'setdefaultbranch')."
				},
				{
					"name": "-s [--source] ARG",
					"description":	"Installs the PACKAGE from the source with name ARG."
				}
			]
		},

		{
			"name": "packages",
			"usage": "packages [CATEGORY_1 [CATEGORY_2 ...]]",
			"description": "Lists all available packages. Through CATEGORY_1,...,CATEGORY_N one\n"
						   "can limit the output to packages which belong to those categories.",
			"options": [
				{
					"name": "-a [--matchall]",
					"description":	"Only packages which match all specified categories are listed."
				},

				{
					"name": "-i [--installed]",
					"description":	"Only installed packages are listed."
				},

				{
					"name": "-n [--installed]",
					"description":	"Only packages which are not installed are listed."
				}
			]
		},

		{
			"name": "ranksource",
			"usage": "ranksource NAME RANK",
			"description":	"Ranks the source with the given NAME at the given RANK. If the same\n"
							"package is contained in multiple sources, the one with the lower rank\n"
							"is used by default."
		},

		{
			"name": "refresh",
			"usage": "refresh",
			"description":	"Pulls package information for all sources from their remote repositories."
		},

		{
			"name": "removesource",
			"usage": "removesource NAME",
			"description":	"Removes the source with the given NAME."
		},

		{
			"name": "setdefaultbranch",
			"usage": "setdefaultbranch BRANCH",
			"description": 	"Sets BRANCH as the default branch used during 'install'"
		},

		{
			"name": "sources",
			"usage": "sources",
			"description": "Lists all available sources ordered from low rank (top) to high rank (bottom)."
		},

	]
}
