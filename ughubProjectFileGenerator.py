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

import codecs
import collections
import os

PathNode = collections.namedtuple("PathTypePair", "path type ignore")

def list_paths(path):
    paths_out = []
    files = os.listdir(path)
    for file in files:
        file_name = os.path.join(path, file)
        if os.path.isdir(file_name):
            paths_out.append(file)
    return paths_out

def get_eclipse_project_paths(root_dir):
    dirs = [PathNode(root_dir, "root", ["apps", "externals", "plugins", "ugcore"]),
            PathNode(os.path.join(root_dir, "ugcore"), "leaf", [])]

    for root_subdirectories in ("apps", "externals", "plugins"):
        full_path = os.path.join(root_dir, root_subdirectories)
        leafs = list_paths(full_path)
        dirs.append(PathNode(full_path, "subroot", leafs))
        for leaf in leafs:
            dirs.append(PathNode(os.path.join(full_path, leaf), "leaf", []))

    return dirs

def generate_eclipse_project_files(root_dir, project_name, overwrite_files):
    local_dir = os.path.dirname(os.path.realpath(__file__))
    template_leaf = codecs.open(os.path.join(local_dir, "project_templates/eclipse-leaf"), "r", "utf-8").read()
    template_root = codecs.open(os.path.join(local_dir, "project_templates/eclipse-root"), "r", "utf-8").read()
    template_filter = codecs.open(os.path.join(local_dir, "project_templates/eclipse-filter"), "r", "utf-8").read()
    template_cproject = codecs.open(os.path.join(local_dir, "project_templates/eclipse-cproject"), "r", "utf-8").read()

    path_nodes = get_eclipse_project_paths(root_dir)
    for pn in path_nodes:
        filename = os.path.join(pn.path, ".project")
        if (not (overwrite_files or pn.type == "subroot")) and os.path.isfile(filename):
            continue

        if project_name and (pn.type == "root"):
            pname = project_name
        else:
            pname = os.path.basename(pn.path)

        if (pn.type == "root") or (pn.type == "subroot"):
            filters = ""
            for p in pn.ignore:
                filters = filters + template_filter.replace("$IGNOREPATH$", p)
            template = template_root.replace("$FILTERS$", filters)

        elif pn.type == "leaf":
            template = template_leaf
            codecs.open(os.path.join(pn.path, ".cproject"), "w", 'utf-8', errors="replace").write(template_cproject)

        file_contents = template.replace("$PROJECTNAME$", pname)
        codecs.open(filename, "w", 'utf-8', errors="replace").write(file_contents)

    print(    "Eclipse project files generated.")
    print(    "Execute the following steps to import or update your project in Eclipse:")
    print(    "  - Open Eclipse,\n"
            "  - Click 'File->Import...->General->Existing Project Into Workspace'\n"
            "  - Choose ug4's root directory, and enable the options 'Search for nested projects'\n"
            "    and 'Hide projects that already exist in the workspace'.\n"
            "  - From Eclipse MARS on (Eclipse v4.5) you may activate the option\n"
            "    'Project Presentation->Hierarchical' in the dropdown menu of the 'Project Explorer'.")

def remove_eclipse_project_files(root_dir):
    path_nodes = get_eclipse_project_paths(root_dir)
    for pn in path_nodes:
        for f in (".project", ".cproject"):
            filename = os.path.join(pn.path, f)
            if os.path.isfile(filename):
                os.remove(filename)

    print("Eclipse project files deleted.")

def run(root_dir, target_name, project_name, overwrite_files):
    if target_name.lower() == "eclipse":
        generate_eclipse_project_files(root_dir, project_name, overwrite_files)

def remove_files(root_dir, target_name):
    if target_name.lower() == "eclipse":
        remove_eclipse_project_files(root_dir)

