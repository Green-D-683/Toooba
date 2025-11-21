#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from os import path
from json import loads as load_json
from typing import TypedDict, NotRequired
class Param(TypedDict):
    const:bool;
    default:int;
    minimum:NotRequired[int];
    increment:int;

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

parser.add_argument("--table", type=str, default="toooba_optimisation", help = "Name of the main results table in the database - default `toooba_optimisation`");

#================================================================================================================#
# Toooba Parameters
#================================================================================================================#

(lambda default: parser.add_argument("--param_file", type=str, default = default, help = f"File used to discover Toooba Parameters (must be a json file matching the specification displayed by the default) - default `{default}`")) (f"/{path.join(*(__file__.split(path.sep)[:-1]), "param_sweep.json")}");

def _get_params_obj()->dict[str,Param]:
    with open(parser.parse_args().param_file, "r") as f:
        return {k: v for k, v in load_json("".join(f.readlines())).items() if not v["const"]};

#================================================================================================================#
# Email Arguments
#================================================================================================================#

(lambda default: parser.add_argument("--email_json", type=str, default=default, help = f"JSON object file used to configure email notifications for iteration ends - default `{default}`")) (f"/{path.join(*(__file__.split(path.sep)[:-1]), "email.json")}");

#================================================================================================================#
# Optimiser to run
#================================================================================================================#

# All optimisers declared in `optimisers.py` - will print message to stderr if missing optimisers are found
_optimisers:dict[str,str] = {
    "initialValues": "Generate `benchmark_res_initial.csv` and `quartus_initial_size` for all other runs - must be run first",
    "initialSweep": "Perform an initial sweep of parameters - determine likely candidates for decrease",
    "incrementSweep": "Perform a sweep of the parameters as an iteration on the current values"
}

(lambda default: parser.add_argument("--optimiser", choices=_optimisers.keys(), default = default, help = f"Optimiser to run, call with `--list-optimisers` for details - default `{default}`") )("initialValues")

parser.add_argument("--list_optimisers", "-l", action="store_true", help = "List Available Optimisers and Their Uses")

#================================================================================================================#
# Parse Arguments and setup global values
#================================================================================================================#

parsed_args:Namespace = parser.parse_args()

PARAM_OBJ:dict[str,Param] = _get_params_obj();
PARAMS:list[str] = PARAM_OBJ.keys();
PARAM_DEFAULTS:dict[str,int] = {k:v["default"] for k, v in PARAM_OBJ.items()};
PARAM_VALUES:dict[str,int] = {k:(v["current"] if "current" in v.keys() else v["default"]) for k, v in PARAM_OBJ.items()};

# Handle --list_arguments in a similar manner to --help
if parsed_args.list_optimisers:
    opstrs = [];
    for optimiser in _optimisers:
        opstrs.append(f"""
{optimiser}:
{_optimisers[optimiser]}
""")
    print ("\n-------\n".join(opstrs))
    exit(0);