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
			"shortdescription": "Adds a ughub package source.",
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
			"shortdescription": "Generates project files for UG for different targets.",
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
			"name": "git",
			"usage": "git COMMAND [GIT-OPTIONS] [--- [PACKAGE_1 [PACKAGE_2 [...]]]]",
			"description":	"Executes 'git COMMAND GIT-OPTIONS' on installed packages.\n"
							"COMMAND has to be a valid git-command. See 'git help' for valid git-commands.\n"
							"If PACKAGE_1,...,PACKAGE_N is specified after the separator '---' then\n"
							"'git COMMAND GIT-OPTIONS' will be executed on the specified packages only.\n"
							"If the separator or PACKAGE_1 was not specified, then the operation\n"
							"is performed for all installed packages.\n",
			"shortdescription": "Allows executing git commands on installed packages."
		},

		{
			"name": "help",
			"usage": "help [--commands | COMMAND [OPTIONS] ]",
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
						   "packages is displayed by the command 'ughub listpackages'.\n",
			"shortdescription": "Prints help about ughub commands",
			"options": [
				{
					"name": "--commands",
					"description":	"Prints all available commands, separated by a space."
				},
				{
					"name": "--shortdescription",
					"description":	"Only prints a short description of the command."
				},
			]
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
			"shortdescription": "Initializes a path for usage with ughub.",
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
							"Dependend packages will also be automatically installed/updated unless\n"
							"the options '--nodeps' or '--noupdate' are specified.\n"
							"\n"
							"If an affected package exists already and if the requested branch\n"
							"does not match the current branch of that package, an error is raised\n"
							"unless the --ignore or --resolve option is specified. The first will\n"
							"keep the old branch/repository while the second one will automatically\n"
							"perform a checkout of the newly requested branch/repository.",
			"shortdescription": "Installs or updates the specified packages.",
			"options": [
				{
					"name": "-b [--branch] ARG",
					"description":	"The branch ARG of the associated PACKAGE repository will be\n"
									"installed/updated. If not specified, the default branch of\n"
									"the package is used."
				},
				{
					"name": "-d [--dry]",
					"description":	"Performs a dry run, i.e., prints all dependencies without\n"
									"installing any files."
				},
				{
					"name": "-i [--ignore]",
					"description":	"Ignores conflicts (e.g. branch or remote conflicts) and performs the requested\n"
									"installation/update without changing any conflicting branches or repositories.\n"
									"Please note that this may lead to build-problems later on."
				},
				{
					"name": "--nodeps",
					"description":	"Won't install or update packages on which the installed one depends.\n"
									"Useful if one only wants to inspect a specific package.\n"
									"Please note that this may lead to build-problems later on."
				},
				{
					"name": "--noupdate",
					"description":	"Disables autmatic updates of installed packages which are\n"
									"contained in the dependency list of the installed package.\n"
									"Please note that this may lead to build-problems later on."
				},
				{
					"name": "-r [--resolve] ARG",
					"description":	"Resolves conflicts (e.g. branch or remote conflicts) by adjusting\n"
									"the local repository accordingly. Be sure to commit and push any\n"
									"changes before executing 'ughub install' with this option."
				},
				{
					"name": "-s [--source] ARG",
					"description":	"Installs the PACKAGE from the source with name ARG."
				},
			]
		},

		{
			"name": "installall",
			"usage": "installall [CATEGORY_1 [CATEGORY_2 [...]]] [OPTIONS]",
			"description":	"Installs all available packages as listed by the correponding call to 'ughub list'\n"
							"plus packages which are contained in the dependecy lists of considered packages\n"
							"(unless the --nodeps option is specified). Considered packages which already are\n"
							"installed are updated automatically (unless the --noupdate option is specified).\n"
							"\n"
							"Through CATEGORY_1,...,CATEGORY_N one can limit the list of packages that\n"
						   	"will be installed/updated to packages which belong to at least one of those categories.\n"
							"Using --matchall, --installed, --notinstalled further limits the list of\n"
							"considered packages accordingly.\n"
							"\n"
							"If an affected package exists already and if the requested branch\n"
							"does not match the current branch of that package, an error is raised\n"
							"unless the --ignore or --resolve option is specified. The first will\n"
							"keep the old branch/repository while the second one will automatically\n"
							"perform a checkout of the newly requested branch/repository.",
			"shortdescription": "Installs/updates all available packages.",
			"options": [
				{
					"name": "-a [--matchall]",
					"description":	"Only packages which match all specified categories are installed/updated."
				},
				{
					"name": "-b [--branch] ARG",
					"description":	"For each package the branch ARG of the associated PACKAGE repository will\n"
									"be installed/updated. If not specified, the default branch is used."
				},
				{
					"name": "-d [--dry]",
					"description":	"Performs a dry run, i.e., prints all dependencies without\n"
									"installing any files."
				},
				{
					"name": "-i [--ignore]",
					"description":	"Ignores conflicts (e.g. branch or remote conflicts) and performs the requested\n"
									"installation/update without changing any conflicting branches or repositories.\n"
									"Please note that this may lead to build-problems later on."
				},
				{
					"name": "--nodeps",
					"description":	"Won't install or update packages on which the installed one depends.\n"
									"Useful if one only wants to inspect a specific package.\n"
									"Please note that this may lead to build-problems later on."
				},
				{
					"name": "--noupdate",
					"description":	"Disables autmatic updates of installed packages which are\n"
									"contained in the dependency list of the installed package.\n"
									"Please note that this may lead to build-problems later on."
				},
				{
					"name": "-i [--installed]",
					"description":	"Only already installed packages are updated."
				},
				{
					"name": "-n [--notinstalled]",
					"description":	"Only packages which are not already installed are installed."
				},
				{
					"name": "-r [--resolve] ARG",
					"description":	"Resolves conflicts (e.g. branch or remote conflicts) by adjusting the local\n"
									"repository accordingly. Be sure to commit and push any changes before executing\n"
									"'ughub install' with this option."
				},
				{
					"name": "-s [--source] ARG",
					"description":	"Installs packages from the specified source ARG only."
				},
			]
		},


		{
			"name": ["listpackages", "list"],
			"usage": "list [CATEGORY_1 [CATEGORY_2 [...]]] [OPTIONS]",
			"description": "Lists all available packages. Through CATEGORY_1,...,CATEGORY_N one\n"
						   "can limit the output to packages which belong to those categories.",
			"shortdescription": "Lists available/installed packages.",
			"options": [
				{
					"name": "-a [--matchall]",
					"description":	"Only packages which match all specified categories are listed."
				},
				{
					"name": "--namesonly",
					"description":	"Only print package names, space separated."
				},

				{
					"name": "-i [--installed]",
					"description":	"Only installed packages are listed."
				},

				{
					"name": "-n [--notinstalled]",
					"description":	"Only packages which are not installed are listed."
				},

				{
					"name": "-s [--source] ARG",
					"description":	"Lists packages from the specified source only."
				},
			]
		},

		{
			"name": "log",
			"usage": "log [OPTIONS] [PACKAGE_1 [PACKAGE_2 [...]]]",
			"description": "Executes 'git log' with a special formatting on the packages\n"
						   " PACKAGE_1, ..., PACKAGE_N. If no package was specified, then\n"
						   "'git log' will be executed for all installed packages.",
			"shortdescription": "View the git log of installed, specified packages.",
			"options": [
				{
					"name": "-n ARG",
					"description":	"Prints only the last 'ARG' log entries for each package.\n"
									"ARG has to be an integer number greater than 0. Default is 10."
				},
			]
		},

		{
			"name": "listsources",
			"usage": "listsources",
			"shortdescription": "Lists available sources.",
			"description": "Lists all available sources ordered from low rank (top) to high rank (bottom)."
		},

		{
			"name": "packageinfo",
			"usage": "packageinfo NAME [OPTIONS]",
			"shortdescription": "Lists information of all packages with the given name.",
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
			"shortdescription": "Attempts to repair a broken ughub directory.",
			"description":	"Attempts to repair a broken ughub directory by performing\n"
							"the following:\n"
							"- Generating a 'CMakeLists.txt' file in ughub's root directory.\n"
							"- Restoring the default '.ughub/sources.json' source list (if necessary)."
		},

		{
			"name": "get-completions",
			"usage": "ughub get-completions TYPEDSTRING",
			"shortdescription": "Returns auto complete suggestions.",
			"description":	"Returns auto complete suggestions based on TYPEDSTRING, the symbols the user typed until now.\n"
							"This uses information such as available commands, installed packages, usable options..."
		},

		{
			"name": "updatesources",
			"usage": "updatesources",
			"shortdescription": "Updates package information for all sources.",
			"description":	"Pulls package information for all sources from their remote repositories."
		},

		{
			"name": "version",
			"usage": "version",
			"shortdescription": "Prints the version number of ughub.",
			"description": "Prints the version number of ughub."
		},

	]
}
