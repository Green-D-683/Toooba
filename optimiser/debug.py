from args import parsed_args
from send_email import send_email, hostname
from traceback import format_exc

def dprintf(pattern:str, *args, **kwargs):
    """
    Debug Print Statement - use {<kw>} for wildcard values expanded after by *args and **kwargs

    Args:
        pattern (str): Pattern of string to print
    """
    if parsed_args.debug:
        print(pattern.format(*args, **kwargs), flush=True);

def emailWarn(id:str, fn:function, *args, **kwargs):
    try:
        # Main program goes here - thus an uncaught exception will trigger an email warning
        fn(*args, **kwargs);
        # Testing warning system
        # raise FutureWarning()
    except BaseException as e:
        send_email(f"FAILURE - `{id}` on {hostname()}", f"""\
Optimiser Process failed on {send_email.hostname()}:

{str(e)}

Trace:
{format_exc()}
""");
        raise e;