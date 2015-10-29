################################################################################
# Copyright 2015 Sebastian Reiter (G-CSC, Universität Frankfurt am Main)
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
# ARE DISCLAIMED. IN NO EVENT SHALL G-CSC FRANKFURT BE LIABLE FOR ANY
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
						   "Valid repositories have to contain a 'package.json' file,\n"
						   "and optionally 'build_scripts' and 'licenses' folders in their\n"
						   "top-level directory. The specified URL has to be a valid git-url.",
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
			"name": "help",
			"usage": "help [COMMAND]",
			"description": "Shows the help for the given COMMAND, or a list of\n"
						   "all available commands if no COMMAND was specified."
		},

		{
			"name": "init",
			"usage": "init [OPTIONS]",
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
			"usage": "install PACKAGE [OPTIONS]",
			"description":	"Installs/updates the specified PACKAGE\n"
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

		{
			"name": "packages",
			"usage": "packages [CATEGORY_1 [CATEGORY_2 ...]] [OPTIONS]",
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
			"name": "sources",
			"usage": "sources",
			"description": "Lists all available sources ordered from low rank (top) to high rank (bottom)."
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
