#! /usr/bin/env python

# copyright 2015 Sebastian Reiter (G-CSC Frankfurt)

# standard library imports
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


def GetRootDirectory():
	curDir = os.getcwd()
	while True:
		if os.path.isdir(os.path.join(curDir, ".ughub")):
			return curDir
		nextDir = os.path.dirname(curDir)
		if nextDir == curDir:
			raise NoRootDirectoryError()
		curDir = nextDir


def GetUGHubDirectory():
	return os.path.join(GetRootDirectory(), ".ughub")


def InitializeDirectory(args):
	force = ughubUtil.HasCommandlineOption(args, ("-f", "--force"))

	if os.path.isdir(".ughub"):
		print("Directory has been initialized already. Aborting.")
	else:
		try:
			rootDir = GetRootDirectory()
			if not force:
				print("Warning: Found ughub root path at: {0}".format(rootDir))
				print("call 'ughub init -f' to force initialization in this path.")
				return

		except NoRootDirectoryError:
			pass

		# this is actually the expected case
		os.mkdir(".ughub")
		# create a dictionary that stores the default source-urls
		sources = 	[{	"name": "UG4",
						"url": "/home/sreiter/projects/ug4-packages",
						"branch": "master"}]

		with open(os.path.join(".ughub", "sources.json"), "w") as outfile:
			json.dump(sources, outfile, indent = 4)


def LoadSources(path=None):
	if path == None:
		path = GetUGHubDirectory()
	return json.loads(file(os.path.join(path, "sources.json")).read())

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


def RefreshSources(args):
	sources = LoadSources()
	ValidateSourceNames(sources)

	ughubDir = GetUGHubDirectory()
	sourcesDir = os.path.join(ughubDir, "sources")
	if not os.path.isdir(sourcesDir):
		os.mkdir(sourcesDir)

	# check for each source whether it was already installed. if that's the case,
	# perform git pull on that directory. If not, perform git clone.
	try:
		for src in sources:
			name = src["name"]
			url = src["url"]
			branch = src["branch"]

			srcDir = os.path.join(sourcesDir, name)

			if not os.path.isdir(srcDir):
				print("Cloning source '{0}' from branch '{1}' at '{2}'".
					  format(name, branch, url))
				proc = subprocess.Popen(["git", "clone", "--branch", branch, url, name], cwd = sourcesDir)
				if proc.wait() != 0:
					raise InvalidSourceError("Couldn't check out source '{0}' from branch '{1}' at '{2}'"
											 .format(name, branch, url))
			else:
				print("Updating source '{0}' from branch '{1}' at '{2}'".
					  format(name, branch, url))
				proc = subprocess.Popen(["git", "pull"], cwd = srcDir)
				if proc.wait() != 0:
					raise InvalidSourceError("Couldn't pull from branch '{0}' at '{1}' for source '{2}'"
											 .format(branch, url, name))

	except LookupError as e:
		raise InvalidSourceError("lookup of field '{0}' failed.".format(e.message))


# returns a list with all available package descriptors
# adds a 'source' entry to each desc which contains the name of the package source
def LoadPackageDescs():
	sources		= LoadSources()
	sourcesDir	= os.path.join(GetUGHubDirectory(), "sources")
	packagesOut = []

	for src in sources:
		try:
			sourceName = src["name"]
			try:
				packagesFile = os.path.join(sourcesDir, sourceName, "packages.json")
				content = json.loads(file(packagesFile).read())
				for pkgDesc in content["packages"]:
					pkgDesc["__SOURCE"] = sourceName
					packagesOut.append(pkgDesc)

			except LookupError:
				raise InvalidSourceError("Failed to access package list in '{0}'"
										 .format(packagesFile))

		except LookupError:
			raise InvalidSourceError("couldn't find field 'name'")

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

		for pkg in packages:
			print("{0:16.16}  {1:10.10}  {2:.50}"
				  .format(pkg["name"], pkg["prefix"], pkg["url"]))

	except LookupError as e:
		raise InvalidPackageError(e.message)


def PrintPackageInfo(args):
	if len(args) != 1:
		print("Please specify exactly one package name. See 'ughub help packageinfo'")
		return

	packageName	= args[0]
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
				print(ughubUtil.NestedTableToString(pkg))

		except LookupError:
			raise InvalidSourceError("Failed to access package list in '{0}'"
									 .format(packagesFile))

def GetPackageDir(pkg):
	return os.path.join(GetRootDirectory(), pkg["prefix"], pkg["name"])

def ShortPackageInfo(pkg):
	s = "  {0:10}: '{1}'".format("name", pkg["name"])
	if "__SOURCE" in pkg:
		s = "\n".join((s, "  {0:10}: '{1}'".format("source", pkg["__SOURCE"])))
	if "__BRANCH" in pkg:
		s = "\n".join((s, "  {0:10}: '{1}'".format("branch", pkg["__BRANCH"])))
	s = "\n".join((s, "  {0:10}: '{1}'".format("url", pkg["url"])))
	s = "\n".join((s, "  {0:10}: '{1}'".format("target", GetPackageDir(pkg))))
	return s


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
					if processedPBP[0] == packageName:
						if processedPBP[1] == useBranch:
							return []
						else:
							raise DependencyError("Branch conflict: '{0}' required from branch '{1}' and branch '{2}'.\n"
												  "Package list:"
												  .format(packageName, useBranch, processedPBP[1]))

				pkg["__BRANCH"] = useBranch
				packagesOut.append(pkg)
				processedPackageBranchPairs.append((packageName, useBranch))

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

	branch = ughubUtil.GetCommandlineOptionValue(args, ("-b", "--branch"))
	source = ughubUtil.GetCommandlineOptionValue(args, ("-s", "--source"))
	packageName = args[0]
	packages = LoadPackageDescs()
	requiredPackages = BuildPackageDependencyList(packageName, packages, source, branch)
	rootDir = GetRootDirectory()

	print("The following packages will be installed/updated:")
	firstPkg = True
	for pkg in requiredPackages:
		if not firstPkg:
			print("")
		firstPkg = False

		print(ShortPackageInfo(pkg))

	if ughubUtil.HasCommandlineOption(args, ("-d", "--dry")):
		return



	print("ERROR - NOT YET IMPLEMENTED")
	# for arg in args:
	# 	if arg in ("-b", "--branch"):



def ParseArguments(args):
	try:
		if args == None or len(args) == 0:
			ughubHelp.PrintUsage()
			return

		cmd = args[0]
		
		if cmd == "help":
			print("")
			if len(args) == 1:
				ughubHelp.PrintHelp()
			else:
				ughubHelp.PrintCommandHelp(args[1])

		elif cmd == "init":
			InitializeDirectory(args[1:])

		elif cmd == "install":
			InstallPackage(args[1:])

		elif cmd == "refresh":
			RefreshSources(args[1:])

		elif cmd == "packageinfo":
			PrintPackageInfo(args[1:])

		elif cmd == "packages":
			ListPackages(args[1:])

		else:
			ughubHelp.PrintUsage()

	except NoRootDirectoryError:
		print(	"Couldn't find ughub root directory. Please change directory to a path\n"
				"with a '.ughub' folder or initialize a directory for use with ughub by\n"
				"calling 'ughub init'.")

	except ughubHelp.MalformedHelpContentsError as e:
		print("ERROR (malformed help contents) --- {0}".format(e.message))

	except InvalidSourceError as e:
		print("ERROR (invalid source) --- {0}".format(e.message))

	except InvalidPackageError as e:
		print("ERROR (invalid package) --- {0}".format(e.message))

	except DependencyError as e:
		print("ERROR (dependency error) --- {0}".format(e.message))
		print("ERROR (dependency error) --- see above")
	print("")

ParseArguments(sys.argv[1:])
