#!/usr/bin/env python3

#================================================================================================================#
# Imports
#================================================================================================================#

# Crash Handler
import traceback;

# Local Imports
import args;
from db import add_run;
import send_email;
from perform_run import create_run, Manager, RunRetObj, Process, Queue

# Set Datetime in db
from datetime import datetime

#================================================================================================================#
# Optimiser Programs
#================================================================================================================#

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
    run = 0;
    for parameterisation, i in zip(run_params, range(len(run_params))):
        proc, q = create_run(i, [0, run], parameterisation, man);
        procs.append(proc);
        qs.append(q);

    for proc in procs:
        proc.start();
    
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
# Call Site for `main()` - Crash Handler
#================================================================================================================#

if __name__=="__main__":
    try:
        # Main program goes here - thus an uncaught exception will trigger an email warning
        main();
        # Testing warning system
        # raise FutureWarning()
    except BaseException as e:
        send_email.send_email(f"FAILURE - `optimiser.py` on {send_email.hostname()}", f"""\
Optimiser Process failed on {send_email.hostname()}:

{str(e)}

Trace:
{traceback.format_exc()}
""");
        raise e;


# ! USER_CLK_PERIOD is dummy value passed through to FPGA Synthesis
# ! L1_TLB_SIZE is probably negligible in the provided benchmarks - too small to use VirtMem 

# ! Could add parameter for branch predictor state size - see Btb.bsv and TourPred.bsv