
import colorama
import numpy as np
import os
import pandas as pd
import requests
import sqlite3
import sys

from colorama import Fore
from typing import Tuple
from requests.exceptions import RequestException

app_title = "MX Corn Flour Prices Data Munging v0.1"
cnnstr = "todo.db"
source_url = "https://www.economia-sniim.gob.mx/SNIIM-Archivosfuente/Comentarios/Otros/PreciosHarinaMaiz%2030(07)25.xlsx"
source_filename = "cornflourprices.xlsx"
state_iso = {
    "Aguascalientes": "AGU",
    "Baja California": "BCN",
    "Baja California Sur": "BCS",
    "Campeche": "CAM",
    "Chiapas": "CHP",
    "Chihuahua": "CHH",
    "Ciudad de México": "CMX",
    "Coahuila": "COA",
    "Colima": "COL",
    "Durango": "DUR",
    "Estado de México": "MEX",
    "Guanajuato": "GUA",
    "Guerrero": "GRO",
    "Hidalgo": "HID",
    "Jalisco": "JAL",
    "México": "MEX",  # Estado de México
    "Michoacán": "MIC",
    "Morelos": "MOR",
    "Nayarit": "NAY",
    "Nuevo León": "NLE",
    "Oaxaca": "OAX",
    "Puebla": "PUE",
    "Querétaro": "QUE",
    "Quintana Roo": "ROO",
    "San Luis Potosí": "SLP",
    "Sinaloa": "SIN",
    "Sonora": "SON",
    "Tabasco": "TAB",
    "Tamaulipas": "TAM",
    "Tlaxcala": "TLA",
    "Veracruz": "VER",
    "Yucatán": "YUC",
    "Zacatecas": "ZAC"
}

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

        with pd.ExcelFile(source_filename) as excel:
            print(f"Found {len(excel.sheet_names)} sheets with data.")
            for sheet_name in excel.sheet_names:
                print(f"Processing sheet '{sheet_name}'...")
                sheet = pd.read_excel(excel, sheet_name=sheet_name, skiprows=8, skipfooter=3)


                sheet = sheet.drop(sheet.columns[1], axis=1)
                sheet = sheet.rename(columns={"Entidad federativa":"State"})
                sheet["State"] = sheet["State"].str.strip()
                sheet["State"] = sheet["State"].map(state_iso)
                sheet = sheet.replace("-", pd.NA)

                maseca_cols = ["State"] + [col for col in sheet.columns if "Unnamed" not in str(col)][1:(len(sheet.columns) // 2) + 1]
                minsa_cols = ["State"] + [col for col in sheet.columns if "Unnamed" not in str(col)][(len(sheet.columns) // 2) + 1:]

                maseca_data = sheet[maseca_cols].melt(id_vars=["State"],
                                                 var_name="Date",
                                                 value_name="MasecaPrice")
                maseca_data["Date"] = maseca_data["Date"].str.replace(r"\.1$", "", regex=True)
                minsa_data = sheet[minsa_cols].melt(id_vars=["State"],
                                               var_name="Date",
                                               value_name="MinsaPrice")
                minsa_data["Date"] = minsa_data["Date"].str.replace(r"\.1$", "", regex=True)

                sheet = pd.merge(maseca_data, minsa_data, on=["State", "Date"], how="outer")
                sheet["Date"] = pd.to_datetime(sheet["Date"], format="mixed", dayfirst=True)
                sheet.insert(2, "Year", sheet["Date"].dt.year)
                sheet.insert(3, "Month", sheet["Date"].dt.month)

                sheet = sheet.drop(sheet.columns[1], axis=1)

                sheet["Year"] = sheet["Year"].astype("int16")
                sheet["Month"] = sheet["Month"].astype("int8")
                sheet["MasecaPrice"] = sheet["MasecaPrice"].astype("Float32")
                sheet["MinsaPrice"] = sheet["MinsaPrice"].astype("Float32")

                with (sqlite3.connect("cornflourprices.db") as cnn):
                    sheet.to_sql("prices", cnn, index=False, if_exists="replace")

                #print(sheet)
                break

    except RequestException as ex:
        print(f"** {Fore.RED}Error while downloading the data source.{Fore.RESET} **")
    except PermissionError as ex:
        print(f"** {Fore.RED}Couldn't download the data source because write permission was denied.{Fore.RESET} **")


def run():
    print(f"===== {app_title} =====")

    colorama.init()
    clrscr()
    commands = get_commands()
    cmd_get()
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