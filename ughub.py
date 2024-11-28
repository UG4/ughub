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

# v1.0.1:    Supporting 'include' statement in packages.json files.
# v1.0.2:    Various improvements. Most notably auto-detection of outdated remotes
#            and full support for python 2.6, 2.7, and 3. Furthermore,
#            project-file-generation for Eclipse has been added.
g_ughub_version_string = "2025.1.0"

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

ughub_directory_name = ".ughub"
sources_file_name = "sources.json"
packages_file_name = "packages.json"

PackageBranchPair = collections.namedtuple("PackageBranchPair", "package branch")

# returns True if the first version number is smaller or equal to the second, False if not.
def compare_versions(version_string_a, version_string_b):
    nums0 = version_string_a.split(".")
    nums1 = version_string_b.split(".")
    for v0, v1 in zip(nums0, nums1):
        if int(v0) > int(v1):
            return False
        if int(v0) < int(v1):
            return True
    return True

# This text is shown when the application terminates. Methods may append
# warning and error messages to this string.
# Use AppendToExitText to append your messages
g_exit_text = ""
def append_to_exit_text(text):
    global g_exit_text
    g_exit_text = g_exit_text + text

def get_root_directory(path=None):
    """
        Recursively finds the root directory containing a specific base directory.

        This function starts at the given `path` (or the current working directory if no path is provided)
        and traverses upwards in the directory tree until it finds a directory containing
        a `.ughub` directory. If the base directory is not found, a `NoRootDirectoryError` is raised.

        :arg:
            path (str, optional): The starting directory. If None, the current working directory is used.

        :returns:
            str: The absolute path of the root directory containing the base directory.

        :raises:
            NoRootDirectoryError: If no root directory containing the base directory is found.

        :example:
            >>> get_root_directory("/home/user/projects/my_project/subfolder")
            '/home/user/projects/'
        """
    current_directory = path or os.getcwd()
    while True:
        if os.path.isdir(os.path.join(current_directory, ughub_directory_name)):
            return current_directory
        next_directory = os.path.dirname(current_directory)
        if next_directory == current_directory:
            raise NoRootDirectoryError()
        current_directory = next_directory

def get_ughub_directory(path=None):
    return os.path.join(get_root_directory(path), ughub_directory_name)

def generate_default_source_file(path=None):
    target_path = get_ughub_directory(path)

    sources = [{ "name": "github-ug4",
                 "url": "https://github.com/UG4/ug4-packages.git",
                 "branch": "master"}] # todo change to main

    write_sources(sources, target_path)

def generate_cmakelists(path=None):
    filename = os.path.join(get_root_directory(path), "CMakeLists.txt")
    print("Generating '{0}'".format(filename))
    f = open(filename, "w")
    f.write("# WARNING: PLEASE DO NOT CHANGE THIS FILE (any changes may be lost)\n")
    f.write("# This file was automatically generated and may be overwritten without notice.\n")
    f.write("\n")
    f.write("cmake_minimum_required(VERSION 3.5)\n")
    f.write("project(UG4)\n")
    f.write("if(IS_DIRECTORY ${CMAKE_SOURCE_DIR}/ugcore)\n")
    f.write("    add_subdirectory(ugcore)\n")
    f.write("else()\n")
    f.write("    message(FATAL_ERROR \"Please install the 'ugcore' package using 'ughub install ugcore'.\")\n")
    f.write("endif()\n")
    f.close()
    return 
    # todo write file as one block / copy raw cmake file from resource folder 
    f = open(filename, "w")
    f.write("""# WARNING: PLEASE DO NOT CHANGE THIS FILE (any changes may be lost)\n
    # This file was automatically generated and may be overwritten without notice.\n
    \n
    cmake_minimum_required(VERSION 3.5)\n
    project(UG4)\n
    if(IS_DIRECTORY ${CMAKE_SOURCE_DIR}/ugcore)\n
        add_subdirectory(ugcore)\n
	else()\n
	    message(FATAL_ERROR \"Please install the 'ugcore' package using 'ughub install ugcore'.\")\n
	endif()\n""")
    f.close()

def initialize_directory(args):
    force = ughubUtil.has_commandline_option(args, ("-f", "--force"))


    root_path = os.getcwd()
    if len(args) > 0 and args[0][0] != '-':
        if os.path.isabs(args[0]):
            root_path = args[0]
        else:
            root_path = os.path.join(root_path, args[0])
    print("root path: {0}".format(root_path))
    ughub_path = os.path.normpath(os.path.join(root_path, ughub_directory_name))
    if os.path.isdir(ughub_path):
        if os.path.isfile(os.path.join(ughub_path, sources_file_name)):
            print("Directory '{0}' has been initialized already.".format(ughub_path))
            return
    else:
        try:
            existing_root_dir = get_root_directory(ughub_path)
            if not force:
                print("Warning: Found ughub root directory at: {0}".format(existing_root_dir))
                print("call 'ughub init -f' to force initialization in this path.")
                return

        except NoRootDirectoryError:
            pass

        # this is actually the expected case
        os.makedirs(ughub_path)

    generate_default_source_file(ughub_path)
    update_sources(ughub_path)
    generate_cmakelists(root_path)
    print("initialized ughub directory at '{0}'".format(root_path))

def repair():
    try:
        load_sources()
    except InvalidSourceError:
        print(f"Restoring default '{sources_file_name}' file.")
        generate_default_source_file()
        update_sources()

    generate_cmakelists()

def write_sources(sources, path=None):
    path = get_ughub_directory(path)
    with open(os.path.join(path, sources_file_name), "w") as outfile:
        json.dump(sources, outfile, indent = 4)

def print_source(s):
    print("  {0:8}: '{1}'".format("name", s["name"]))
    print("  {0:8}: '{1}'".format("branch", s["branch"]))
    print("  {0:8}: '{1}'".format("url", s["url"]))

def add_source(args):
    if len(args) < 2 or args[0][0] == "-" or args[1][0] == "-":
        print("ERROR in addsource: Invalid arguments specified. See 'ughub help addsource'.")
        return

    name = args[0]
    url = args[1]
    sources = load_sources()
    branch = ughubUtil.get_commandline_option_value(args, ("-b", "--branch")) or "master" # todo change to main
    new_source = { "name": name,
                   "url": url,
                   "branch": branch}

    for s in sources:
        if s["name"] == name:
            print("ERROR in addsource: A source with name '{0}' exists already".format(name))
            return

    try:
        update_source(new_source)

    except InvalidSourceError as e:
        print("WARNING: Requested source was not added due to errors:")
        print_source(new_source)
        raise e

    sources.append(new_source)
    write_sources(sources)
    print("The following source was added at rank {0}:".format(len(sources)))
    print_source(new_source)

def load_sources(path=None):
    path = get_ughub_directory(path)
    try:
        return json.loads(open(os.path.join(path, sources_file_name)).read())
    except IOError:
        raise InvalidSourceError("No '{0}/{1}' file found. Please call 'ughub  repair' to generate a new {1} file." .format(path,sources_file_name))

def validate_source_names(sources):
    try:
        names = []
        for src in sources:
            source_name = src["name"]
            if source_name in names:
                raise InvalidSourceError("duplicate source name: {0}".format(source_name))
            else:
                # todo:    check name for invalid characters (e.g. '.')
                names.append(source_name)

    except LookupError as e:
        raise InvalidSourceError("lookup of field '{0}' failed.".format(e))

def update_source(src, path=None):
    # check for each source whether it was already installed. if that's the case,
    # perform git pull on that directory. If not, perform git clone.
    ughub_dir = get_ughub_directory(path)
    sources_dir = os.path.join(ughub_dir, "sources")
    if not os.path.isdir(sources_dir):
        os.mkdir(sources_dir)

    try:
        name = src["name"]
        url = transform_ssh(src["url"])
        branch = src["branch"]

        src_dir = os.path.join(sources_dir, name)

        if not os.path.isdir(src_dir):
            print("Cloning source '{0}', branch '{1}' from '{2}'".format(name, branch, url))
            proc = subprocess.Popen(["git", "clone", "--branch", branch, url, name], cwd = sources_dir)
            if proc.wait() != 0:
                raise InvalidSourceError("Couldn't clone source '{0}' with branch '{1}' from '{2}'"
                                         .format(name, branch, url))
        else:
            print("Updating source '{0}' (branch '{1}') from '{2}'".format(name, branch, url))
            proc = subprocess.Popen(["git", "pull"], cwd = src_dir)
            if proc.wait() != 0:
                raise InvalidSourceError("Couldn't pull from '{1}' (branch '{0}') for source '{2}'"
                                         .format(branch, url, name))

    except LookupError as e:
        raise InvalidSourceError("lookup of field '{0}' failed.".format(e))


def update_sources(path=None):
    sources = load_sources(path)
    validate_source_names(sources)
    for src in sources:
        update_source(src, path)


def list_sources():
    sources = load_sources()
    print("List of known sources:")
    first_one = True
    for s in sources:
        if not first_one:
            print("")
        first_one = False

        try:
            print_source(s)

        except LookupError as e:
            raise InvalidSourceError("lookup of field '{0}' failed.".format(e))


def load_package_descs_from_file(filename, source_name):
    packages_out = []
    try: # todo simplify block try-try ?
        try:
            content = json.loads(open(filename).read())
            if "minUGHubVersion" in content:
                if not compare_versions(content["minUGHubVersion"], g_ughub_version_string):
                    raise InvalidSourceError("ughub version '{0}' required but current version is '{1}'"
                                             .format(content["minUGHubVersion"], g_ughub_version_string))

            if "include" in content:
                current_dir = os.path.dirname(filename)
                for include_file in content["include"]:
                    packages_out = packages_out + load_package_descs_from_file(os.path.join(current_dir, include_file), source_name)

            if "packages" in content:
                for pkgDesc in content["packages"]:
                    pkgDesc["__SOURCE"] = source_name
                    packages_out.append(pkgDesc)

        except LookupError as e:
            raise InvalidSourceError("Failed to access {0} in '{1}'".format(e, filename))
        except IOError:
            raise InvalidSourceError("Package descriptor file of source '{0}' not found: '{1}'. "
                                     "Please call 'ughub updatesources'.".format(source_name, filename))

    except LookupError:
        raise InvalidSourceError("couldn't find field 'name'")
    except ValueError as e:
        raise InvalidSourceError("couldn't parse file '{0}': {1}".format(filename, e))

    return packages_out


# returns a list with all available package descriptors
# adds a 'source' entry to each desc which contains the name of the package source
# sourceName is an optional parameter. If specified only the source with the given name
# is considered. If source_name is None (by default), packages from all sources are loaded.
def load_package_descs(source_name = None):
    sources = load_sources()
    sources_directory = os.path.join(get_ughub_directory(), "sources")
    packages_out = []
    errors = ""
    
    for src in sources:
        if source_name is None or source_name == src["name"]:
            source_name = src["name"]
            source_dir = os.path.join(sources_directory, source_name)
            package_desc_name = os.path.join(source_dir, packages_file_name)

            try:
                packages_out = packages_out + load_package_descs_from_file(package_desc_name, source_name)

            except InvalidSourceError as e:
                errors = errors + "Error in source '{0}':\n  {1}\n".format(source_name, e)

    if len(errors) > 0:
        append_to_exit_text("WARNING: Problems occurred during 'load_package_descs':\n" + errors)

    return packages_out


def filter_packages_any(packages, categories):
     filtered_packages = []
     for pkg in packages:
          try:
               pkgcats = ughubUtil.get_from_nested_table(pkg, "categories")
               if any(pcat in categories for pcat in pkgcats):
                    filtered_packages.append(pkg)

          except ughubUtil.NestedTableEntryNotFoundError:
               pass
     return filtered_packages


def filter_packages_all(packages, categories):
     filtered_packages = []
     for pkg in packages:
          try:
               pkgcats = ughubUtil.get_from_nested_table(pkg, "categories")
               if all(cat in pkgcats for cat in categories):
                    filtered_packages.append(pkg)

          except ughubUtil.NestedTableEntryNotFoundError:
               pass
     return filtered_packages


def load_filtered_package_descs(args):
    categories = []
    match_all = ughubUtil.has_commandline_option(args, ("-a", "--matchall"))
    installed = ughubUtil.has_commandline_option(args, ("-i", "--installed"))
    notinstalled = ughubUtil.has_commandline_option(args, ("-n", "--notinstalled"))
    sourceName = ughubUtil.has_commandline_option(args, ("-s", "--source"))

    for arg in args:
        if arg[0] != "-":
            categories.append(arg)
        else:
            break

    try:
        all_packages = load_package_descs(sourceName)

        if len(all_packages) == 0:
            return all_packages

        packages = []

        # select according to installed/notinstalled
        if installed and notinstalled:
            print("Cannot use --installed and --notinstalled simultaneously.")
            raise Exception()

        if installed:
            for pkg in all_packages:
                if package_is_installed(pkg):
                    packages.append(pkg)

        if notinstalled:
            for pkg in all_packages:
                if not package_is_installed(pkg):
                    packages.append(pkg)

        if not installed and not notinstalled: 
            for pkg in all_packages:
                packages.append(pkg)

        # select according to category
        if match_all:
            packages = filter_packages_all(packages, categories)
        elif len(categories) > 0:
            packages = filter_packages_any(packages, categories)

        return packages

    except LookupError as e:
        raise InvalidPackageError(e)


def list_packages(args):
    try:
        packages = load_filtered_package_descs(args)

        if len(packages) == 0:
            print("no packages found")
            return

        # sort packages alphabetically
        packageDict = {}
        for pkg in packages:
            packageDict[pkg["name"]] = packageDict.get(pkg["name"], []) + [pkg]

        namesonly = ughubUtil.has_commandline_option(args, ("--namesonly",))

        if namesonly:
            result = ""
            for key in sorted(packageDict.keys()):
                pkgs = packageDict[key]
                for pkg in pkgs:
                    result += pkg["name"] + " "

            ughubUtil.write(result)
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


def short_package_info(pkg):
    s = "  {0:10}: '{1}'".format("name", pkg["name"])
    if "__SOURCE" in pkg:
        s = "\n".join((s, "  {0:10}: '{1}'".format("source", pkg["__SOURCE"])))
    if "__BRANCH" in pkg:
        s = "\n".join((s, "  {0:10}: '{1}'".format("branch", pkg["__BRANCH"])))
    s = "\n".join((s, "  {0:10}: '{1}'".format("url", pkg["url"])))
    s = "\n".join((s, "  {0:10}: '{1}'".format("target", get_package_dir(pkg))))
    return s


def long_package_info(pkg):
    return ughubUtil.nested_table_to_string(pkg)


def print_package_info(args):
    package_list = ughubUtil.remove_options(args)
    if len(package_list) != 1:
        print("Please specify exactly one package name. See 'ughub help packageinfo'")
        return

    package_name = package_list[0]
    packages = load_package_descs()

    first_package = True
    for pkg in packages:
        try:
            if pkg["name"] == package_name:
                if not first_package:
                    print("")
                first_package = False

                print("package '{0}' from source '{1}':"
                      .format(package_name, pkg["__SOURCE"]))
                if ughubUtil.has_commandline_option(args, ("-s", "--short")):
                    print(short_package_info(pkg))
                else:
                    print(long_package_info(pkg))

        except LookupError:
            raise InvalidSourceError("Failed to access package list in '{0}'"
                                     .format(package_name))


def get_package_dir(pkg):
    return os.path.join(get_root_directory(), pkg["prefix"], pkg["name"])


# returns a list of package descriptors that have to be installed for a given package.
# note that this list may contain packages that are already installed.
def build_package_dependency_list(package_name, available_packages, source=None,
                               branch=None, processed_package_branch_pairs=[], # todo ersätta lista
                               nodeps = False):
    packages_out = []

    got_one = False
    for pkg in available_packages:
        if pkg["name"] == package_name and (source is None or source == pkg["__SOURCE"]):
            try:
                got_one = True
                use_branch = branch or pkg["defaultBranch"]

                for processed_pbp in processed_package_branch_pairs:
                    if processed_pbp.package == package_name:
                        if processed_pbp.branch == use_branch:
                            return []
                        else:
                            raise DependencyError("Branch conflict: '{0}' required from branch '{1}' and branch '{2}'.\n"
                                                  "Package list:"
                                                  .format(package_name, use_branch, processed_pbp.branch))

                pkg["__BRANCH"] = use_branch
                packages_out.append(pkg)
                processed_package_branch_pairs.append(PackageBranchPair(package_name, use_branch))

                if not nodeps and "dependencies" in pkg:
                    depends_on = None
                    deps = pkg["dependencies"]
                    for dep in deps:
                        if "branch" in dep:
                            if dep["branch"] == pkg["__BRANCH"]:
                                depends_on = dep
                        else:
                            if depends_on is None:
                                depends_on = dep

                    if depends_on:
                        for dep_pkg in depends_on["packages"]:
                            dep_pkg_name = dep_pkg["name"]
                            dep_pkg_branch = None
                            if "branch" in dep_pkg:
                                dep_pkg_branch = dep_pkg["branch"]

                            packages_out = packages_out + build_package_dependency_list(
                                                            dep_pkg_name,
                                                            available_packages,
                                                            None,
                                                            dep_pkg_branch,
                                                            processed_package_branch_pairs)

            except DependencyError as e:
                raise DependencyError("{0}\n\n{1}"
                                     .format(e, short_package_info(pkg)))
    if not got_one:
        raise DependencyError("Required package '{0}' is not available in the current sources.\n"
                              "  Please make sure that all required sources are added to your current\n"
                              "  ughub installation (use 'ughub listsources' and 'ughub addsource')\n"
                              "  and make sure that they are all up to date (use 'ughub updatesources')."
                              .format(package_name))
    return packages_out


#    Returns the fetch and pull urls of the git repository of the specified package as strings.
#    If no corresponding remote-urls are found, None is returned for each return value.
def get_current_remote_git_urls(pkg, origin = "origin"):
    root_dir = get_root_directory()
    origin_fetch_url = None
    origin_push_url = None
    if pkg["repoType"] == "git":
        #prefix_path = os.path.join(root_dir, pkg["prefix"])
        #pkg_path = os.path.join(prefix_path, pkg["name"])
        pkg_path = os.path.join(root_dir, pkg["prefix"], pkg["name"])
        if os.path.isdir(os.path.join(pkg_path, ".git")):
            origin_fetch_url, origin_push_url = get_repository_urls(pkg_path,pkg["name"])

    return origin_fetch_url, origin_push_url

def transform_ssh(package):
    """
    Transforms an HTTPS package URL to an SSH URL format if applicable.

    :param package: The package URL to be transformed.
    :type package: str
    :return: The transformed URL in SSH format if the input starts with 'https://';
             otherwise, the original URL.
    :rtype: str

    :example:
    >>> transform_ssh("https://github.com/user/repo.git")
    'git@github.com:user/repo.git'

    >>> transform_ssh("git@github.com:user/repo.git")
    'git@github.com:user/repo.git'
    """
    package_url = package
    if package_url.startswith("https://"):
        parts = package_url.split("/")
        identifier = "/".join(parts[3:]) # todo check len(parts) and throw error/use monade
        package_url = "git@" + parts[2] + ":" + identifier
    return package_url

def get_submodules(package, prefix_path):
    """
    Initializes and updates the Git submodules for a given repository.

    :param package: (dict) Information about the package, including the "name" key.
    :param prefix_path: (str) Path to the Git repository.

    :raises: TransactionError: If submodule initialization or update fails.
    """
    print()
    submodule_file = os.path.join(prefix_path, ".gitmodules")
    if os.path.isfile(submodule_file):
        proc = subprocess.Popen(["git", "submodule", "init"], cwd=prefix_path)
        if proc.wait() != 0:
            raise TransactionError(f"Couldn't initialize submodules '"+package["name"]+"'")

        proc = subprocess.Popen(["git", "submodule", "update"], cwd=prefix_path)
        if proc.wait() != 0:
            raise TransactionError(f"Couldn't update submodules '"+package["name"]+"'")

def install_package(args):
    package_names = args
    options = []

    for i in range(len(args)):
        if args[i][0] == "-":
            package_names = args[0:i]
            options = args[i:]
            break

    if len(package_names) == 0:
        print("Please specify a package name. See 'ughub help install'.")
        return

    dry_run = ughubUtil.has_commandline_option(options, ("-d", "--dry"))
    ignore = ughubUtil.has_commandline_option(options, ("-i", "--ignore"))
    resolve = ughubUtil.has_commandline_option(options, ("-r", "--resolve"))
    noupdate = ughubUtil.has_commandline_option(options, ("--noupdate",))
    nodeps = ughubUtil.has_commandline_option(options, ("--nodeps",))
    branch = ughubUtil.get_commandline_option_value(options, ("-b", "--branch"))
    source = ughubUtil.get_commandline_option_value(options, ("-s", "--source"))
    packages = load_package_descs()
    root_directory = get_root_directory()

    required_packages = []
    processed_package_branch_pairs = []

    for package_name in package_names:
        required_packages = (required_packages + build_package_dependency_list(package_name, packages, source, branch,
                                                                               processed_package_branch_pairs, nodeps))

    print("List of required packages:")

    #0: Message, 1: Package name, 2: current remote, 3: required remote
    text_remote_conflict_uf = (""
        "{0}: Url of remote 'origin' of package '{1}' does not correspond\n"
        "  to the current source-definition:\n"
        "  current URL: '{2}'\n"
        "  expected URL: '{3}'\n"
        "  This is most likely a result of an updated source-definition (e.g. through 'ughub updatesources').")

    #0: required remote, 2: package-path
    text_remote_conflict_options_uf = (""
        "  You may\n"
        "    - call 'ughub install ...' with the '--resolve' option to resolve conflicts on the fly.\n"
        "    - manually adjust the url by executing\n"
        "      'git remote set-url origin {0}'\n"
        "      at '{1}'\n"
        "    - call 'ughub install ...' with the '--ignore' option to perform installation despite this\n"
        "      error. This may result in an outdated package and build conflicts!")

    #0: Message, 1: Package name, 2: current branch, 3: required branch
    text_branch_conflict_uf = (""
        "{0}: Current branch '{2}' of installed package '{1}' "
        "does not correspond to the required branch '{3}'.")

    #0: required branch, 2: package-path
    text_branch_conflict_options_uf = (""
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

    first_package = True
    problems_occurred = False
    for pkg in required_packages:
        if not first_package:
            print("")
        first_package = False
        print(short_package_info(pkg))

    #    check whether the package is already installed
        if pkg["repoType"] == "git":
            prefix_path = os.path.join(root_directory, pkg["prefix"])
            pkg_path = os.path.join(prefix_path, pkg["name"])
            if os.path.isdir(os.path.join(pkg_path, ".git")):
            #    The package exists. validate its origin.
                fetch_url, push_url = get_current_remote_git_urls(pkg)
                if fetch_url != pkg["url"] or push_url != pkg["url"]:
                    if fetch_url != pkg["url"]:
                        wrong_url = fetch_url
                    if push_url != pkg["url"]:
                        wrong_url = push_url

                    problems_occurred = True
                    if resolve:
                        print(text_remote_conflict_uf.format("NOTE", pkg["name"], wrong_url, pkg["url"]))
                        print("NOTE: The remote will be automatically adjusted (--resolve)")
                        if not dry_run:
                            proc = subprocess.Popen(["git","remote","set-url","origin", pkg["url"]], cwd = pkg_path)
                            if proc.wait() != 0:
                                raise TransactionError("Couldn't set url '{0}' of remote 'origin' for package '{1}' at '{2}'"
                                                        .format(pkg["url"], pkg["name"], pkg_path))
                    elif ignore:
                        print(text_remote_conflict_uf.format("WARNING", pkg["name"], wrong_url, pkg["url"]))
                        print("NOTE: The warning will be ignored (--ignore). "
                              "This may result in an outdated package and build conflicts!")
                    
                    else:
                        text = (text_remote_conflict_uf.format("ERROR", pkg["name"], wrong_url, pkg["url"]) +
                                "\n" + text_remote_conflict_options_uf.format(pkg["url"], pkg_path))
                        if dry_run:
                            print(text)
                        else:
                            raise DependencyError(text)

            #    Validate branch
                p = subprocess.Popen("git branch".split(), cwd = pkg_path, stdout=subprocess.PIPE)
                git_log = p.communicate()[0].decode("utf-8")
                if not p.returncode is None:
                    raise TransactionError("Couldn't access branch information of package '{0}' at '{1}'"
                                            .format(pkg["name"], pkg_path))

                current_branch = None
                for line in git_log.splitlines():
                    if line[0] == "*":
                        current_branch = line.split()[1]
                        break

                if current_branch != pkg["__BRANCH"]:
                    problems_occurred = True
                    if resolve:
                    #todo: call git-fetch, or else checkout may fail or may be outdated.
                        print(text_branch_conflict_uf.format("NOTE", pkg["name"], current_branch, pkg["__BRANCH"]))
                        print("NOTE: The required branch will be automatically checked out (--resolve)")
                        if not dry_run:
                            proc = subprocess.Popen(["git", "checkout", pkg["__BRANCH"]], cwd = pkg_path)
                            if proc.wait() != 0:
                                raise TransactionError("Trying to resolve branch conflict but couldn't check "
                                                        "out branch '{0}' of package '{1}' at '{2}'"
                                                        .format(pkg["__BRANCH"], pkg["name"], pkg_path))
                    elif ignore:
                        print(text_branch_conflict_uf.format("WARNING", pkg["name"], current_branch, pkg["__BRANCH"]))
                        print("NOTE: The warning will be ignored (--ignore). This may result in build problems!")

                    else:
                        text = (text_branch_conflict_uf.format("ERROR", pkg["name"], current_branch, pkg["__BRANCH"]) +
                                "\n" + text_branch_conflict_options_uf.format(pkg["__BRANCH"], pkg_path))
                        if dry_run:
                            print(text)
                        else:
                            raise DependencyError(text)

                if not (dry_run or noupdate):
                # todo: only perform pull if not in detached head state
                    proc = subprocess.Popen(["git", "pull"], cwd = pkg_path)
                    if proc.wait() != 0:
                        raise TransactionError("Couldn't pull for package '{0}' at '{1}'"
                                                .format(pkg["name"], pkg_path))
                elif noupdate:
                    print("NOTE: Package won't be updated due to 'noupdate' option. "
                          "This may lead to build conflicts and errors.")

            else:
            #    the package doesn't exist yet. Make sure that all paths are set up correctly
            #    and perform a clone
                if os.path.exists(pkg_path):
                    try:
                        if not os.path.isdir(pkg_path):
                            raise TargetError("Target path '{0}' for package '{1}' exists but is not a directory"
                                               .format(pkg_path, pkg["name"]))
                        if os.listdir(pkg_path):
                            raise TargetError("Target path '{0}' for package '{1}' has to be empty or a valid git working copy."
                                              .format(pkg_path, pkg["name"]))
                    except TargetError as e:
                        if dry_run:
                            print("WARNING: {0}".format(e))
                            problems_occurred = True
                        else:
                            raise e

                if not dry_run:
                    if not os.path.exists(pkg_path):
                        os.makedirs(pkg_path)
                    package_url = transform_ssh(pkg["url"])

                    proc = subprocess.Popen(["git", "clone", "--branch", pkg["__BRANCH"], pkg["url"], pkg["name"]], cwd = prefix_path)
                    if proc.wait() != 0:
                        raise TransactionError("Couldn't clone package '{0}' with branch '{1}' from '{2}'"

                                                .format(pkg["name"], pkg["__BRANCH"], package_url))

                    module_path = os.path.join(prefix_path, pkg["name"])
                    get_submodules(pkg, module_path)
        else:
            raise InvalidPackageError("Unsupported repository type of package '{0}': '{1}'"
                                         .format(pkg["name"], pkg["repoType"]))

    if dry_run:
        print("Dry run. Nothing was installed/updated.")
        if problems_occurred:
            print("WARNING: problems were detected during dry installation run. See above.")
        return

def install_all_packages(args):
    source = ughubUtil.get_commandline_option_value(args, ("-s", "--source"))
    packages = load_filtered_package_descs(args)
    names = []

    for pkg in packages:
        names.append(pkg["name"])

    is_option = False
    for arg in args:
        if is_option or arg[0] == "-":
            is_option = True
            names.append(arg)

    install_package(names)

def package_is_installed(pkg):
    return os.path.isdir(get_package_dir(pkg))

def call_git_on_package(pkg, git_command, args):
#todo:    check for changes first for 'commit' and 'push', using e.g.
#        git status --porcelain
    print("> {0}".format(get_package_dir(pkg)))

    proc = subprocess.Popen(["git", "--no-pager", git_command] + args, cwd = get_package_dir(pkg), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
                               .format(git_command, pkg["name"], get_package_dir(pkg)))

def cache_git_password():
    # todo:    This currently only works on unix (tested on linux). A version for Windows
    #        and possibly OSX has to be added.
    proc = subprocess.Popen("git config --global credential.helper cache".split())
    if proc.wait() != 0:
        raise TransactionError("Couldn't enable password caching! Please check your git version.")

def call_git_on_packages(args, git_command):
    packages = load_package_descs()

    fails = []
    first_package = True

    specified_packages = []

    # get the argument separator "---"
    gitargs = args
    for i in range(len(args)):
        if args[i] == "---":
            gitargs = args[0:i]
            specified_packages = args[i+1:]
            break

    try:
        cache_git_password()
    except TransactionError as e:
        print("WARNING:\n  " + str(e))

    if len(specified_packages) > 0:
        for pname in specified_packages:
            if not first_package:
                print("")
            first_package = False

            try:
                pkg = ughubUtil.get_from_nested_table(packages, pname)
                if not package_is_installed(pkg):
                    raise InvalidPackageError("Package '{0}' is not installed. See 'ughub help install'".format(pname))

                try:
                    call_git_on_package(pkg, git_command, gitargs)
                except TransactionError as e:
                    fails.append(str(e))

            except ughubUtil.NestedTableEntryNotFoundError:
                fails.append("Unknown package '{0}'".format(pname))

    else:
    #    check for each known package whether it is installed. If this is the case, perform a pull
        for pkg in packages:
            if package_is_installed(pkg):
                if not first_package:
                    print("")
                first_package = False

                try:
                    call_git_on_package(pkg, git_command, gitargs)
                except TransactionError as e:
                    fails.append(str(e))

    if len(fails) > 0:
        msg = "The following errors occurred while performing 'git {0}':".format(git_command)
        for e in fails:
            msg = msg + "\n  - " + e

        raise TransactionError(msg)

def package_logs(args):
    num = "10"
    newargs = ["---"]
    ignore_entries = 0
    for i in range(len(args)):
        if ignore_entries > 0:
            ignore_entries = ignore_entries - 1
        else:
            if args[i] == "-n":
                num = args[i+1]
                ignore_entries = 1
            else:
                newargs = newargs + [args[i]]

    call_git_on_packages(["-n", num, "--pretty=format:* %an (%ad | %h)%n  \"%s\""] + newargs, "log")

def generate_project_files(args):
    options = []
    for i in range(len(args)):
        if args[i][0] == "-":
            options = args[i:]
            args = args[0:i]
            break

    if len(args) < 1:
        raise ArgumentError("Please specify a TARGET.")

    name = ughubUtil.get_commandline_option_value(args, ("-n", "--name"))
    overwrite_files = ughubUtil.has_commandline_option(options, ("-o", "--overwrite"))
    delete_files = ughubUtil.has_commandline_option(options, ("-d", "--delete"))

    if delete_files:
        ughubProjectFileGenerator.remove_files(get_root_directory(), args[0])
    else:
        ughubProjectFileGenerator.run(get_root_directory(), args[0], name, overwrite_files)

def get_auto_completions(args):

    if len(args) >= 1 and args[0] == "install":
        try:
            packages = load_package_descs()
        except:
            return
        result = ughubHelp.get_option_strings_for_command("install")
        result += "\n"
        for p in packages:
            result += p["name"] + "\n"
        
        ughubUtil.write(result[:-1])
        
        return

    if len(args) >= 1 and args[0] == "log":
        try:
            packages = load_package_descs()
        except:
            return
        result = ughubHelp.get_option_strings_for_command("log")
        result += "\n"
        for p in packages:
            if package_is_installed(p):
                result += p["name"] + "\n"

        ughubUtil.write(result[:-1])
        return

    if len(args) >= 1 and args[0] == "help":
        ughubHelp.print_command_names()        
        ughubUtil.write("\n" + ughubHelp.get_option_strings_for_command(args[0]))
        return
    
    if len(args) >= 1 and ughubHelp.is_command_in_help(args[0]):
        ughubUtil.write(ughubHelp.get_option_strings_for_command(args[0]))    
        return

    if len(args) == 1:
        ughubHelp.print_command_names()
        return 

def get_repository_urls(path, name):
    origin_fetch_url = None
    origin_push_url = None

    p = subprocess.Popen(["git", "remote", "-v"], cwd=path, stdout=subprocess.PIPE)
    if not p.returncode is None:
        raise TransactionError("Couldn't access remote information of package '{0}' at '{1}'".format(name, path))

    git_log = p.communicate()[0].decode("utf-8")

    for line in git_log.splitlines():
        m = re.match(r"^origin\s+(.+?)\s+\(fetch\)$", line)
        if m:
            origin_fetch_url = m.group(1)
        m = re.match(r"^origin\s+(.+?)\s+\(push\)$", line)
        if m:
            origin_push_url = m.group(1)

    return  origin_fetch_url, origin_push_url

def get_current_branch(path):
    branch = "unknown"
    branch_process = subprocess.Popen(["git", "branch", "--show-current"], cwd=path, stdout=subprocess.PIPE)
    stdout = branch_process.communicate()

    if len(stdout) > 0:
        branch = stdout[0].decode('utf-8').strip()

    return branch

def self_update():
    print("---------------")
    package_name = "ughub"
    raw_script_path = __file__
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    print(f"ughub-directory: {script_dir}")
    branch = get_current_branch(script_dir)
    print("ughub-branch:", branch)

    fetch_url, push_url = get_repository_urls(script_dir, package_name)

    proc = subprocess.Popen(["git", "pull"], cwd=script_dir)
    if proc.wait() != 0:
        raise InvalidSourceError("Couldn't pull from '{1}' (branch '{0}') for source '{2}'"
                                 .format(branch, fetch_url, package_name))


def run_ughub(args):
    exit_code = 1

    try:
        print(f"ughub version: {g_ughub_version_string}")
        print(f"Python version: {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}")

        if args is None or len(args) == 0:
            ughubHelp.print_usage()
            return

        cmd = args[0]

        if cmd == "addsource":  # (ø) checked
            add_source(args[1:])

        elif cmd == "help":  # (ø) checked
            if len(args) == 1:
                ughubHelp.print_help()
            elif args[1] == "--commands":
                ughubHelp.print_command_names()
            else:
                ughubHelp.print_command_help(args[1], args[2:])

        elif cmd == "genprojectfiles":
            generate_project_files(args[1:])

        elif cmd == "git":  # (ø) checked
            call_git_on_packages(args[2:], args[1])

        # deprecated todo: remove (ø)
        # elif cmd == "gitadd":
        #    raise Exception("gitadd is no longer supported. Please call 'ughub git add' instead.")
        #
        # elif cmd == "gitcommit":
        #     raise Exception("gitcommit is no longer supported. Please call 'ughub git commit' instead.")
        #
        # elif cmd == "gitpull":
        #    raise Exception("gitpull is no longer supported. Please call 'ughub git pull' instead.")
        #
        # elif cmd == "gitpush":
        #    raise Exception("gitpush is no longer supported. Please call 'ughub git push' instead.")
        #
        # elif cmd == "gitstatus":
        #    raise Exception("gitstatus is no longer supported. Please call 'ughub git status' instead.")
        
        elif cmd == "init": # (ø) checked
            initialize_directory(args[1:])

        elif cmd == "install": # (ø) checked
            install_package(args[1:])

        elif cmd == "installall":
            install_all_packages(args[1:])

        elif cmd == "packageinfo":
            print_package_info(args[1:])

        elif cmd in ["list", "listpackages"]:
            list_packages(args[1:])

        elif cmd == "log":
            package_logs(args[1:])

        elif cmd == "repair":
            repair()

        elif cmd == "listsources":
            list_sources()

        elif cmd == "updatesources":
            update_sources()

        elif cmd == "selfupdate":
            self_update()

        elif cmd in ("version", "--version"):
            print("ughub, version {}".format(g_ughub_version_string))
            print("Copyright 2015 G-CSC, Goethe University Frankfurt")
            print("All rights reserved")
        
        elif cmd == "getcompletions":
            get_auto_completions(args[1:])
        
        else:
            print("Unknown command: '{0}'".format(cmd))
            ughubHelp.print_usage()

    except ArgumentError as e:
        print("ERROR (bad arguments to '{0}')\n  {1}".format(cmd, e))

    except NoRootDirectoryError:
        print("Couldn't find ughub root directory. Please change directory to a path\n"
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
        exit_code = 0

    print()

    if len(g_exit_text) > 0:
        print(g_exit_text)

    return exit_code

if __name__ == "__main__":
    sys.exit(run_ughub(sys.argv[1:]))
