#!/usr/bin/env python3

import traceback;

import args;

import db;

import send_email;

if __name__=="__main__":
    try:
        # Main program goes here - thus an uncaught exception will trigger an email warning

        pass; # TODO 

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