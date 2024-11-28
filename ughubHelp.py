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

import ughubUtil
import ughubHelpContents


class MalformedHelpContentsError(Exception) : pass

def get_help_entry(entry):
    return ughubUtil.get_from_nested_table(ughubHelpContents.content, entry)

def get_commands_in_help():
    try:
        d = get_help_entry("commands")
        out = []

        if type(d) == list:
            for e in d:
                name = e["name"]
                if type(name) == str:
                    out.append(name)
                elif type(name) == list and len(name) > 0:
                    s = name[0]
                    for i in range(1, len(name)):
                        s = s + ", " + name[i]
                    out.append(s)
        else:
            raise MalformedHelpContentsError("'commands' entry has to be a list")
    except ughubUtil.NestedTableEntryNotFoundError as e:
        raise MalformedHelpContentsError("'commands' list required in help contents")

    return out

def is_command_in_help(command):
    try:
        d = get_help_entry("commands")
        if type(d) == list:
            for e in d:
                name = e["name"]
                if type(name) == str and name == command:
                    return True
                elif type(name) == list and command in name:
                    return True                        
        else:
            raise MalformedHelpContentsError("'commands' entry has to be a list")
    except ughubUtil.NestedTableEntryNotFoundError as e:
        raise MalformedHelpContentsError("'commands' list required in help contents")
    return False

def print_usage():
    try:
        print(get_help_entry("usage"))
    except ughubUtil.NestedTableEntryNotFoundError as e:
        raise MalformedHelpContentsError(e)

def print_commands():
    for cmd in get_commands_in_help():
        print("  {0}".format(cmd))

def print_command_names():
    result = ""
    for cmd in get_commands_in_help():
        for c in cmd.split(","):
            result += c.strip() + "\n"    
                
    ughubUtil.write(result[:-1])

# Prints help for the command specified in 'cmd'.
def print_command_help(cmd_name, args=[]): # todo remove [] from default

    short_desc = ughubUtil.has_commandline_option(args, ("--short",))

    try:
        cmd_dict = get_help_entry("commands.{0}".format(cmd_name))

    except ughubUtil.NestedTableEntryNotFoundError:
        raise MalformedHelpContentsError("Requested command '{0}' not found in help database".format(cmd_name))

    if short_desc:
        if "shortdescription" in cmd_dict:
            ughubUtil.write(cmd_dict["shortdescription"])
        return

    print("Usage: ughub {0}".format(cmd_dict["usage"]))
    print()
    for line in cmd_dict["description"].splitlines():
        print("  {0}".format(line))

    try:
        options = ughubUtil.get_from_nested_table(cmd_dict, "options")
    except ughubUtil.NestedTableEntryNotFoundError:
        return

    print()
    print("Valid options:")
    for opt in options:
        name = opt["name"]
        sep = ":"
        for line in opt["description"].splitlines():
            print("  {0:20}{1} {2}".format(name, sep, line))
            name = ""
            sep = " "

def get_option_strings_for_command(command_name):
    result = ""
    try:
        cmd_dict = get_help_entry("commands.{0}".format(command_name))
        
        try:
            options = ughubUtil.get_from_nested_table(cmd_dict, "options")
            
            for opt in options:
                option_strings = opt["name"]

                # filter out [ ]            
                option_strings = option_strings.replace("[", "").replace("]", "")

                # split
                option_strings = option_strings.split(" ")

                # which of those start with - or --?
                option_strings = list(filter(lambda s: s.startswith('-') or s.startswith('--'), option_strings))

                for ss in option_strings:
                    result += ss + "\n"
                
        except ughubUtil.NestedTableEntryNotFoundError:
            pass

    except ughubUtil.NestedTableEntryNotFoundError:
        raise MalformedHelpContentsError("Requested command '{0}' not found in help database"
                                           .format(command_name))

    return result[:-1]

# Prints help on how to use the help command and a list of all available commands
def print_help():
    print_command_help("help")
    print("")
    print("available commands:")
    print_commands()
