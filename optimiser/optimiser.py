#!/usr/bin/env python3

#================================================================================================================#
# Imports
#================================================================================================================#

from debug import emailWarn;

import optimisers
from args import parsed_args

#================================================================================================================#
# Main Function - runs selected optimiser
#================================================================================================================#

# TODO - add arg for selecting optimiser program from above - and make `main()` below run the selected program

def main() -> None:
    """
    Main Optimiser - this runs within a crash warning handler that will email in the case of a failure - declare the main program here rather than outside
    """
    getattr(optimisers, parsed_args.optimiser)();

#================================================================================================================#
# Call Site for `main()` - Crash Handler `emailWarn`
#================================================================================================================#

if __name__=="__main__":
    emailWarn("optimiser.py", main);


# ! USER_CLK_PERIOD is dummy value passed through to FPGA Synthesis
# ! L1_TLB_SIZE is probably negligible in the provided benchmarks - too small to use VirtMem 

# ! Could add parameter for branch predictor state size - see Btb.bsv and TourPred.bsv