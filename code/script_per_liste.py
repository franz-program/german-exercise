import pandas as pd
import os
from termcolor import cprint
from random import uniform
from sorting_algorithm import process_sorting_indexes

csv_filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/" + "generici.csv"
wrong_ids = set()

descriptions_index = None
ids_index = None
priorities_index = None
properties_index = None
starting_index = None
n_of_tries_index = None
n_of_errors_index = None

def main():
    os.system("clear")
    df = pd.read_csv(csv_filepath, sep=",")
    set_rows_indexes(df)
    ids = get_ids_sorted(df)
    ask_lists_to_user(df, ids)
    print_wrong_ids(df)
    cprint("Alla prossima!", "magenta")
    df.to_csv(csv_filepath, index=False)

def get_ids_sorted(df):
    ids = df.iloc[ids_index].tolist()[1:]

    priorities = df.iloc[priorities_index].tolist()[1:]

    errors = df.iloc[n_of_errors_index].tolist()[1:]
    tries = df.iloc[n_of_tries_index].tolist()[1:]
    
    indexes = process_sorting_indexes(priorities, tries, errors)
    ids = [ids[i] for i in indexes]

    return ids

def ask_lists_to_user(df, ids):
    global wrong_ids
    for id in ids:
        ret = ask_list_to_user(df[id])
        if (ret == "q"):
            break
        if (ret == "wrong"):
            ids.append(id)
            if(id not in wrong_ids):
                wrong_ids.add(id)



def ask_list_to_user(list):
    print("Scrivimi '", end="")
    cprint(list[descriptions_index], "blue", end="")
    print("': ", end="")

    user_input = input()
    if (user_input == "q" or user_input == "exit"):
        return "q"

    if (list[n_of_tries_index] == ""):
        list[n_of_tries_index] = "0"
    if(list[n_of_errors_index] == ""):
        list[n_of_errors_index] = "0"      
        
    list[n_of_tries_index] = str(1 + int(list[n_of_tries_index]))

    result = compare_user_input([input.strip() for input in user_input.split(",")],
                [word for word in list[starting_index:] if str(word) != "nan"],
                [property.strip() for property in list[properties_index].split(",")])
                    
    if(not result):
        list[n_of_errors_index] = str(1 + int(list[n_of_errors_index]))
        return "wrong"
    else:
        return "correct"


def compare_user_input(user_input, list, properties):
    if ("no order" in properties):
        return compare_without_order(user_input, list, properties)
    else:
        return compare_with_order(user_input, list, properties)

def compare_without_order(user_input, list, properties):
    user_input = set(user_input)
    list = set(list)
    missing = list - user_input
    wrong = user_input - list
    if (len(missing) == 0 and len(wrong) == 0):
        cprint("Corretto!", "green")
        return True
    else:
        cprint("Sbagliato!", "red")
        cprint("Mancano: " + ", ".join(missing), "red")
        cprint("Sbagliati: " + ", ".join(wrong), "red")
        return False

def compare_with_order(user_input, list, properties):
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

def print_wrong_ids(df):
    global wrong_ids
    if(len(wrong_ids) > 0):
        cprint("Hai fatto errori su: ", "red", end="")
        wrong_descriptions = [df[wrong_id][descriptions_index] for wrong_id in wrong_ids]
        cprint(", ".join(wrong_descriptions), "yellow")
    else: 
        cprint("Non hai fatto errori!", "green") 

def set_rows_indexes(df):
    global descriptions_index
    global ids_index
    global priorities_index
    global properties_index
    global starting_index
    global n_of_tries_index
    global n_of_errors_index

    first_column = df["FIRST"].tolist()
    descriptions_index = first_column.index("descrizione")
    ids_index = first_column.index("id")
    priorities_index = first_column.index("priorita")
    properties_index = first_column.index("proprieta")
    starting_index = first_column.index("inizio")
    n_of_tries_index = first_column.index("tentativi")
    n_of_errors_index = first_column.index("errori")

main()