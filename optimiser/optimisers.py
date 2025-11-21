#!/usr/bin/env python3

#================================================================================================================#
# Imports
#================================================================================================================#

# Local Imports
import args;
from db import add_run, get_latest_iteration;

from perform_run import create_run, Manager, RunRetObj, Process, Queue;

# Set Datetime in db
from datetime import datetime;
from shutil import copy;
from os.path import join;
from os import getcwd;

#================================================================================================================#
# Optimiser Programs
#================================================================================================================#

def initialValues() -> None:
    """
    Generate `benchmark_res_initial.csv` and `quartus_initial_size` for all other runs - must be run first
    """    
    man = Manager();
    proc, q = create_run(0, [-1, -1], {}, man, False);
    proc.run();
    assert(q.get() == "DONE")
    copy(join(getcwd(), "optimiser_artifacts", "iteration_-1", "run_-1", "quartus_size"), join(getcwd(), "quartus_initial_size"));
    copy(join(getcwd(), "optimiser_artifacts", "iteration_-1", "run_-1", "benchmark_results.csv"), join(getcwd(), "benchmark_res_initial.csv"));

def _sweep(iteration:int, run_params:list[dict[str,int]], runOffset:int = 0):
    # Create Multiprocessing Manager
    man = Manager();

    procs:list[Process] = [];
    qs:list[Queue] = [];

    # Perform initial runs
    for parameterisation, run in zip(run_params, range(len(run_params))):
        proc, q = create_run(run, [iteration, runOffset + run], parameterisation, man);
        procs.append(proc);
        qs.append(q);

    for proc in procs:
        proc.start();
    
    # Don't leave zombies...
    [p.join() for p in procs]

    for q in qs:
        res:RunRetObj = q.get();
        add_run(iteration, datetime.now().isoformat(), res["performance"], res["area"], **(res["params"]));

def initialSweep() -> None:
    """
    Perform an initial sweep of parameters - determine likely candidates for decrease
    """

    # Get Default Parameter Values
    param_defaults:dict[str,int] = args.PARAM_DEFAULTS;
    
    # Create Sweep Permutations
    run_params = [];
    for param in args.PARAMS:
        paramO = args.PARAM_OBJ[param];
        if not (("minimum" in paramO.keys() and paramO["default"] == paramO["minimum"]) or (paramO["default"] == 1)):
            parameterisation = param_defaults.copy();
            parameterisation[param] -= paramO["increment"]; 
            run_params.append(parameterisation);

    _sweep(0, run_params);
    
def incrementSweep() -> None:
    """
    Perform a sweep of the parameters as an iteration
    """
    param_values:dict[str,int] = args.PARAM_VALUES;
    prev_iter = get_latest_iteration()
    # Create Sweep Permutations
    run_params = [param_values]; # Include iteration base values
    for param in args.PARAMS:
        paramO = args.PARAM_OBJ[param];
        if not (("minimum" in paramO.keys() and param_values[param] - paramO["increment"] < paramO["minimum"]) or (param_values[param] - paramO["increment"] < 1)):
            parameterisation = param_values.copy();
            parameterisation[param] -= paramO["increment"]; 
            run_params.append(parameterisation);

    # Perform Sweep
    _sweep(prev_iter + 1, run_params);


#================================================================================================================#
# Definition Checking
# 
# - All optimisers must be included in dict `_optimisers` in `args.py` to be able to be called from the master script
# - The below will print a warning to stderr if this is not met
#================================================================================================================#

from sys import modules
from debug import printf_err

# Get all global variable names in this file
for objName in dir(modules[__name__]):
    # Only check exports - using "_" convention for private values
    if objName.startswith("_"):
        # Get the value associated with the variable, and restrict to checking functions only
        obj = getattr(modules[__name__], objName)
        if callable(obj):
            # Check the function is actually declared in this module
            if __name__ == obj.__module__:
                # Print an error message if the optimiser function is not declared in `args.py`
                if not (objName in args._optimisers.keys()):
                    printf_err(f"Optimiser `{objName}()` has not been added to args.py _optimisers - this optimiser will remain unavailable until this is done")