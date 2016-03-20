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
from __future__ import print_function
import codecs
import collections
import os

PathNode = collections.namedtuple("PathTypePair", "path type ignore")

def CollectAffectedFiles(path, svnPath, conf):
	files = sorted(os.listdir(path))
	affectedFiles = []
	for f in files:
		fullName = os.path.join(path, f)
		if os.path.isdir(fullName):
			svnName = os.path.join(svnPath, f)
			affectedFiles = affectedFiles + CollectAffectedFiles(fullName, svnName, conf)

	for f in files:
		fullName = os.path.join(path, f)
		if os.path.isfile(fullName):
			svnName = os.path.join(svnPath, f)
			if ConsiderFile(svnName, conf):
				affectedFiles.append(AffectedFile(fullName, svnName))

	return affectedFiles


def ListPaths(path):
	pathsOut = []
	files = os.listdir(path)
	for f in files:
		fname = os.path.join(path, f)
		if os.path.isdir(fname):
			pathsOut.append(f)
	return pathsOut


def GetEclipseProjectPaths(rootDir):
	dirs = [	PathNode(rootDir, "root", ["apps", "externals", "plugins", "ugcore"]),
				PathNode(os.path.join(rootDir, "ugcore"), "leaf", [])]

	for subroot in ("apps", "externals", "plugins"):
		fullDir = os.path.join(rootDir, subroot);
		leafs = ListPaths(fullDir)
		dirs.append(PathNode(fullDir, "subroot", leafs))
		for leaf in leafs:
			dirs.append(PathNode(os.path.join(fullDir, leaf), "leaf", []))

	return dirs

def GenerateEclipseProjectFiles(rootDir, projectName, overwriteFiles):
	localDir = os.path.dirname(os.path.realpath(__file__))
	templateLeaf = codecs.open(os.path.join(localDir, "project_templates/eclipse-leaf"), "r", "utf-8").read()
	templateRoot = codecs.open(os.path.join(localDir, "project_templates/eclipse-root"), "r", "utf-8").read()
	templateFilter = codecs.open(os.path.join(localDir, "project_templates/eclipse-filter"), "r", "utf-8").read()
	templateCProject = codecs.open(os.path.join(localDir, "project_templates/eclipse-cproject"), "r", "utf-8").read()

	pathNodes = GetEclipseProjectPaths(rootDir)
	for pn in pathNodes:
		filename = os.path.join(pn.path, ".project")
		if (not (overwriteFiles or pn.type == "subroot")) and os.path.isfile(filename):
			continue

		if projectName and (pn.type == "root"):
			pname = projectName
		else:
			pname = os.path.basename(pn.path)

		if (pn.type == "root") or (pn.type == "subroot"):
			filters = ""
			for p in pn.ignore:
				filters = filters + templateFilter.replace("$IGNOREPATH$", p)
			template = templateRoot.replace("$FILTERS$", filters)

		elif pn.type == "leaf":
			template = templateLeaf
			codecs.open(os.path.join(pn.path, ".cproject"), "w", 'utf-8', errors="replace").write(templateCProject)

		fileContents = template.replace("$PROJECTNAME$", pname);
		codecs.open(filename, "w", 'utf-8', errors="replace").write(fileContents)

	print(	"Eclipse project files generated.")
	print(	"Execute the following steps to import or update your project in Eclipse:")
	print(	"  - Open Eclipse,\n"
			"  - Click 'File->Import...->General->Existing Project Into Workspace'\n"
			"  - Choose ug4's root directory, and enable the options 'Search for nested projects'\n"
			"    and 'Hide projects that already exist in the workspace'.\n"
			"  - From Eclipse MARS on (Eclipse v4.5) you may activate the option\n"
			"    'Project Presentation->Hierarchical' in the dropdown menu of the 'Project Explorer'.")


def RemoveEclipseProjectFiles(rootDir):
	pathNodes = GetEclipseProjectPaths(rootDir)
	for pn in pathNodes:
		for f in (".project", ".cproject"):
			filename = os.path.join(pn.path, f)
			if os.path.isfile(filename):
				os.remove(filename)

	print("Eclipse project files deleted.")

# def GenerateEclipseProjectFiles(rootDir, projectName, overwriteFiles):
# 	localDir = os.path.dirname(os.path.realpath(__file__))
# 	templateNested = codecs.open(os.path.join(localDir, "project_templates/eclipse-nested"), "r", "utf-8").read()
# 	templateRoot = codecs.open(os.path.join(localDir, "project_templates/eclipse-root"), "r", "utf-8").read()

# 	rootDirs = [rootDir]
# 	nestedDirs = [os.path.join(rootDir, "ugcore")]

# 	for d in ("apps", "externals", "plugins"):
# 		fullDir = os.path.join(rootDir, d);
# 		rootDirs.append(fullDir)
# 		nestedDirs = nestedDirs + ListPaths(fullDir)

# #	write root files
# 	for d in rootDirs:
# 		filename = os.path.join(d, ".project")
		
# 		if os.path.isfile(filename) and not overwriteFiles:
# 			continue

# 		if projectName and d == rootDir:
# 			pname = projectName
# 		else:
# 			pname = os.path.basename(d)

# 		template = templateRoot
# 		fileContents = template.replace("$PROJECTNAME$", pname);
# 		codecs.open(filename, "w", 'utf-8', errors="replace").write(fileContents)

# #	write nested files
# 	for d in nestedDirs:
# 		filename = os.path.join(d, ".project")
		
# 		if os.path.isfile(filename) and not overwriteFiles:
# 			continue

# 		pname = os.path.basename(d)
# 		template = templateNested

# 		fileContents = template.replace("$PROJECTNAME$", pname);
# 		codecs.open(filename, "w", 'utf-8', errors="replace").write(fileContents)

# 	print(	"Eclipse project files generated.")
# 	print(	"  - Open Eclipse,\n"
# 			"  - Click 'File->Import...->General->Existing Project Into Workspace'\n"
# 			"  - Choose ug4's root directory and enable 'Search for nested projects' only.\n"
# 			"  - From Eclipse MARS on (Eclipse v4.5) you can activate the option\n"
# 			"    'Project Presentation->Hierarchical' in the dropdown menu of the 'Project Explorer'.")


# def RemoveEclipseProjectFiles(rootDir):
# 	dirs = [rootDir, os.path.join(rootDir, "ugcore")]

# 	for d in ("apps", "externals", "plugins"):
# 		fullDir = os.path.join(rootDir, d);
# 		dirs.append(fullDir)
# 		dirs = dirs + ListPaths(fullDir)

# #	write root files
# 	for d in dirs:
# 		for f in (".project", ".cproject"):
# 			filename = os.path.join(d, f)
		
# 			if os.path.isfile(filename):
# 				os.remove(filename)

# 	print("Eclipse project files deleted.")


def Run(rootDir, targetName, projectName, overwriteFiles):
	if targetName.lower() == "eclipse":
		GenerateEclipseProjectFiles(rootDir, projectName, overwriteFiles)


def RemoveFiles(rootDir, targetName):
	if targetName.lower() == "eclipse":
		RemoveEclipseProjectFiles(rootDir)

