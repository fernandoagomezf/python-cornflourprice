
import colorama
import os
import pandas as pd
import requests
import sys

from colorama import Fore
from typing import Tuple

app_title = "MX Corn Flour Prices Data Munging v0.1"
cnnstr = "todo.db"
source_url = "https://www.economia-sniim.gob.mx/SNIIM-Archivosfuente/Comentarios/Otros/PreciosHarinaMaiz%2030(07)25.xlsx"
source_filename = "cornflourprices.xlsx"

def get_commands():
    return {
        "exit": (cmd_exit, "Terminates the application."),
        "help": (cmd_help, "Shows available application commands."),
        "get": (cmd_get, "Gets the get")
    }

def clrscr():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def cmd_exit():
    clrscr()
    sys.exit(0)

def cmd_help():
    clrscr()
    print("Available commands:")
    for name, (cmd, txt) in get_commands().items():
        print(f"* {name} - {txt}")

def cmd_get():
    try:
        print(f"Downloading data source...")
        print(f"** {source_url}")
        response = requests.get(source_url)
        response.raise_for_status()
        with open(source_filename, "wb") as file:
            file.write(response.content)
        print(f"{Fore.GREEN}Data saved to file {source_filename}.{Fore.RESET}")

    except requests.exceptions.RequestException as ex:
        print(f"** {Fore.RED}Error while downloading the data source.{Fore.RESET} **")

def run():
    print(f"===== {app_title} =====")

    colorama.init()
    clrscr()
    commands = get_commands()
    while True:
        print("\nInput a command or type help")
        cmd_input = input(":> ")
        if cmd_input in commands:
            cmd, _ = commands[cmd_input]
            cmd()
        else:
            print("Command not recongized.")

if __name__ == "__main__":
    run()