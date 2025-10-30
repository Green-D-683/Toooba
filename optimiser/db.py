#!/usr/bin/env python3
import sqlite3;

from os import path, getcwd, PathLike;

from debug import dprintf

#================================================================================================================#
# Database Parameters - 
#================================================================================================================#

from args import parsed_args;

DB_FILE:str = parsed_args.db_file;
TABLE:str = parsed_args.table;

#================================================================================================================#
# Get Toooba Parameters
#================================================================================================================#

# Read `Include_RISCY_Parameters.mk` to get list of Parameters, can be overridden using an argument
PARAM_FILE:PathLike = parsed_args.param_file;

def get_params(param_file:PathLike=PARAM_FILE)->list[str]:
    f = open(param_file, "r");
    ls:list[str] = f.readlines();
    f.close();
    return [(l.split("?=")[0]).strip() for l in ls];

PARAMS:list[str] = get_params();

#================================================================================================================#
# Setup Schema of DB
#================================================================================================================#

SCHEMA_DICT:dict[str,str] = {
    "run": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "iteration": "INTEGER NOT NULL",
    "time": "TEXT NOT NULL",
    "performance": "REAL NOT NULL",
    "area": "REAL NOT NULL"
};

for param in PARAMS:
    SCHEMA_DICT[param] = "INTEGER NOT NULL";

SCHEMA:str = ",".join([f"{attr} {SCHEMA_DICT[attr]}" for attr in SCHEMA_DICT.keys()]);

#================================================================================================================#
# Connecting to the DB
#================================================================================================================#

def _connect_db() -> sqlite3.Connection:
    """
    Obtain a database conncection - creates a new file and object if not found

    Returns:
        sqlite3.Connection: Database Connection Object
    """    
    return sqlite3.connect(DB_FILE);

def setup_db(con:sqlite3.Connection):
    """
    Initialise a new database in the case that the file cannot be found

    Args:
        con (sqlite3.Connection): Database Connection Object - should point to new database
    """    
    cur:sqlite3.Cursor = con.cursor();
    res:sqlite3.Cursor = cur.execute(f"CREATE TABLE {TABLE} ({SCHEMA})");
    res.fetchall();

def connect_db() -> sqlite3.Connection:
    """
    Connect to the Database, returning the connection Object

    Returns:
        sqlite3.Connection: Database Connection Object
    """
    if path.exists(path.join(getcwd(), DB_FILE)):
        dprintf("DB File Exists - {}", "Loading");
        con:sqlite3.Connection = _connect_db();
    else:
        dprintf("DB File not Found - Creating and Initialising");
        con:sqlite3.Connection = _connect_db();
        setup_db(con);
    return con;

#================================================================================================================#
# Store Iteration Results
#================================================================================================================#

# TODO

#================================================================================================================#
# Testing Function - define as needed to debug
#================================================================================================================#

def _db_test():
    """
    Misc Test function - change as needed
    """    
    con:sqlite3.Connection = connect_db();
    con.close();

if __name__ == "__main__":
    _db_test()