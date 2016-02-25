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

content = {
	"usage": "type 'ughub help' for usage.",

	"commands": [
		{
			"name": "addsource",
			"usage": "addsource NAME URL [OPTIONS]",
			"description": "Adds a package-source (i.e. a git repository) from the given\n"
						   "URL. The source may later be referenced by NAME in other commands.\n"
						   "Valid repositories have to contain a 'package.json' file.\n"
						   "The specified URL has to be a valid git-url.",
			"options": [
				{
					"name": "-b [--branch] ARG",
					"description":	"The branch specified by ARG of the git repository at URL\n"
									"will be used as source. The default branch is 'master'."
				},
				# {
				# 	"name": "-r [--rank] ARG",
				# 	"description":	"The rank at which the source is added. If the same\n"
				# 			"package is contained in multiple sources, the one with the\n"
				# 			"lower rank is used by default."
				# }
			]
		},

		{
			"name": "genprojectfiles",
			"usage": "genprojectfiles TARGET [OPTIONS]",
			"description":	"Generates project-files for the given TARGET platform.\n"
							"NAME specifies the name of the root project.\n"
							"Possible TARGET's:\n"
							"  eclipse\n",
			"options": [
				{
					"name": "-n [--name] ARG",
					"description":	"Sets ARG as the name of the resulting project."
				},
				{
					"name": "-o [--overwrite]",
					"description":	"overwrites other project-files of the given TARGET."
				},
				{
					"name": "-d [--delete]",
					"description":	"removes project-files of the given TARGET."
				}
			]
		},

		{
			"name": "gitadd",
			"usage": "gitadd [PACKAGE_1 [PACKAGE_2 [...]]] [--- [GIT-OPTIONS]]",
			"description":	"If PACKAGE_1,...,PACKAGE_N is specified, files specified under GIT_OPTIONS\n"
							"are added in the local installations of PACKAGE_1,...,PACKAGE_N.\n"
							"If PACKAGE_1 was not specified, the operation is performed for all\n"
							"installed packages.\n"
							"'---' separates arguments to ughub's gitadd command from arguments\n"
							"that shall be passed to the underlying git-command itself. Please refer\n"
							"to git's documentation for available parameters."
		},

		{
			"name": "gitcommit",
			"usage": "gitcommit [PACKAGE_1 [PACKAGE_2 [...]]] [--- [GIT-OPTIONS]]",
			"description":	"If PACKAGE_1,...,PACKAGE_N is specified, changes of the working-copies\n"
							"of the local installations of PACKAGE_1,...,PACKAGE_N are commited.\n"
							"If PACKAGE_1 was not specified, the operation is performed for all\n"
							"installed packages.\n"
							"'---' separates arguments to ughub's gitcommit command from arguments\n"
							"that shall be passed to the underlying git-command itself. Please refer\n"
							"to git's documentation for available parameters."
		},

		{
			"name": "gitpull",
			"usage": "gitpull [PACKAGE_1 [PACKAGE_2 [...]]] [--- [GIT-OPTIONS]]",
			"description":	"If PACKAGE_1,...,PACKAGE_N is specified, changes from the origins\n"
							"of PACKAGE_1,...,PACKAGE_N are pulled to their local installations.\n"
							"Note that PACKAGE_1,...,PACKAGE_N has to be installed before one can\n"
							"pull new changes (see 'ughub help install').\n"
							"If PACKAGE_1 was not specified, changes from all remote repositories of\n"
							"all installed packages are pulled.\n"
							"'---' separates arguments to ughub's gitpull command from arguments\n"
							"that shall be passed to the underlying git-command itself. Please refer\n"
							"to git's documentation for available parameters."
		},

		{
			"name": "gitpush",
			"usage": "gitpush [PACKAGE_1 [PACKAGE_2 [...]]] [--- [GIT-OPTIONS]]",
			"description":	"If PACKAGE_1,...,PACKAGE_N is specified, changes from the local\n"
							"installations of PACKAGE_1,...,PACKAGE_N are pushed to their remote repositories.\n"
							"If PACKAGE_1 was not specified, changes from all installed packages are\n"
							"pushed to their remote repositories.\n"
							"'---' separates arguments to ughub's gitpush command from arguments\n"
							"that shall be passed to the underlying git-command itself. Please refer\n"
							"to git's documentation for available parameters."
		},

		{
			"name": "gitstatus",
			"usage": "gitstatus [PACKAGE_1 [PACKAGE_2 [...]]] [--- [GIT-OPTIONS]]",
			"description":	"If PACKAGE_1,...,PACKAGE_N is specified, the git-status messages of\n"
							"the local installations of PACKAGE_1,...,PACKAGE_N are displayed.\n"
							"If PACKAGE_1 was not specified, git-status messages of all\n"
							"installed packages are shown.\n"
							"'---' separates arguments to ughub's gitstatus command from arguments\n"
							"that shall be passed to the underlying git-command itself. Please refer\n"
							"to git's documentation for available parameters."
		},

		{
			"name": "help",
			"usage": "help [COMMAND]",
			"description": "Call help with one of the COMMANDs listed below to get help for that COMMAND.\n\n"
						   "'ughub' is a program to automatically download and install packages for\n"
						   "the UG4 simulation environment. It gathers package information like names,\n"
						   "urls, and dependencies to other packages from so called package-sources\n"
						   "(only referred to as 'sources' in the following).\n"
						   "In order to use 'ughub' one first has to initialize a (preferably empty)\n"
						   "directory for ughub usage by calling 'ughub init'. Executing any ughub command\n"
						   "will then always apply to the whole directory tree starting at the first\n"
						   "parent directory in which 'ughub init' was performed.\n"
						   "After initializing a directory one typically starts with installing a package\n"
						   "of interest by calling 'ughub install PACKAGE_NAME'. A list of all available\n"
						   "packages is displayed by the command 'ughub listpackages'.\n"
		},

		{
			"name": "init",
			"usage": "init [PATH] [OPTIONS]",
			"description": "Initializes a path for use with ughub. To this end a .ughub folder,\n"
						   "is created in which information on available and installed packages will\n"
						   "be stored. Through the optional parameter PATH one may specify a path\n"
						   "where the initialization shall be performed.\n"
						   "PATH may either be a relative path or an absolute path. If PATH is omitted,\n"
						   "initialization is performed in the current directory.",
			"options": [
				{
					"name": "-f [--force]",
					"description":	"Forces initialization, even if a parent directory of the specified\n"
									"PATH (or of the current directory, if PATH was omitted) already\n"
									"contains a '.ughub' subdirectory."
				}
			]
		},

		{
			"name": "install",
			"usage": "install PACKAGE_1 [PACKAGE_2 [PACKAGE_3 [...]]] [OPTIONS]",
			"description":	"Installs/updates the specified PACKAGES\n"
							"Dependend packages will also be automatically installed/updated.\n"
							"If an affected package exists already and if the requested branch\n"
							"does not match the current branch of that package, an error is raised\n"
							"unless the --force option is specified. The latter will automatically\n"
							"perform a checkout of the newly requested branch.",
			"options": [
				{
					"name": "-b [--branch] ARG",
					"description":	"The branch ARG of the associated PACKAGE repository will be installed/updated.\n"
									"If not specified, the default branch of the package is used."
				},
				{
					"name": "-d [--dry]",
					"description":	"Performs a dry run, i.e., prints all dependencies without\n"
									"installing any files."
				},
				{
					"name": "-f [--force]",
					"description":	"Ignores branch conflicts between a requested and a present branch\n"
									"for existing packages by simply checking out the requested branch."
				},
				{
					"name": "-s [--source] ARG",
					"description":	"Installs the PACKAGE from the source with name ARG."
				},
			]
		},

		{
			"name": "installall",
			"usage": "installall [OPTIONS]",
			"description":	"Installs/updates all packages (for detailed package list run 'ughub list')\n"
							"Installs all available packages as listed in the current package list.\n"
							"If an affected package exists already and if the requested branch\n"
							"does not match the current branch of that package, an error is raised\n"
							"unless the --force option is specified. The latter will automatically\n"
							"perform a checkout of the newly requested branch.",
			"options": [
				{
					"name": "-b [--branch] ARG",
					"description":	"For each package the branch ARG of the associated package repository will\n"
									"be installed/updated. If not specified, the default branch is used."
				},
				{
					"name": "-d [--dry]",
					"description":	"Performs a dry run, i.e., prints all dependencies without\n"
									"installing any files."
				},
				{
					"name": "-f [--force]",
					"description":	"Ignores branch conflicts between a requested and a present branch\n"
									"for existing packages by simply checking out the requested branch."
				},
				{
					"name": "-s [--source] ARG",
					"description":	"For each package installs the package from the source with name ARG."
				},
			]
		},


		{
			"name": "listpackages (list)",
			"usage": "list [CATEGORY_1 [CATEGORY_2 [...]]] [OPTIONS]",
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
					"name": "-n [--notinstalled]",
					"description":	"Only packages which are not installed are listed."
				}
			]
		},

		{
			"name": "listsources",
			"usage": "listsources",
			"description": "Lists all available sources ordered from low rank (top) to high rank (bottom)."
		},

		{
			"name": "packageinfo",
			"usage": "packageinfo NAME [OPTIONS]",
			"description": "Lists detailed information of all available packages with the given NAME.",
			"options": [
				{
					"name": "-s [--short]",
					"description":	"Prints a short overview of the package info"
				},
			]
		},

		# {
		# 	"name": "ranksource",
		# 	"usage": "ranksource NAME RANK",
		# 	"description":	"Ranks the source with the given NAME at the given RANK. If the same\n"
		# 					"package is contained in multiple sources, the one with the lower rank\n"
		# 					"is used by default."
		# },

		# {
		# 	"name": "removesource",
		# 	"usage": "removesource NAME",
		# 	"description":	"Removes the source with the given NAME."
		# },

		{
			"name": "repair",
			"usage": "repair",
			"description":	"Attempts to repair a broken ughub directory by performing\n"
							"the following:\n"
							"- Generating a 'CMakeLists.txt' file in ughub's root directory.\n"
							"- Restoring the default '.ughub/sources.json' source list (if necessary)."
		},

		{
			"name": "updatesources",
			"usage": "updatesources",
			"description":	"Pulls package information for all sources from their remote repositories."
		},

		{
			"name": "version",
			"usage": "version",
			"description": "Prints the version number of ughub."
		},

	]
}
