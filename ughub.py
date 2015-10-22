#! /usr/bin/env python

# copyright 2015 Sebastian Reiter (G-CSC Frankfurt)

# standard library imports
import json
import os
import re
import sys

import ughubHelp


def ParseArguments(args):
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
		print("")

	else:
		ughubHelp.PrintUsage()


ParseArguments(sys.argv[1:])
