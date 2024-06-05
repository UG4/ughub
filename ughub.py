#! /usr/bin/env python

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

# v1.0.1:	Supporting 'include' statement in packages.json files.
# v1.0.2:	Various improvements. Most notably auto-detection of outdated remotes
#			and full support for python 2.6, 2.7, and 3. Furthermore,
#			project-file-generation for Eclipse has been added.
g_ughubVersionString = "1.0.2"

import collections
import json
import os
import re
import subprocess
import sys

import ughubHelp
import ughubProjectFileGenerator
import ughubUtil

class ArgumentError(Exception) : pass
class DependencyError(Exception) : pass
class InvalidSourceError(Exception) : pass
class InvalidPackageError(Exception) : pass
class NoRootDirectoryError(Exception) : pass
class TargetError(Exception) : pass
class TransactionError(Exception): pass


PackageBranchPair = collections.namedtuple("PackageBranchPair", "package branch")

# returns True if the first version number is smaller or equal to the second, False if not.
def CompareVersions(vstr0, vstr1):
	nums0 = vstr0.split(".")
	nums1 = vstr1.split(".")
	for v0, v1 in zip(nums0, nums1):
		if v0 > v1:
			return False
	return True


# This text is shown when the application terminates. Methods may append
# warning and error messages to this string.
# Use AppendToExitText to append your messages
g_exitText = ""
def AppendToExitText(text):
	global g_exitText
	g_exitText = g_exitText + text


def GetRootDirectory(path=None):
	curDir = path or os.getcwd()
	while True:
		if os.path.isdir(os.path.join(curDir, ".ughub")):
			return curDir
		nextDir = os.path.dirname(curDir)
		if nextDir == curDir:
			raise NoRootDirectoryError()
		curDir = nextDir


def GetUGHubDirectory(path=None):
	return os.path.join(GetRootDirectory(path), ".ughub")


def GenerateDefaultSourceFile(path=None):
	targetPath = GetUGHubDirectory(path)

	sources = 	[{	"name": "github-ug4",
					"url": "https://github.com/UG4/ug4-packages.git",
					"branch": "master"}]

	WriteSources(sources, targetPath)


def GenerateCMakeLists(path=None):
	filename = os.path.join(GetRootDirectory(path), "CMakeLists.txt")
	print("Generating '{0}'".format(filename))
	f = open(filename, "w")
	f.write("# WARNING: PLEASE DO NOT CHANGE THIS FILE (any changes may be lost)\n")
	f.write("# This file was automatically generated and may be overwritten without notice.\n")
	f.write("\n")
	f.write("cmake_minimum_required(VERSION 2.8.12)\n")
	f.write("project(UG4)\n")
	f.write("if(IS_DIRECTORY ${CMAKE_SOURCE_DIR}/ugcore)\n")
	f.write("	add_subdirectory(ugcore)\n")
	f.write("else()\n")
	f.write("	message(FATAL_ERROR \"Please install the 'ugcore' package using 'ughub install ugcore'.\")\n")
	f.write("endif()\n")
	f.close()


def InitializeDirectory(args):
	force = ughubUtil.HasCommandlineOption(args, ("-f", "--force"))

	rootPath = os.getcwd()
	if len(args) > 0 and args[0][0] != '-':
		if os.path.isabs(args[0]):
			rootPath = args[0]
		else:
			rootPath = os.path.join(rootPath, args[0])

	ughubPath = os.path.normpath(os.path.join(rootPath, ".ughub"))
	if os.path.isdir(ughubPath):
		if os.path.isfile(os.path.join(ughubPath, "sources.json")):
			print("Directory '{0}' has been initialized already.".format(ughubPath))
			return
	else:
		try:
			existingRootDir = GetRootDirectory(ughubPath)
			if not force:
				print("Warning: Found ughub root directory at: {0}".format(existingRootDir))
				print("call 'ughub init -f' to force initialization in this path.")
				return

		except NoRootDirectoryError:
			pass

		# this is actually the expected case
		os.makedirs(ughubPath)

	GenerateDefaultSourceFile(ughubPath)
	UpdateSources([], ughubPath)
	GenerateCMakeLists(rootPath)
	print("initialized ughub directory at '{0}'".format(rootPath))


def Repair(args):
	try:
		LoadSources()
	except InvalidSourceError:
		print("Restoring default 'sources.json' file.")
		GenerateDefaultSourceFile()
		UpdateSources([])

	GenerateCMakeLists()


def WriteSources(sources, path=None):
	path = GetUGHubDirectory(path)
	with open(os.path.join(path, "sources.json"), "w") as outfile:
		json.dump(sources, outfile, indent = 4)


def PrintSource(s):
	print("  {0:8}: '{1}'".format("name", s["name"]))
	print("  {0:8}: '{1}'".format("branch", s["branch"]))
	print("  {0:8}: '{1}'".format("url", s["url"]))


def AddSource(args):
	if len(args) < 2 or args[0][0] == "-" or args[1][0] == "-":
		print("ERROR in addsource: Invalid arguments specified. See 'ughub help addsource'.")
		return

	name		= args[0]
	url			= args[1]
	sources 	= LoadSources()
	branch		= ughubUtil.GetCommandlineOptionValue(args, ("-b", "--branch")) or "master"
	newSource	= {	"name": name,
					"url": url,
					"branch": branch}

	for s in sources:
		if s["name"] == name:
			print("ERROR in addsource: A source with name '{0}' exists already".format(name))
			return

	try:
		UpdateSource(newSource)

	except InvalidSourceError as e:
		print("WARNING: Requested source was not added due to errors:")
		PrintSource(newSource)
		raise e

	sources.append(newSource)
	WriteSources(sources)
	print("The following source was added at rank {0}:".format(len(sources)))
	PrintSource(newSource)


def LoadSources(path=None):
	path = GetUGHubDirectory(path)
	try:
		return json.loads(open(os.path.join(path, "sources.json")).read())
	except IOError:
		raise InvalidSourceError("No '{0}/sources.json' file found. "
								 "Please call 'ughub repair' to generate a new sources.json file."
								 .format(path))

def ValidateSourceNames(sources):
	try:
		names = []
		for src in sources:
			srcName = src["name"]
			if srcName in names:
				raise InvalidSourceError("duplicate source name: {0}".format(srcName))
			else:
				# todo:	check name for invalid characters (e.g. '.')
				names.append(srcName)

	except LookupError as e:
		raise InvalidSourceError("lookup of field '{0}' failed.".format(e))


def UpdateSource(src, path=None):
	# check for each source whether it was already installed. if that's the case,
	# perform git pull on that directory. If not, perform git clone.
	ughubDir = GetUGHubDirectory(path)
	sourcesDir = os.path.join(ughubDir, "sources")
	if not os.path.isdir(sourcesDir):
		os.mkdir(sourcesDir)

	try:
		name = src["name"]
		url = src["url"]
		branch = src["branch"]

		srcDir = os.path.join(sourcesDir, name)

		if not os.path.isdir(srcDir):
			print("Cloning source '{0}', branch '{1}' from '{2}'".
				  format(name, branch, url))
			proc = subprocess.Popen(["git", "clone", "--branch", branch, url, name], cwd = sourcesDir)
			if proc.wait() != 0:
				raise InvalidSourceError("Couldn't clone source '{0}' with branch '{1}' from '{2}'"
										 .format(name, branch, url))
		else:
			print("Updating source '{0}' (branch '{1}') from '{2}'".
				  format(name, branch, url))
			proc = subprocess.Popen(["git", "pull"], cwd = srcDir)
			if proc.wait() != 0:
				raise InvalidSourceError("Couldn't pull from '{1}' (branch '{0}') for source '{2}'"
										 .format(branch, url, name))

	except LookupError as e:
		raise InvalidSourceError("lookup of field '{0}' failed.".format(e))


def UpdateSources(args, path=None):
	sources = LoadSources(path)
	ValidateSourceNames(sources)

	for src in sources:
		UpdateSource(src, path)


def ListSources(args):
	sources = LoadSources()
	print("List of known sources:")
	firstOne = True
	for s in sources:
		if not firstOne:
			print("")
		firstOne = False

		try:
			PrintSource(s)

		except LookupError as e:
			raise InvalidSourceError("lookup of field '{0}' failed.".format(e))


def LoadPackageDescsFromFile(filename, sourceName):
	packagesOut = []
	try:
		try:
			content = json.loads(open(filename).read())
			if "minUGHubVersion" in content:
				if not CompareVersions(content["minUGHubVersion"], g_ughubVersionString):
					raise InvalidSourceError("ughub version '{0}' required but current version is '{1}'"
											 .format(content["minUGHubVersion"], g_ughubVersionString))

			if "include" in content:
				curDir = os.path.dirname(filename)
				for incfile in content["include"]:
					packagesOut = packagesOut + LoadPackageDescsFromFile(os.path.join(curDir, incfile), sourceName)

			if "packages" in content:
				for pkgDesc in content["packages"]:
					pkgDesc["__SOURCE"] = sourceName
					packagesOut.append(pkgDesc)

		except LookupError as e:
			raise InvalidSourceError("Failed to access {0} in '{1}'"
									 .format(e, filename))
		except IOError:
			raise InvalidSourceError("Package descriptor file of source '{0}' not found: '{1}'. "
									 "Please call 'ughub updatesources'.".format(sourceName, filename))

	except LookupError:
		raise InvalidSourceError("couldn't find field 'name'")
	except ValueError as e:
		raise InvalidSourceError("couldn't parse file '{0}': {1}"
								 .format(filename, e))

	return packagesOut


# returns a list with all available package descriptors
# adds a 'source' entry to each desc which contains the name of the package source
# sourceName is an optional parameter. If specified only the source with the given name
# is considered. If sourceName == None (by default), packages from all sources are loaded.
def LoadPackageDescs(sourceName = None):
	sources		= LoadSources()
	sourcesDir	= os.path.join(GetUGHubDirectory(), "sources")
	packagesOut = []
	errors 		= ""

	for src in sources:
		if sourceName == None or sourceName == src["name"]:
			sname = src["name"]
			sdir = os.path.join(sourcesDir, sname)
			packageDescName = os.path.join(sdir, "packages.json")

			try:
				packagesOut = packagesOut + LoadPackageDescsFromFile(packageDescName, sname)

			except InvalidSourceError as e:
				errors = errors + "Error in source '{0}':\n  {1}\n".format(sname, e)

	if len(errors) > 0:
		AppendToExitText("WARNING: Problems occurred during 'LoadPackageDescs':\n" + errors)

	return packagesOut


def FilterPackagesAny(packages, categories):
	filteredPackages = []
	for pkg in packages:
		try:
			pkgcats = ughubUtil.GetFromNestedTable(pkg, "categories")
			if any(pcat in categories for pcat in pkgcats):
				filteredPackages.append(pkg)

		except ughubUtil.NestedTableEntryNotFoundError:
			pass
	return filteredPackages


def FilterPackagesAll(packages, categories):
	filteredPackages = []
	for pkg in packages:
		try:
			pkgcats = ughubUtil.GetFromNestedTable(pkg, "categories")
			if all(cat in pkgcats for cat in categories):
				filteredPackages.append(pkg)

		except ughubUtil.NestedTableEntryNotFoundError:
			pass
	return filteredPackages


def LoadFilteredPackageDescs(args):
	categories = []
	matchAll = ughubUtil.HasCommandlineOption(args, ("-a", "--matchall"))
	installed = ughubUtil.HasCommandlineOption(args, ("-i", "--installed"))
	notinstalled = ughubUtil.HasCommandlineOption(args, ("-n", "--notinstalled"))
	sourceName = ughubUtil.GetCommandlineOptionValue(args, ("-s", "--source"))

	for arg in args:
		if arg[0] != "-":
			categories.append(arg)
		else:
			break

	try:
		allPackages = LoadPackageDescs(sourceName)

		if len(allPackages) == 0:
			return allPackages
	
		packages = []

		# select according to installed/notinstalled
		if installed and notinstalled:
			print("Cannot use --installed and --notinstalled simultaneously.")
			raise Exception()

		if installed:
			for pkg in allPackages:
				if PackageIsInstalled(pkg):
					packages.append(pkg)

		if notinstalled:
			for pkg in allPackages:
				if not PackageIsInstalled(pkg):
					packages.append(pkg)

		if not installed and not notinstalled: 
			for pkg in allPackages:
				packages.append(pkg)

		# select according to category
		if matchAll:
			packages = FilterPackagesAll(packages, categories)
		elif len(categories) > 0:
			packages = FilterPackagesAny(packages, categories)

		return packages

	except LookupError as e:
		raise InvalidPackageError(e)
	

def ListPackages(args):

	try:
		packages = LoadFilteredPackageDescs(args)

		if len(packages) == 0:
			print("no packages found")
			return

		# sort packages alphabetically
		packageDict = {}
		for pkg in packages:
			packageDict[pkg["name"]] = packageDict.get(pkg["name"], []) + [pkg]

		namesonly = ughubUtil.HasCommandlineOption(args, ("--namesonly",))

		if namesonly:
			result = ""
			for key in sorted(packageDict.keys()):
				pkgs = packageDict[key]
				for pkg in pkgs:
					result += pkg["name"] + " "

			ughubUtil.Write(result)
		else:
			print("{0:24.4}  {1:10} {2:11} {3:}"
					.format("NAME", "PREFIX", "SOURCE", "URL"))

			for key in sorted(packageDict.keys()):
				pkgs = packageDict[key]
				for pkg in pkgs:
					print("{0:24}  {1:10} {2:11} {3:}"
						.format(pkg["name"], pkg["prefix"], pkg["__SOURCE"], pkg["url"]))

	except LookupError as e:
		raise InvalidPackageError(e)


def ShortPackageInfo(pkg):
	s = "  {0:10}: '{1}'".format("name", pkg["name"])
	if "__SOURCE" in pkg:
		s = "\n".join((s, "  {0:10}: '{1}'".format("source", pkg["__SOURCE"])))
	if "__BRANCH" in pkg:
		s = "\n".join((s, "  {0:10}: '{1}'".format("branch", pkg["__BRANCH"])))
	s = "\n".join((s, "  {0:10}: '{1}'".format("url", pkg["url"])))
	s = "\n".join((s, "  {0:10}: '{1}'".format("target", GetPackageDir(pkg))))
	return s


def LongPackageInfo(pkg):
	return ughubUtil.NestedTableToString(pkg)


def PrintPackageInfo(args):
	packageList = ughubUtil.RemoveOptions(args)
	if len(packageList) != 1:
		print("Please specify exactly one package name. See 'ughub help packageinfo'")
		return

	packageName	= packageList[0]
	packages = LoadPackageDescs()

	firstPackage = True
	for pkg in packages:
		try:
			if pkg["name"] == packageName:
				if not firstPackage:
					print("")
				firstPackage = False

				print("package '{0}' from source '{1}':"
					  .format(packageName, pkg["__SOURCE"]))
				if ughubUtil.HasCommandlineOption(args, ("-s", "--short")):
					print(ShortPackageInfo(pkg))
				else:
					print(LongPackageInfo(pkg))

		except LookupError:
			raise InvalidSourceError("Failed to access package list in '{0}'"
									 .format(packagesFile))


def GetPackageDir(pkg):
	return os.path.join(GetRootDirectory(), pkg["prefix"], pkg["name"])


# returns a list of package descriptors that have to be installed for a given package.
# note that this list may contain packages that are already installed.
def BuildPackageDependencyList(packageName, availablePackages, source=None,
							   branch=None, processedPackageBranchPairs=[],
							   nodeps = False):
	packagesOut = []

	gotOne = False
	for pkg in availablePackages:
		if pkg["name"] == packageName and (source == None or source == pkg["__SOURCE"]):
			try:
				gotOne = True
				useBranch = branch or pkg["defaultBranch"]

				for processedPBP in processedPackageBranchPairs:
					if processedPBP.package == packageName:
						if processedPBP.branch == useBranch:
							return []
						else:
							raise DependencyError("Branch conflict: '{0}' required from branch '{1}' and branch '{2}'.\n"
												  "Package list:"
												  .format(packageName, useBranch, processedPBP.branch))

				pkg["__BRANCH"] = useBranch
				packagesOut.append(pkg)
				processedPackageBranchPairs.append(PackageBranchPair(packageName, useBranch))

				if not nodeps and "dependencies" in pkg:
					dependsOn = None
					deps = pkg["dependencies"]
					for dep in deps:
						if "branch" in dep:
							if dep["branch"] == pkg["__BRANCH"]:
								dependsOn = dep
						else:
							if dependsOn == None:
								dependsOn = dep

					if dependsOn:
						for depPkg in dependsOn["packages"]:
							depPkgName = depPkg["name"]
							depPkgBranch = None
							if "branch" in depPkg:
								depPkgBranch = depPkg["branch"]

							packagesOut = packagesOut + BuildPackageDependencyList(
															depPkgName,
															availablePackages,
															None,
															depPkgBranch,
															processedPackageBranchPairs)

			except DependencyError as e:
				raise DependencyError("{0}\n\n{1}"
									 .format(e, ShortPackageInfo(pkg)))
	if not gotOne:
		raise DependencyError("Required package '{0}' is not available in the current sources.\n"
							  "  Please make sure that all required sources are added to your current\n"
							  "  ughub installation (use 'ughub listsources' and 'ughub addsource')\n"
							  "  and make sure that they are all up to date (use 'ughub updatesources')."
							  .format(packageName))
	return packagesOut


#	Returns the fetch and pull urls of the git repository of the specified package as strings.
#	If no corresponding remote-urls are found, None is returned for each return value.
def GetCurrentRemoteGitURLs(pkg, origin = "origin"):
	rootDir			= GetRootDirectory()
	originFetchURL	= None
	originPushURL	= None
	if pkg["repoType"] == "git":
		prefixPath = os.path.join(rootDir, pkg["prefix"])
		pkgPath = os.path.join(prefixPath, pkg["name"])
		if os.path.isdir(os.path.join(pkgPath, ".git")):
			p = subprocess.Popen("git remote -v".split(), cwd = pkgPath, stdout=subprocess.PIPE)
			gitLog = p.communicate()[0].decode("utf-8")
			if p.returncode != 0:
				raise TransactionError("Couldn't access remote information of package '{0}' at '{1}'"
										.format(pkg["name"], pkgPath))

			for line in gitLog.splitlines():
				m = re.match(r"^origin\s+(.+?)\s+\(fetch\)$", line)
				if m:
					originFetchURL = m.group(1)
				m = re.match(r"^origin\s+(.+?)\s+\(push\)$", line)
				if m:
					originPushURL = m.group(1)

	return originFetchURL, originPushURL


def InstallPackage(args):
	packageNames	= args
	options			= []

	for i in range(len(args)):
		if args[i][0] == "-":
			packageNames = args[0:i]
			options = args[i:]
			break

	if len(packageNames) == 0:
		print("Please specify a package name. See 'ughub help install'.")
		return

	dryRun		= ughubUtil.HasCommandlineOption(options, ("-d", "--dry"))
	ignore		= ughubUtil.HasCommandlineOption(options, ("-i", "--ignore"))
	resolve		= ughubUtil.HasCommandlineOption(options, ("-r", "--resolve"))
	noupdate	= ughubUtil.HasCommandlineOption(options, ("--noupdate",))
	nodeps		= ughubUtil.HasCommandlineOption(options, ("--nodeps",))
	branch		= ughubUtil.GetCommandlineOptionValue(options, ("-b", "--branch"))
	source		= ughubUtil.GetCommandlineOptionValue(options, ("-s", "--source"))
	packages	= LoadPackageDescs()
	rootDir		= GetRootDirectory()

	requiredPackages = []
	processedPackageBranchPairs = []

	for packageName in packageNames:
		requiredPackages = (requiredPackages +
							BuildPackageDependencyList(packageName, packages,
													   source, branch,
									   				   processedPackageBranchPairs,
									   				   nodeps))

	print("List of required packages:")

	#0: Message, 1: Package name, 2: current remote, 3: required remote
	textRemoteConflictUF = (""
		"{0}: Url of remote 'origin' of package '{1}' does not correspond\n"
		"  to the current source-definition:\n"
		"  currentt URL: '{2}'\n"
		"  expected URL: '{3}'\n"
		"  This is most likely a result of an updated source-definition (e.g. through 'ughub updatesources').")

	#0: required remote, 2: package-path
	textRemoteConflictOptionsUF = (""
		"  You may\n"
		"    - call 'ughub install ...' with the '--resolve' option to resolve conflicts on the fly.\n"
		"    - manually adjust the url by executing\n"
		"      'git remote set-url origin {0}'\n"
		"      at '{1}'\n"
		"    - call 'ughub install ...' with the '--ignore' option to perform installation despite this\n"
		"      error. This may result in an outdated package and build conflicts!")

	#0: Message, 1: Package name, 2: current branch, 3: required branch
	textBranchConflictUF = (""
		"{0}: Current branch '{2}' of installed package '{1}' "
		"does not correspond to the required branch '{3}'.")

	#0: required branch, 2: package-path
	textBranchConflictOptionsUF = (""
		"  You may\n"
		"  - call 'ughub install' with the '--resolve' option to automatically resolve the conflict\n"
		"    (a checkout of the required branch will be performed).\n"
		"  - manually check out the required branch by executing\n"
		"    'git checkout {0}' at '{1}'\n"
		"  - call 'ughub install' with the '--ignore' option to ignore the error. This may lead to build problems!\n")

	# iterate over all required packages. Check for each whether it already
	# exists and whether the branch matches.
	# If it doesn't exist, perform a fresh clone.
	# If it does exist and branches match, perform a pull.
	# If it does exist but branches mismatch, perform a pull if --ignore was specified
	# and abort with a warning if it wasn't specified.

	firstPkg = True
	problemsOccurred = False
	for pkg in requiredPackages:
		if not firstPkg:
			print("")
		firstPkg = False
		print(ShortPackageInfo(pkg))

	#	check whether the package is already installed
		if pkg["repoType"] == "git":
			prefixPath = os.path.join(rootDir, pkg["prefix"])
			pkgPath = os.path.join(prefixPath, pkg["name"])
			if os.path.isdir(os.path.join(pkgPath, ".git")):
			#	The package exists. validate its origin.
				fetchURL, pushURL = GetCurrentRemoteGitURLs(pkg)
				if fetchURL != pkg["url"] or pushURL != pkg["url"]:
					if fetchURL != pkg["url"]:
						wrongURL = fetchURL
					if pushURL != pkg["url"]:
						wrongURL = pushURL

					problemsOccurred = True
					if resolve:
						print(textRemoteConflictUF.format("NOTE", pkg["name"], wrongURL, pkg["url"]))
						print("NOTE: The remote will be automatically adjusted (--resolve)")
						if not dryRun:
							proc = subprocess.Popen(["git","remote","set-url","origin", pkg["url"]], cwd = pkgPath)
							if proc.wait() != 0:
								raise TransactionError("Couldn't set url '{0}' of remote 'origin' for package '{1}' at '{2}'"
														.format(pkg["url"], pkg["name"], pkgPath))
					elif ignore:
						print(textRemoteConflictUF.format("WARNING", pkg["name"], wrongURL, pkg["url"]))
						print("NOTE: The warning will be ignored (--ignore). "
							  "This may result in an outdated package and build conflicts!")
					
					else:
						text = (textRemoteConflictUF.format("ERROR", pkg["name"], wrongURL, pkg["url"]) +
								"\n" + textRemoteConflictOptionsUF.format(pkg["url"], pkgPath))
						if dryRun:
							print(text)
						else:
							raise DependencyError(text)

			#	Validate branch
				p = subprocess.Popen("git branch".split(), cwd = pkgPath, stdout=subprocess.PIPE)
				gitLog = p.communicate()[0].decode("utf-8")
				if p.returncode != 0:
					raise TransactionError("Couldn't access branch information of package '{0}' at '{1}'"
											.format(pkg["name"], pkgPath))

				curBranch = None
				for line in gitLog.splitlines():
					if line[0] == "*":
						curBranch = line.split()[1]
						break

				if curBranch != pkg["__BRANCH"]:
					problemsOccurred = True
					if resolve:
					#todo: call git-fetch, or else checkout may fail or may be outdated.
						print(textBranchConflictUF.format("NOTE", pkg["name"], curBranch, pkg["__BRANCH"]))
						print("NOTE: The required branch will be automatically checked out (--resolve)")
						if not dryRun:
					 		proc = subprocess.Popen(["git", "checkout", pkg["__BRANCH"]], cwd = pkgPath)
					 		if proc.wait() != 0:
					 			raise TransactionError("Trying to resolve branch conflict but couldn't check "
					 								   "out branch '{0}' of package '{1}' at '{2}'"
					 								   .format(pkg["__BRANCH"], pkg["name"], pkgPath))
					elif ignore:
						print(textBranchConflictUF.format("WARNING", pkg["name"], curBranch, pkg["__BRANCH"]))
						print("NOTE: The warning will be ignored (--ignore). This may result in build problems!")

					else:
						text = (textBranchConflictUF.format("ERROR", pkg["name"], curBranch, pkg["__BRANCH"]) +
								"\n" + textBranchConflictOptionsUF.format(pkg["__BRANCH"], pkgPath))
						if dryRun:
							print(text)
						else:
							raise DependencyError(text)

				if not (dryRun or noupdate):
				# todo: only perform pull if not in detached head state
					proc = subprocess.Popen(["git", "pull"], cwd = pkgPath)
					if proc.wait() != 0:
						raise TransactionError("Couldn't pull for package '{0}' at '{1}'"
												.format(pkg["name"], pkgPath))
				elif noupdate:
					print("NOTE: Package won't be updated due to 'noupdate' option. "
						  "This may lead to build conflicts and errors.")

			else:
			#	the package doesn't exist yet. Make sure that all paths are set up correctly
			#	and perform a clone
				if os.path.exists(pkgPath):
					try:
						if not os.path.isdir(pkgPath):
							raise TargetError("Target path '{0}' for package '{1}' exists but is not a directory"
											   .format(pkgPath, pkg["name"]))
						if os.listdir(pkgPath):
							raise TargetError("Target path '{0}' for package '{1}' has to be empty or a valid git working copy."
											  .format(pkgPath, pkg["name"]))
					except TargetError as e:
						if dryRun:
							print("WARNING: {0}".format(e))
							problemsOccurred = True
						else:
							raise e

				if not dryRun:
					if not os.path.exists(pkgPath):
						os.makedirs(pkgPath)

					proc = subprocess.Popen(["git", "clone", "--branch", pkg["__BRANCH"], pkg["url"], pkg["name"]], cwd = prefixPath)
					if proc.wait() != 0:
						raise TransactionError("Couldn't clone package '{0}' with branch '{1}' from '{2}'"
												.format(pkg["name"], pkg["__BRANCH"], pkg["url"]))

		else:
			raise InvalidPackageError("Unsupported repository type of package '{0}': '{1}'"
							   		  .format(pkg["name"], pkg["repoType"]))

	if dryRun:
		print("Dry run. Nothing was installed/updated.")
		if problemsOccurred:
			print("WARNING: problems were detected during dry installation run. See above.")
		return

def InstallAllPackages(args):
	source		= ughubUtil.GetCommandlineOptionValue(args, ("-s", "--source"))
	packages	= LoadFilteredPackageDescs(args)
	names		= []

	for pkg in packages:
		names.append(pkg["name"])

	isOption = False
	for arg in args:
		if isOption or arg[0] == "-":
			isOption = True
			names.append(arg)

	InstallPackage(names)


def PackageIsInstalled(pkg):
	return os.path.isdir(GetPackageDir(pkg))

def CallGitOnPackage(pkg, gitCommand, args):
#todo:	check for changes first for 'commit' and 'push', using e.g.
#		git status --porcelain
	print("> {0}".format(GetPackageDir(pkg)))

	proc = subprocess.Popen(["git", "--no-pager", gitCommand] + args, cwd = GetPackageDir(pkg), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	encoding = sys.stdout.encoding or "ascii"
	
	if proc.wait() == 0:
		print(proc.stdout.read().decode(encoding, "ignore"))
		print(proc.stderr.read().decode(encoding, "ignore"))
	else:
		if proc.stdout:
			print(proc.stdout.read().decode(encoding, "ignore"))
		if proc.stderr:
			print(proc.stderr.read().decode(encoding, "ignore"))

		raise TransactionError("Couldn't perform 'git {0}' for package '{1}' at '{2}'"
							   .format(gitCommand, pkg["name"], GetPackageDir(pkg)))


def CacheGitPassword():
	# todo:	This currently only works on unix (tested on linux). A version for Windows
	#		and possibly OSX has to be added.
	proc = subprocess.Popen("git config --global credential.helper cache".split())
	if proc.wait() != 0:
		raise TransactionError("Couldn't enable password caching! Please check your git version.")


def CallGitOnPackages(args, gitCommand):
	packages = LoadPackageDescs()

	fails = []
	firstPackage = True

	specifiedPackages = []

	# get the argument separator "---"
	gitargs = args
	for i in range(len(args)):
		if args[i] == "---":
			gitargs = args[0:i]
			specifiedPackages = args[i+1:]
			break

	try:
		CacheGitPassword()
	except TransactionError as e:
		print("WARNING:\n  " + str(e))

	if len(specifiedPackages) > 0:
		for pname in specifiedPackages:
			if not firstPackage:
				print("")
			firstPackage = False

			try:
				pkg = ughubUtil.GetFromNestedTable(packages, pname)
				if not PackageIsInstalled(pkg):
					raise InvalidPackageError("Package '{0}' is not installed. See 'ughub help install'".format(pname))

				try:
					CallGitOnPackage(pkg, gitCommand, gitargs)
				except TransactionError as e:
					fails.append(str(e))

			except ughubUtil.NestedTableEntryNotFoundError:
				fails.append("Unknown package '{0}'".format(pname))

	else:
	#	check for each known package whether it is installed. If this is the case, perform a pull
		for pkg in packages:
			if PackageIsInstalled(pkg):
				if not firstPackage:
					print("")
				firstPackage = False

				try:
					CallGitOnPackage(pkg, gitCommand, gitargs)
				except TransactionError as e:
					fails.append(str(e))

	if len(fails) > 0:
		msg = "The following errors occurred while performing 'git {0}':".format(gitCommand)
		for e in fails:
			msg = msg + "\n  - " + e

		raise TransactionError(msg)


def PackageLogs(args):
	num = "10"
	newargs = ["---"]
	ignoreEntries = 0
	for i in range(len(args)):
		if ignoreEntries > 0:
			ignoreEntries = ignoreEntries - 1
		else:
			if args[i] == "-n":
				num = args[i+1]
				ignoreEntries = 1
			else:
				newargs = newargs + [args[i]]

	CallGitOnPackages(["-n", num, "--pretty=format:* %an (%ad | %h)%n  \"%s\""] + newargs, "log")


def GenerateProjectFiles(args):
	
	options			= []

	for i in range(len(args)):
		if args[i][0] == "-":
			options = args[i:]
			args = args[0:i]
			break

	if len(args) < 1:
		raise ArgumentError("Please specify a TARGET.")

	name			= ughubUtil.GetCommandlineOptionValue(args, ("-n", "--name"))
	overwriteFiles	= ughubUtil.HasCommandlineOption(options, ("-o", "--overwrite"))
	deleteFiles		= ughubUtil.HasCommandlineOption(options, ("-d", "--delete"))

	if deleteFiles:
		ughubProjectFileGenerator.RemoveFiles(GetRootDirectory(), args[0])
	else:
		ughubProjectFileGenerator.Run(GetRootDirectory(), args[0], name, overwriteFiles)

def GetAutoCompletions(args):

	if len(args) >= 1 and args[0] == "install":
		try:
			packages = LoadPackageDescs()
		except:
			return
		result = ughubHelp.GetOptionStringsForCommand("install")
		result += "\n"
		for p in packages:
			result += p["name"] + "\n"
		
		ughubUtil.Write(result[:-1])
		
		return

	if len(args) >= 1 and args[0] == "log":
		try:
			packages = LoadPackageDescs()
		except:
			return
		result = ughubHelp.GetOptionStringsForCommand("log")
		result += "\n"
		for p in packages:
			if PackageIsInstalled(p):
				result += p["name"] + "\n"

		ughubUtil.Write(result[:-1])
		return

	if len(args) >= 1 and args[0] == "help":
		ughubHelp.PrintCommandNames()		
		ughubUtil.Write("\n" + ughubHelp.GetOptionStringsForCommand(args[0]))
		return
	
	if len(args) >= 1 and ughubHelp.IsCommandInHelp(args[0]):
		ughubUtil.Write(ughubHelp.GetOptionStringsForCommand(args[0]))	
		return

	if len(args) == 1:
		ughubHelp.PrintCommandNames()
		return 

	
def RunUGHub(args):

	exitCode = 1

	try:
		# A more elaborate check would be required here, since ughub actually runs with python 3, too.
		# if sys.version_info[0] != 2:
		# 	raise Exception("'ughub' requires Python v2. Currently in use is Python v{0}.{1}.{2}."
		# 					.format(str(sys.version_info[0]),
		# 							str(sys.version_info[1]),
		# 							str(sys.version_info[2])))

		if args == None or len(args) == 0:
			ughubHelp.PrintUsage()
			return

		cmd = args[0]

		if cmd == "addsource":
			AddSource(args[1:])

		elif cmd == "help":
			if len(args) == 1:
				ughubHelp.PrintHelp()
			elif args[1] == "--commands":
				ughubHelp.PrintCommandNames()
			else:
				ughubHelp.PrintCommandHelp(args[1], args[2:])

		elif cmd == "genprojectfiles":
			GenerateProjectFiles(args[1:])

		elif cmd == "git":
			CallGitOnPackages(args[2:], args[1])

		elif cmd == "gitadd":
			raise Exception("gitadd is no longer supported. Please call 'ughub git add' instead.")

		elif cmd == "gitcommit":
			raise Exception("gitcommit is no longer supported. Please call 'ughub git commit' instead.")

		elif cmd == "gitpull":
			raise Exception("gitpull is no longer supported. Please call 'ughub git pull' instead.")

		elif cmd == "gitpush":
			raise Exception("gitpush is no longer supported. Please call 'ughub git push' instead.")

		elif cmd == "gitstatus":
			raise Exception("gitstatus is no longer supported. Please call 'ughub git status' instead.")

		elif cmd == "init":
			InitializeDirectory(args[1:])

		elif cmd == "install":
			InstallPackage(args[1:])

		elif cmd == "installall":
			InstallAllPackages(args[1:])

		elif cmd == "packageinfo":
			PrintPackageInfo(args[1:])

		elif cmd in ["list", "listpackages"]:
			ListPackages(args[1:])

		elif cmd == "log":
			PackageLogs(args[1:])

		elif cmd == "repair":
			Repair(args[1:])

		elif cmd == "listsources":
			ListSources(args[1:])

		elif cmd == "updatesources":
			UpdateSources(args[1:])

		elif cmd in ("version", "--version"):
			print("ughub, version {}".format(g_ughubVersionString))
			print("Copyright 2015 G-CSC, Goethe University Frankfurt")
			print("All rights reserved")
		
		elif cmd == "getcompletions":
			GetAutoCompletions(args[1:])
		
		else:
			print("Unknown command: '{0}'".format(cmd))
			ughubHelp.PrintUsage()

	except ArgumentError as e:
		print("ERROR (bad arguments to '{0}')\n  {1}".format(cmd, e))

	except NoRootDirectoryError:
		print(	"Couldn't find ughub root directory. Please change directory to a path\n"
				"with a '.ughub' folder or initialize a directory for use with ughub by\n"
				"calling 'ughub init'.")

	except ughubHelp.MalformedHelpContentsError as e:
		print("ERROR (malformed help contents)\n  {0}".format(e))

	except InvalidSourceError as e:
		print("ERROR (invalid source)\n  {0}".format(e))

	except InvalidPackageError as e:
		print("ERROR (invalid package)\n  {0}".format(e))

	except DependencyError as e:
		print("ERROR (dependency error)\n  {0}".format(e))
		print("ERROR (dependency error) ---  see above")

	except TargetError as e:
		print("ERROR (target error)\n  {0}".format(e))

	except TransactionError as e:
		print("ERROR (transaction error)\n  {0}".format(e))

	except IOError as e:
		print("ERROR (io error):\n  {0}".format(e))

	except Exception as e:
		print("ERROR:\n  {0}".format(e))

	else:
		exitCode = 0

	print("")

	if len(g_exitText) > 0:
		print(g_exitText)

	return exitCode


sys.exit(RunUGHub(sys.argv[1:]))
