#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from os import path

parser:ArgumentParser = ArgumentParser( \
    prog = "optimiser.py", \
    description = "(Semi)-Automatically run iterative optimisations for Toooba - aiming for 50% of default size", \
    epilog = "For more details, see $(REPO)/optimiser", \
    add_help = True \
);

#================================================================================================================#
# Debug Mode
#================================================================================================================#

parser.add_argument("-d", "--debug", action="store_true", help = "Enable Debug Printing");

#================================================================================================================#
# Database Arguments
#================================================================================================================#

parser.add_argument("--db_file", type=str, default="optimiser.db", help = "File to be used for the database - default `optimiser.db`");

parser.add_argument("--table", type=str, default="toooba-optimisation", help = "Name of the main results table in the database - default `toooba-optimisation`");

#================================================================================================================#
# Toooba Parameters
#================================================================================================================#

parser.add_argument("--param_file", type=str, default = path.join(path.sep.join((__file__.split(path.sep)[:-2])), "builds", "Resources", "Include_RISCY_Parameters.mk"), help = "File used to discover Toooba Parameters (must be a *.mk file with only `PARAM ?= <default>` definitions for each parameter) - default `$(REPO)/builds/Resources/Include_RISCY_Parameters.mk`");

#================================================================================================================#

parsed_args:Namespace = parser.parse_args()