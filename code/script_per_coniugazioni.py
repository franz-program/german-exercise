import pandas as pd
import os
from termcolor import cprint
from random import uniform

csv_filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/" + "coniugazioni.csv"

types_descriptions = ["presente", "imperfetto"]
types_ids = ["P", "I"]

def main():
    os.system("clear")
    df = read_data()

    desired_type = get_desired_type()

    sort_df(df)
    ask_conjugations_to_user(df, desired_type)

    write_data(df)


def read_data():
    df = pd.read_csv(csv_filepath, sep=",")
    df["index"] = df.index
    for index, row in df.iterrows():
        if(index == 0):
            continue
        if(str(df.at[index, "tentativi"]) == "nan"):
            df.at[index, "tentativi"] = "0"
        if(str(df.at[index, "errori"]) == "nan"):
            df.at[index, "errori"] = "0"

    return df


def get_desired_type():
    #select one type from user input
    desired_type = None

    while True:
        cprint("Quale tipo di coniugazione vuoi fare?", "yellow")
        for i in range(len(types_descriptions)):
            cprint(types_ids[i] + ": " + types_descriptions[i], "white")

        cprint("Quale vuoi? ", end="", color="yellow")
        user_input = input().strip().upper()
        if (user_input in types_ids):
            desired_type = user_input
            break
        else:
            cprint("Id non valido", "yellow")
            continue
    return desired_type

def sort_df(df):
    df["points"] = df.index
    for index, row in df.iterrows():
        if(index == 0):
            continue
        errors = int(df.at[index, "errori"])
        tries = int(df.at[index, "tentativi"])
        priority = int(df.at[index, "priorita"])

        avg_tries = sum([int(t) for t in df["tentativi"]])/len(df["tentativi"])
        points_for_errors = 1/(1-errors/tries) if tries > avg_tries/4 else 100
        points_for_errors = 1 if points_for_errors < 1.25 else points_for_errors
        max_priority = max([int(p) for p in df["priorita"]])
        points_for_priority = uniform(0,2) + priority/max_priority*10

        df.at[index, "points"] = uniform(0.5, 1)*points_for_errors + uniform(0.5, 1)*points_for_priority

    df.sort_values(by="points", inplace=True)
    df.drop(columns=["points"], inplace=True)

def ask_conjugations_to_user(df, desired_type):
    errors_indexes = []
    for index, row in df.iterrows():
        if(index == 0):
            continue
        if(row["tipo"] != desired_type):
            continue

        print("Inserisci la coniugazione di ", end="")
        cprint(row["verbo"], "blue", end="")
        print(": ", end="")
        
        user_input = input().strip()
        if (user_input == "q"):
            return "stop"


        df.at[index, "tentativi"] = str(int(df.at[index, "tentativi"])+1)

        user_input = [input.strip() for input in user_input.split(",")]
        conjugations = [df.at[index, "ich"], df.at[index, "du"], df.at[index, "er, sie, es"], df.at[index, "wir"], df.at[index, "ihr"], df.at[index, "sie"]]
        
        if(not compare_user_input(user_input, conjugations)):
            errors_indexes.append(index)
            df.at[index, "errori"] = str(int(df.at[index, "errori"])+1)
    
    for index in errors_indexes:
        df.at[index, "tentativi"] = str(int(df.at[index, "tentativi"])+1)
        print("Inserisci la coniugazione di ", end="")
        cprint(df.at[index,"verbo"], "blue", end="")
        print(": ", end="")
        
        user_input = input().strip()
        if (user_input == "q"):
            return "stop"

        user_input = [input.strip() for input in user_input.split(",")]
        conjugations = [df.at[index, "ich"], df.at[index, "du"], df.at[index, "er, sie, es"], df.at[index, "wir"], df.at[index, "ihr"], df.at[index, "sie"]]
        if(not compare_user_input(user_input, conjugations)):
            errors_indexes.append(index)
            df.at[index, "errori"] = str(int(df.at[index, "errori"])+1)

def compare_user_input(user_input, list):
    if(len(user_input) == len(list)):
        correct = True
        for i in range(len(user_input)):
            if(user_input[i] != list[i]):
                correct = False
                break
        if(correct):
            cprint("Corretto!", "green")
            return True

    cprint("Sbagliato!", "red")
    print("I tuoi inserimenti: ", end="")
    for i in range(len(user_input)):
        if(i < len(list) and user_input[i] == list[i]):
            cprint(user_input[i], "green", end="")
        else:
            cprint(user_input[i], "red", end="")
        if(i != len(user_input) - 1):
            print(", ", end="")

    print("\nLa lista corretta e': " + ", ".join(list))
    return False      

def write_data(df):
    df.sort_values(by="index", inplace=True)
    df.drop(columns=["index"], inplace=True)
    df.to_csv(csv_filepath, index=False)
    return 

main()