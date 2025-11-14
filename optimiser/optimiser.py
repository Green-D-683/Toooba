#!/usr/bin/env python3

#================================================================================================================#
# Imports
#================================================================================================================#

# Local Imports
import args;
from db import add_run;
from debug import emailWarn;
from perform_run import create_run, Manager, RunRetObj, Process, Queue

# Set Datetime in db
from datetime import datetime

#================================================================================================================#
# Optimiser Programs
#================================================================================================================#

def initialValues() -> None:
    pass # TODO - generate `benchmark_res_initial.csv` and `quartus_initial_size`

def initialSweep() -> None:
    """
    Perform an initial sweep of parameters - determine likely candidates for decrease
    """

    # Get Default Parameter Values
    param_defaults:dict[str,int] = args.PARAM_DEFAULTS;
    
    # Create Sweep Permutations
    run_params = [ (param_defaults.copy()) for _ in param_defaults.keys()];
    for param, parameterisation in zip(param_defaults.keys(), run_params):
        parameterisation[param] -= 1;

    # Create Multiprocessing Manager
    man = Manager();

    procs:list[Process] = [];
    qs:list[Queue] = [];

    # Perform initial runs
    for parameterisation, run in zip(run_params, range(len(run_params))):
        proc, q = create_run(run, [0, run], parameterisation, man);
        procs.append(proc);
        qs.append(q);

    for proc in procs:
        proc.start();
    
    # Don't leave zombies...
    [p.join() for p in procs]

    for q in qs:
        res:RunRetObj = q.get();
        add_run(0, datetime.now().isoformat(), res["performance"], res["area"], res["params"]);

#================================================================================================================#
# Main Function - runs selected optimiser
#================================================================================================================#

# TODO - add arg for selecting optimiser program from above - and make `main()` below run the selected program

def main() -> None:
    """
    Main Optimiser - this runs within a crash warning handler that will email in the case of a failure - declare the main program here rather than outside
    """
    initialSweep();

#================================================================================================================#
# Call Site for `main()` - Crash Handler `emailWarn`
#================================================================================================================#

if __name__=="__main__":
    emailWarn("optimiser.py", main);


# ! USER_CLK_PERIOD is dummy value passed through to FPGA Synthesis
# ! L1_TLB_SIZE is probably negligible in the provided benchmarks - too small to use VirtMem 

# ! Could add parameter for branch predictor state size - see Btb.bsv and TourPred.bsv