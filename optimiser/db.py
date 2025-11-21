#!/usr/bin/env python3

#================================================================================================================#
# Imports
#================================================================================================================#

import sqlite3, typing;

from os import path, getcwd;

from debug import dprintf;

#================================================================================================================#
# Pretty Printing and Types
#================================================================================================================#

type dbItem = typing.Union[str, float, int];
type dbRow = dict[str:dbItem];

def _ppOut(table:list[dbRow]) -> None:
    if len(table) > 0:

        header:list[str] = list(table[0].keys());
        rows:list[list[dbItem]] = [header] + ([list(row.values()) for row in table]);
        colLens:list[int] = [ max(len(str(rows[i][colNum])) for i in range(len(rows))) for colNum in range(len(rows[0])) ]
        
        hline = lambda : print(f"+{"+".join(["-"*(colLen+2) for colLen in colLens])}+")

        hline()
        print(f"| {" | ".join([str(item).center(colLen) for item, colLen in zip(header, colLens)])} |");
        hline()

        #row:list[dbItem];
        for row in rows[1:]:
            #item:dbItem; colLen:int;
            print(f"| {" | ".join([str(item).center(colLen) for item, colLen in zip(row, colLens)])} |");
        hline()

#================================================================================================================#
# Database + Other Toooba Parameters - 
#================================================================================================================#

from args import parsed_args, PARAMS;

DB_FILE:str = parsed_args.db_file;
TABLE:str = parsed_args.table;

#================================================================================================================#
# Setup Schema of DB
#================================================================================================================#

SCHEMA_DICT:dict[str,str] = {**{ # Use ** unpacking to join dicts
    "run": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "iteration": "INTEGER NOT NULL",
    "time": "TEXT NOT NULL",
    "performance": "REAL NOT NULL",
    "area": "REAL NOT NULL"
}, **{param: "INTEGER NOT NULL" for param in PARAMS}};

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
    con:sqlite3.Connection = sqlite3.connect(DB_FILE);
    # Set return object of queries to be a `dict` object
    con.row_factory = (lambda cursor, row: {key: value for key, value in zip([column[0] for column in cursor.description], row)});
    return con;

def setup_db(con:sqlite3.Connection) -> None:
    """
    Initialise a new database in the case that the file cannot be found

    Args:
        con (sqlite3.Connection): Database Connection Object - should point to new database
    """    
    cur:sqlite3.Cursor = con.cursor();
    res:sqlite3.Cursor = cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE} ({SCHEMA})");
    res.fetchall();

def connect_db() -> sqlite3.Connection:
    """
    Connect to the Database, returning the connection Object

    Returns:
        sqlite3.Connection: Database Connection Object
    """
    if path.exists(path.join(getcwd(), DB_FILE)):
        dprintf("DB File Exists - {}", "Loading");
    else:
        dprintf("DB File not Found - Creating and Initialising");
    con:sqlite3.Connection = _connect_db();
    setup_db(con);
    return con;

#================================================================================================================#
# Store + Access Iteration Results
#================================================================================================================#

def add_run(iteration: int, time:str, performance:float, area:float, **params:int):
    con:sqlite3.Connection;
    with connect_db() as con:
        cur:sqlite3.Cursor = con.cursor();
        res:sqlite3.Cursor = cur.execute(f"INSERT INTO {TABLE} (iteration, time, performance, area, {", ".join(PARAMS)}) VALUES ({iteration}, '{time}', {performance}, {area}, {", ".join([str(params[param]) for param in PARAMS])})");
        res.fetchall();

def get_results(iteration:typing.Union[None, int] = None) -> list[dbRow]:
    con:sqlite3.Connection;
    with connect_db() as con:
        cur:sqlite3.Cursor = con.cursor();
        res:sqlite3.Cursor = cur.execute(f"SELECT * FROM {TABLE} {"" if iteration==None else f"WHERE iteration=={iteration}"}");
        ret = res.fetchall();
    return ret;

def get_latest_iteration() -> int:
    con:sqlite3.Connection;
    with connect_db() as con:
        cur:sqlite3.Cursor = con.cursor();
        res:sqlite3.Cursor = cur.execute(f"SELECT max(iteration) as iteration FROM {TABLE}");
        ret = res.fetchall();
    return ret[0]["iteration"];

#================================================================================================================#
# Testing Function - define as needed to debug
#================================================================================================================#

def _db_test():
    """
    Misc Test function - change as needed
    """
    from random import randint, random
    
    _ppOut(get_results())
    
    _ppOut(get_results(4))

if __name__ == "__main__":
    _db_test()