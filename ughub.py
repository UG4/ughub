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

# v1.0.1: Supporting 'include' statement in packages.json files.
g_ughubVersionString = "1.0.1"

import collections
import json
import os
import re
import subprocess
import sys

import ughubHelp
import ughubUtil

class NoRootDirectoryError(Exception) : pass
class InvalidSourceError(Exception) : pass
class InvalidPackageError(Exception) : pass
class DependencyError(Exception) : pass
class TargetError(Exception) : pass
class TransactionError(Exception): pass


PackageBranchPair = collections.namedtuple("PackageBranchPair", "package branch")

# returns True if the first version number is smaller or equal to the second, False if not.
def CompareVersions(vstr0, vstr1):
	nums0 = vstr0.split(".")
	nums1 = vstr1.split(".")
	for v0, v1 in zip(nums0, nums1):
		if v0 <= v1:
			return True
	return False


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
	f.write("cmake_minimum_required(VERSION 2.6)\n")
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
		return json.loads(file(os.path.join(path, "sources.json")).read())
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
		raise InvalidSourceError("lookup of field '{0}' failed.".format(e.message))


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
		raise InvalidSourceError("lookup of field '{0}' failed.".format(e.message))


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
			firstOne = True

		try:
			PrintSource(s)

		except LookupError as e:
			raise InvalidSourceError("lookup of field '{0}' failed.".format(e.message))


def LoadPackageDescsFromFile(filename, sourceName):
	packagesOut = []
	try:
		try:
			content = json.loads(file(filename).read())
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
									 .format(e.message, filename))
		except IOError:
			raise InvalidSourceError("Package descriptor file of source '{0}' not found: '{1}'. "
									 "Please call 'ughub updatesources'.".format(sourceName, filename))

	except LookupError:
		raise InvalidSourceError("couldn't find field 'name'")
	except ValueError as e:
		raise InvalidSourceError("couldn't parse file '{0}': {1}"
								 .format(filename, e.message))

	return packagesOut


# returns a list with all available package descriptors
# adds a 'source' entry to each desc which contains the name of the package source
def LoadPackageDescs():
	sources		= LoadSources()
	sourcesDir	= os.path.join(GetUGHubDirectory(), "sources")
	packagesOut = []
	errors 		= ""

	for src in sources:
		sourceName = src["name"]
		sourceDir = os.path.join(sourcesDir, sourceName)
		packageDescName = os.path.join(sourceDir, "packages.json")

		try:
			packagesOut = packagesOut + LoadPackageDescsFromFile(packageDescName, sourceName)

		except InvalidSourceError as e:
			errors = errors + "Error in source '{0}':\n  {1}\n".format(sourceName, e.message)

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


def ListPackages(args):
	categories = []
	matchAll = ughubUtil.HasCommandlineOption(args, ("-a", "--matchall"))

	for arg in args:
		if arg[0] != "-":
			categories.append(arg)

	try:
		packages = LoadPackageDescs()

		if len(packages) == 0:
			print("no packages found")
			return

		if matchAll:
			packages = FilterPackagesAll(packages, categories)
		elif len(categories) > 0:
			packages = FilterPackagesAny(packages, categories)

		if len(packages) == 0:
			print("no packages found for the given criteria")
			return

		# sort packages alphabetically
		packageDict = {}
		for pkg in packages:
			packageDict[pkg["name"]] = packageDict.get(pkg["name"], []) + [pkg]

		print("{0:24.24}  {1:10.10} {2:11.11} {3:}"
				.format("NAME", "PREFIX", "SOURCE", "URL"))

		for key in sorted(packageDict.keys()):
			pkgs = packageDict[key]
			for pkg in pkgs:
				print("{0:24.24}  {1:10.10} {2:11.11} {3:}"
					  .format(pkg["name"], pkg["prefix"], pkg["__SOURCE"], pkg["url"]))

	except LookupError as e:
		raise InvalidPackageError(e.message)


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
							   branch=None, processedPackageBranchPairs=[]):
	packagesOut = []

	for pkg in availablePackages:
		if pkg["name"] == packageName and (source == None or source == pkg["__SOURCE"]):
			try:
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

				if "dependencies" in pkg:
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
									 .format(e.message, ShortPackageInfo(pkg)))
	return packagesOut



def InstallPackage(args):
	if len(args) == 0 or args[0][0] == "-":
		print("Please specify a package name. See 'ughub help install'")
		return

	dryRun	= ughubUtil.HasCommandlineOption(args, ("-d", "--dry"))
	force	= ughubUtil.HasCommandlineOption(args, ("-f", "--force"))
	branch	= ughubUtil.GetCommandlineOptionValue(args, ("-b", "--branch"))
	source	= ughubUtil.GetCommandlineOptionValue(args, ("-s", "--source"))
	packageName	= args[0]
	packages	= LoadPackageDescs()
	rootDir		= GetRootDirectory()
	requiredPackages	= BuildPackageDependencyList(packageName, packages, source, branch)

	print("List of required packages:")

	# iterate over all required packages. Check for each whether it already
	# exists and whether the branch matches.
	# If it doesn't exist, perform a fresh clone.
	# If it does exist and branches match, perform a pull.
	# If it does exist but branches mismatch, perform a pull if --force was specified
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
				p = subprocess.Popen("git branch".split(), cwd = pkgPath, stdout=subprocess.PIPE)
				gitLog, _ = p.communicate()
				if p.returncode != 0:
					raise TransactionError("Couldn't access branch information of package '{0}' at '{1}'"
											.format(pkg["name"], pkgPath))
					
				curBranch = None
				for line in gitLog.splitlines():
					if line[0] == "*":
						curBranch = line.split()[1]
						break

				if curBranch != pkg["__BRANCH"]:
					if not dryRun:
						if force:
							proc = subprocess.Popen(["git", "checkout", pkg["__BRANCH"]], cwd = pkgPath)
							if proc.wait() != 0:
								raise TransactionError("Couldn't check out branch '{0}' of package '{1}' at '{2}'"
														.format(pkg["__BRANCH"], pkg["name"], pkgPath))
							print("Forcefully resolved branch conflict by switching from branch '{0}'\n"
								  "to branch '{1}' of package '{2}' at '{3}'"
								  .format(curBranch, pkg["__BRANCH"], pkg["name"], pkgPath))

						else:
							raise DependencyError(
									"Current branch '{0}' and required branch '{1}'\n"
									"  do not match for package '{2}' at '{3}'.\n"
									"  Call 'ughub install' with the '--force' option to force a checkout of the required branch."
									.format(curBranch, pkg["__BRANCH"], pkg["name"], pkgPath))
					else:
						if force:
							print("NOTE: Branch '{0}' of package '{2}' at '{3}'\n"
								  "      will be replaced by branch '{1}'"
								   .format(curBranch, pkg["__BRANCH"], pkg["name"], pkgPath))
						else:
							problemsOccurred = True
							print("WARNING: Branch conflict of package '{2}' at '{3}' detected.\n"
								  "         Use the --force option to replace branch '{0}' by branch '{1}'"
								   .format(curBranch, pkg["__BRANCH"], pkg["name"], pkgPath))


				if not dryRun:
					proc = subprocess.Popen(["git", "pull"], cwd = pkgPath)
					if proc.wait() != 0:
						raise TransactionError("Couldn't pull for package '{0}' at '{1}'"
												.format(pkg["name"], pkgPath))

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
							print("WARNING: {0}".format(e.message))
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


def PackageIsInstalled(pkg):
	return os.path.isdir(GetPackageDir(pkg))

def CallGitOnPackage(pkg, gitCommand, args):
#todo:	check for changes first for 'commit' and 'push', using e.g.
#		git status --porcelain
	print("> {0}".format(GetPackageDir(pkg)))
	proc = subprocess.Popen(["git", gitCommand] + args, cwd = GetPackageDir(pkg))
	if proc.wait() != 0:
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

	# get the argument separator "---"
	gitargs = []
	for i in range(len(args)):
		if args[i] == "---":
			gitargs = args[i+1:]
			args = args[0:i]
			break

	try:
		CacheGitPassword()
	except TransactionError as e:
		print("WARNING:\n  " + e.message)

	# print("args: {0}, gitargs: {1}".format(args, gitargs))
	if len(args) > 0:
		for pname in args:
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
					fails.append(e.message)

			except NestedTableEntryNotFoundError:
				raise fails.append("Unknown package '{0}'".format(pname))

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
					fails.append(e.message)

	if len(fails) > 0:
		msg = "The following errors occurred while performing 'git {0}':".format(gitCommand)
		for e in fails:
			msg = msg + "\n  - " + e

		raise TransactionError(msg)


def ParseArguments(args):
	try:
		if args == None or len(args) == 0:
			ughubHelp.PrintUsage()
			return

		cmd = args[0]
		
		if cmd == "addsource":
			AddSource(args[1:])

		elif cmd == "help":
			print("")
			if len(args) == 1:
				ughubHelp.PrintHelp()
			else:
				ughubHelp.PrintCommandHelp(args[1])

		elif cmd == "gitcommit":
			CallGitOnPackages(args[1:], "commit")

		elif cmd == "gitpull":
			CallGitOnPackages(args[1:], "pull")

		elif cmd == "gitpush":
			CallGitOnPackages(args[1:], "push")

		elif cmd == "gitstatus":
			CallGitOnPackages(args[1:], "status")

		elif cmd == "init":
			InitializeDirectory(args[1:])

		elif cmd == "install":
			InstallPackage(args[1:])

		elif cmd == "packageinfo":
			PrintPackageInfo(args[1:])

		elif cmd == "listpackages":
			ListPackages(args[1:])

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

		else:
			print("Unknown command: '{0}'".format(cmd))
			ughubHelp.PrintUsage()

	except NoRootDirectoryError:
		print(	"Couldn't find ughub root directory. Please change directory to a path\n"
				"with a '.ughub' folder or initialize a directory for use with ughub by\n"
				"calling 'ughub init'.")

	except ughubHelp.MalformedHelpContentsError as e:
		print("ERROR (malformed help contents)\n  {0}".format(e.message))

	except InvalidSourceError as e:
		print("ERROR (invalid source)\n  {0}".format(e.message))

	except InvalidPackageError as e:
		print("ERROR (invalid package)\n  {0}".format(e.message))

	except DependencyError as e:
		print("ERROR (dependency error)\n  {0}".format(e.message))
		print("ERROR (dependency error) ---  see above")

	except TargetError as e:
		print("ERROR (target error)\n  {0}".format(e.message))

	except TransactionError as e:
		print("ERROR (transaction error)\n  {0}".format(e.message))

	except IOError as e:
		print("ERROR (io error):\n  {0}".format(e.message))

	print("")
	
	if len(g_exitText) > 0:
		print(g_exitText)

ParseArguments(sys.argv[1:])
