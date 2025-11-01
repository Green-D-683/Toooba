#!/usr/bin/env python3

#================================================================================================================#
# Imports
#================================================================================================================#

# Send emails asynchronously
from asyncio import run

# Actually sending emails
from email.message import EmailMessage
from ssl import create_default_context, SSLContext
from smtplib import SMTP

# Loading `email.json`
from json import loads

from typing import Union
from args import parsed_args, parser

# Misc - might be useful for emails
def hostname():
    from socket import gethostname;
    return gethostname();

#================================================================================================================#
# Extract information from `email.json``
#================================================================================================================#

_EMAIL_JSON:dict[str:Union[str,int,None]]
try:
    with open(parsed_args.email_json, "r") as f:
        _EMAIL_JSON = loads("".join(f.readlines()))
except FileNotFoundError as e:
    import re;
    print(f"""\
Cannot find `{parsed_args.email_json}` - have you set it up when you cloned the repo?

To set up, run `cp {re.sub("email.json$", "email_template.json", parser.get_default("email_json"))} {parsed_args.email_json}`, and fill in the missing information""");
    exit(1);

# Password is optional in email.json. If not defined, ask the user for it when the module is imported
if _EMAIL_JSON["password"] == None:
    from getpass import getpass;
    _EMAIL_JSON["password"] = getpass("Email Password: ");

#================================================================================================================#
# Actually sending emails...
#================================================================================================================#

async def _send_email(subject:str, content:str):
    """
    Asynchronous email sending function - sets up a secure connection and sends a message

    Args:
        subject (str): Subject of the Message
        content (str): Content of the Message
    """    
    message:EmailMessage = EmailMessage();
    message["From"] = _EMAIL_JSON["username"];
    message["To"] = _EMAIL_JSON["send_to"];
    message["Subject"] = subject;
    message.set_content(content);

    context:SSLContext = create_default_context()
    with SMTP(_EMAIL_JSON["server"], _EMAIL_JSON["port"]) as server:
        server.starttls(context=context);
        server.login(_EMAIL_JSON["username"], _EMAIL_JSON["password"]);
        server.sendmail(_EMAIL_JSON["username"], _EMAIL_JSON["send_to"], message.as_string());

def send_email(subject:str, content:str):
    """
    Hopefully self explanatory - wraps _send_email

    Args:
        subject (str): Subject of the Message
        content (str): Content of the Message
    """    
    run(_send_email(subject, content));

#================================================================================================================#
# Testing
#================================================================================================================#

def _send_email_test():
    """
    Sends a test email
    """
    (lambda hostname: send_email(f"{hostname} Test JSON", f"Hello from {hostname}")) (hostname());

if __name__ == "__main__":
    _send_email_test()