from args import parsed_args

def dprintf(pattern:str, *args, **kwargs):
    """
    Debug Print Statement - use {<kw>} for wildcard values expanded after by *args and **kwargs

    Args:
        pattern (str): Pattern of string to print
    """
    if parsed_args.debug:
        print(pattern.format(*args, **kwargs))