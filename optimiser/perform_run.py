#!/usr/bin/env python3

#================================================================================================================#
# Imports
#================================================================================================================#

from os import chdir, cpu_count, getenv, makedirs as mkdir, getcwd, PathLike, environ, nice;
from os.path import exists, join;

# Used for calling other programs from within Python
from subprocess import run, PIPE, STDOUT, CompletedProcess;

# Multithreading
from multiprocessing import Process, Manager, Queue;
from multiprocessing.managers import SyncManager;

# High-level file operations
from shutil import copy, rmtree;

# Needed for parsing benchmark/quartus outputs
from csv import DictReader;
from re import compile;

# Typing returned object
from typing import TypedDict;
class RunRetObj(TypedDict):
    index: str;
    params: dict[str,int];
    performance: float;
    area: float;

# debug printing
from debug import dprintf, emailWarn, printf_err;

# Area Tooling Option
from args import parsed_args, _area_tools as args_listed_area_tools

#================================================================================================================#
# Global Definitions - known at start-time
#================================================================================================================#

master_dir = getcwd();
_mkJobs = 18; # TODO Should parameterise into argument
_makeCommand = lambda cmd: ["/usr/bin/env", "make", cmd, f"-j{_mkJobs}"];
_exec = lambda cmdArr, env={}: run(cmdArr, capture_output=True, text=True, env={**dict(environ), **env});

#================================================================================================================#
# The main export - creates a view of the subprocess performing the run - allows for multithreading of subprocesses
#================================================================================================================#

def create_run(index: int, itrun:tuple[int, int], params:dict[str, int], man:SyncManager, calc:bool=True) -> tuple[Process, Queue]:  
    """
    Create a Subprocess, set to perform the specified run

    Args:
        index (int): The process index - used to determine working directory
        itrun (tuple[int, int]): Iteration/Run Indices - Used for debugging and return value identification
        params (dict[str, int]): Parameterisation to be explored during the run
        man (SyncManager): Multiprocessing Manager able to synchronise return Queues
        calc (bool, optional): Calculate Results? Defaults to True.

    Returns:
        tuple[Process, Queue]: The Process object (not yet started), and the return Queue for the run
    """
    # Check the existence of the initial value files needed for calc - exit if not found
    if calc and not (exists(join(getcwd(), "benchmark_res_initial.csv")) and exists(join(getcwd(), "quartus_initial_size")) and exists(join(getcwd(), "quartus_map_initial_summary"))):
        printf_err("Cannot find one or more initial area/performance files - did you run `make optimiser_init`")
        exit(1)
    
    q:Queue = man.Queue();
    return (Process(target=_do_run_wrapped, kwargs = {"index":index, "itrun":itrun, "params":params, "ret":q, "calc":calc}), q);

#================================================================================================================#
# Subroutines Used in Implementing the Run
#================================================================================================================#

def _mkdirIfNotExists(dir:PathLike) -> None:
    """
    Make a Directory at a given location if it doesn't exist, including parents, equivalent to `mkdir -p $dir`

    Args:
        dir (PathLike): absolute path to the directory
    """    
    if not exists(dir):
        mkdir(dir);

def _setup_build_dir(dir:PathLike) -> None:
    """
    Setup the build directory - including a Makefile and Quartus files

    Args:
        dir (PathLike): absolute path to the working directory
    """    
    _mkdirIfNotExists(dir);
    chdir(dir);

    # Copy Makefile from template dir
    if not exists(f"{dir}/Makefile"):
        copy(f"{master_dir.replace("verilator", "optimiser_template")}/Makefile", f"{dir}/Makefile");

    # Setup Quartus files for parallel runs - can't parallel build in repo quartus dir
    res = _exec(_makeCommand("setup_quartus"));
    dprintf(str(len(res.stderr)));

def _setup_log_dir(dir:PathLike) -> None:
    """
    Setup the logging directory

    Args:
        dir (PathLike): absolute path to the logging directory
    """    
    _mkdirIfNotExists(dir);

def _write_log(logdir:PathLike, filename:str, text:str):
    with open(join(logdir, filename), ("r" if exists(join(logdir, filename)) else "x")) as f:
        f.writelines(text);

def _make_call_log(logdir:PathLike, cmd:str, env:dict[str,str]={}):
    res:CompletedProcess = _exec(_makeCommand(cmd), env);
    _write_log(logdir, f"make_{cmd}.out", res.stdout);
    _write_log(logdir, f"make_{cmd}.err", res.stderr);
    dprintf(res.stderr);

    # TODO Handle failed commands safely?

def _calculate_perf(perfPath:PathLike) -> float:
    """
    Calculate the relative performance to base Toooba of the Parameterisation

    Args:
        perfPath (PathLike): Absolute Path to the output file of the benchmarks summary

    Returns:
        float: Ratio of the Parameterisation's Performance to base Toooba
    """

    perfs:list[float] = [];

    with open(perfPath, "r") as perf_file:
        csvPerf:list[dict] = list(DictReader(perf_file, skipinitialspace=True));

        with open("benchmark_res_initial.csv", "r") as initial_perf_file:
            initialPerf:list[dict] = list(DictReader(initial_perf_file, skipinitialspace=True));
    
            for row in csvPerf:
                bench:str = row["Log"];
                initRow:dict = list(filter((lambda r: r["Log"] == bench), initialPerf))[0];
                perfs.append(int(initRow["Cycles"]) / int(row["Cycles"]));
    return sum(perfs) / len(perfs);

def _calculate_area_q1(areaPath:PathLike) -> float:
    """
    Calculate the relative area to base Toooba of the Parameterisation, using parsed `stdout` of Quartus

    Args:
        areaPath (PathLike): Absolute Path to the area output file

    Returns:
        float: Ratio of the Parameterisation's Area to Base Toooba
    """    
    with open(areaPath, "r") as area_file:
        areaLines = area_file.readlines();

    with open("quartus_initial_size", "r") as initial_area_file:
        initialAreaLines = initial_area_file.readlines();

    # ? The Regex code below was sketched with Gemini to get something working quickly - I may rewrite if I get time
    logic_cell_pattern = compile(r"Implemented (\d+) logic cells");
    ram_segment_pattern = compile(r"Implemented (\d+) RAM segments");

    for line in areaLines:
        logic_match = logic_cell_pattern.search(line);
        if logic_match:
            logic_cells = int(logic_match.group(1));
        ram_match = ram_segment_pattern.search(line);
        if ram_match:
            ram_segments = int(ram_match.group(1));

    for line in initialAreaLines:
        logic_match = logic_cell_pattern.search(line);
        if logic_match:
            initial_logic_cells = int(logic_match.group(1));
        ram_match = ram_segment_pattern.search(line);
        if ram_match:
            initial_ram_segments = int(ram_match.group(1));

    return 0.5 * (logic_cells / initial_logic_cells) + 0.5 * (ram_segments / initial_ram_segments);

def _calculate_area_q2(areaPath:PathLike) -> float:
    """
    Calculate the relative area to base Toooba of the Parameterisation, using parsed `mkCoreW.map.summary` of Quartus

    Args:
        areaPath (PathLike): Absolute Path to the area output file

    Returns:
        float: Ratio of the Parameterisation's Area to Base Toooba
    """    
    with open(areaPath, "r") as area_file:
        areaLines = area_file.readlines();

    with open("quartus_map_initial_summary", "r") as initial_area_file:
        initialAreaLines = initial_area_file.readlines();

    comb_function_pattern = compile(r"Total combinational functions : (\d{1,3}(?:,\d{3})*)$");
    mem_bit_pattern = compile(r"Total memory bits : (\d{1,3}(?:,\d{3})*)$");

    for line in areaLines:
        logic_match = comb_function_pattern.search(line);
        if logic_match:
            logic_cells = int((logic_match.group(1)).replace(",", "")); # Remove Commas from regex output
        ram_match = mem_bit_pattern.search(line);
        if ram_match:
            ram_segments = int(ram_match.group(1).replace(",", ""));

    for line in initialAreaLines:
        logic_match = comb_function_pattern.search(line);
        if logic_match:
            initial_logic_cells = int(logic_match.group(1).replace(",", ""));
        ram_match = mem_bit_pattern.search(line);
        if ram_match:
            initial_ram_segments = int(ram_match.group(1).replace(",", ""));

    return 0.5 * (logic_cells / initial_logic_cells) + 0.5 * (ram_segments / initial_ram_segments);

_area_tools = {
    "quartus_size": _calculate_area_q1,
    "quartus_map_summary": _calculate_area_q2
};

def _calculate_area(adir:PathLike) -> float:
    """
    Calculate the relative area to base Toooba of the Parameterisation, using the tool specified by the `--area_tool` command-line argument

    Args:
        adir (PathLike): Artifact Directory of the run

    Returns:
        float: Ratio of the Parameterisation's Area to Base Toooba
    """    
    tool = parsed_args.area_tool;
    func = _area_tools[tool];
    return func(f"{adir}/{tool}");

# ! Check all Area Tools are listed as options in `args.py`
for t in _area_tools.keys():
    if t not in args_listed_area_tools.keys():
        printf_err(f"Area Tool `{t}(...)` has not been added to `args.py` `_area_tools` - this area tool will remain unavailable until this is done");

for t in args_listed_area_tools.keys():
    if t not in _area_tools.keys():
        printf_err(f"Area Tool `{t}(...)` mentioned in `args.py` `_area_tools` is not defined as an area tool in `perform_run.py`. This will crash if used");
        if t == parsed_args.area_tool:
            exit(1);

#================================================================================================================#
# Performing the run
#================================================================================================================#

def _do_run(index:int, itrun:tuple[int, int], params:dict[str,int], ret:Queue, calc:bool = True) -> None:
    """
    Perform a run, usually executed from inside a subprocess, and return the relative area and performance down a FIFO

    Args:
        index (int): The process index - used to determine working directory
        itrun (tuple[int, int]): Iteration/Run Indices - Used for debugging and return value identification
        params (dict[str, int]): Parameterisation to be explored during the run
        man (SyncManager): Multiprocessing Manager able to synchronise return Queues
        calc (bool, optional): Calculate Results? Defaults to True.
    """

    nice(5); # Prevent System Throttling when many parallel runs

    # Setting up Directories
    proc_dir = master_dir.replace("verilator", (f"optimiser_{index}"));
    _setup_build_dir(proc_dir);
    log_dir = join(master_dir, "optimiser_artifacts", parsed_args.table, f"iteration_{itrun[0]}", f"run_{itrun[1]}");
    _setup_log_dir(log_dir);
    
    # Define Parameters for Make - these are passed into bsv as compliation flags
    with (open(join(getcwd(), "Include_Generated_Params.mk"), "w") if exists(join(getcwd(), "Include_Generated_Params.mk")) else open(join(getcwd(), "Include_Generated_Params.mk"), "x")) as param_file:
        # Set Manual Parameterisation - otherwise will build standard Toooba
        param_file.write("CORE_SIZE = MANUAL\nCACHE_SIZE = MANUAL\n");
        # Write Parameters
        for param in params.keys():
            param_file.write(f"{param} = {params[param]}\n");

    # `make compile
    _make_call_log(log_dir, "compile");

    # TODO - Quartus can run in parallel as soon as compile is done, alongside simulator and benchmarks - how to async execute subprocess?

    # `make simulator`
    _make_call_log(log_dir, "simulator");

    # 'make benchmarks`
    _make_call_log(log_dir, "benchmarks", {"TIMESTAMP": f"{itrun[0]}_{itrun[1]}"});
    # Copy Benchmarks results summary
    copy(f"{proc_dir}/benchmark_results_{itrun[0]}_{itrun[1]}.csv", f"{log_dir}/benchmark_results.csv");

    # `make quartus`
    _make_call_log(log_dir, "quartus")
    # Copy Quartus Area Report(s)
    copy(f"{proc_dir}/quartus_artifacts/quartus_size", f"{log_dir}/quartus_size");
    copy(f"{proc_dir}/output_files/mkCoreW.map.summary", f"{log_dir}/quartus_map_summary");

    # Cleanup Build Dir
    chdir(master_dir);
    rmtree(proc_dir);

    if calc:
        # Calculate Performance and Area from Artifacts
        performance:float = _calculate_perf(f"{log_dir}/benchmark_results.csv");
        area:float = _calculate_area(f"{log_dir}");

        # Build and Enqueue Return Object
        ret.put(RunRetObj(index = index, params = params, performance = performance, area = area));
    else:
        ret.put("DONE")

def _do_run_wrapped(index:int, itrun:tuple[int, int], params:dict[str,int], ret:Queue, calc:bool = True) -> None:
    """
    Wrap _do_run in an error handler that will email in case of an Exception being raised

    Args:
        index (int): The process index - used to determine working directory
        itrun (tuple[int, int]): Iteration/Run Indices - Used for debugging and return value identification
        params (dict[str, int]): Parameterisation to be explored during the run
        man (SyncManager): Multiprocessing Manager able to synchronise return Queues
        calc (bool, optional): Calculate Results? Defaults to True.
    """    
    emailWarn(f"optimisation process {index} - {itrun}", _do_run, index, itrun, params, ret);

#================================================================================================================#
# Testing
#================================================================================================================#

def _test_perform_run():
    """
    Performs a test run, printing the results
    """    
    man:SyncManager = Manager();
    proc, q = create_run(0, {}, man);
    proc.run();
    print(q.get());

# If this file is run directly, run the test function
if __name__ == "__main__":
    _test_perform_run();