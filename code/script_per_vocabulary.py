import pandas as pd
import os
from termcolor import cprint
from sorting_algorithm import process_sorting_indexes
import sys

csv_filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data/" + "vocabolario.csv"

#TODO: correggere bug che non chiede tempo passato

vocabulary_descriptions = ["verbi", "aggettivi", "nomi", "espressioni", "grammatica", "avverbi", "congiunzioni"]
vocabulary_ids = ["V", "A", "N", "ESPR", "G", "ADV", "CONG"]
chosen_vocabulary = []

directions = ["it->de", "de->it"]
chosen_direction = None
labels_statistics = ["da italiano a tedesco", "da tedesco a italiano"]
labels = ["italiano", "tedesco"]

chosen_modes = {}

modes = {
    "de->it": {
        "V": ["traduzione", "prateritum", "perfekt", "casi retti"],
        "N": ["traduzione", "plurale"],
    },
    "it->de": {
        "V": ["traduzione","prateritum", "perfekt", "casi retti"],
        "N": ["traduzione","plurale"]
    }
}

words_sorted = []

errors = []

def main():
    os.system("clear")
    df = read_data()

    get_chosen_vocabulary()
    get_chosen_direction()
    get_chosen_modes()

    get_sorted_words(df)

    try: 
        start_exercise(df)
    except Exception as e:
        cprint("ERRORE: ", "red", end="")
        cprint(e, "yellow")

    print_errors()
    write_data(df)

def read_data():
    df = pd.read_csv(csv_filepath, sep=",")
    columns_to_check = ["tentativi da italiano a tedesco", "errori da italiano a tedesco", 
        "tentativi da tedesco a italiano", "errori da tedesco a italiano"]

    for index, row in df.iterrows():
        for column in columns_to_check:
            if(str(df.at[index, column]) == "nan"):
                df.at[index, column] = "0"  

    int_columns = columns_to_check + ["priorita"]
    for index, row in df.iterrows():
        for column in int_columns:
            df.at[index, column] = int(df.at[index, column])

    return df

def get_chosen_vocabulary():
    global chosen_vocabulary
    while True:
        print("Quale tipo di esercizio vuoi fare?")
        for i in range(len(vocabulary_ids)):
            cprint(vocabulary_ids[i] + ": " + vocabulary_descriptions[i], "white")
        cprint("Quali vuoi? ", "blue", end="")
        user_input = input().strip().upper()

        if(user_input == "ALL"):
            chosen_vocabulary = vocabulary_ids
            return

        user_input = [id.strip() for id in user_input.split(",")]
        for id in user_input:
            if(id in vocabulary_ids):
                chosen_vocabulary.append(id)
            else:
                cprint("Id non valido, reinserisci tutto", "yellow")
                continue
        break
    print("Hai scelto: ", end="")
    cprint(", ".join(chosen_vocabulary), "green")

def get_chosen_direction():
    global chosen_direction
    while True:
        print("In quale direzione vuoi fare l'esercizio?")
        for i in range(len(directions)):
            cprint(directions[i], "white")
        cprint("Quale vuoi? (default it->de)", "blue", end="")
        user_input = input().strip().lower()

        if(user_input in directions):
            chosen_direction = user_input
            break
        elif(user_input == ""):
            chosen_direction = directions[0]
            break
        else:
            cprint("Direzione non valida", "yellow")
            continue
    print("Hai scelto: ", end="")
    cprint(chosen_direction, "green")

def get_chosen_modes():

    for vocabulary in chosen_vocabulary:
        get_chosen_modes_for_vocabulary(vocabulary)

def get_chosen_modes_for_vocabulary(vocabulary):
    global chosen_modes
    global chosen_direction
    chosen_modes[vocabulary] = []

    if vocabulary not in modes[chosen_direction]:
        return

    available_modes = modes[chosen_direction][vocabulary]

    while True:
        print("Quale cose vuoi ti vengano chieste per " + vocabulary + "?")
        for i in range(len(available_modes)):
            cprint(available_modes[i], "white")
        cprint("Quali vuoi? (default traduzione)", "blue", end="")
        user_input = input().strip().lower()

        if(user_input == "all"):
            chosen_modes[vocabulary] = available_modes
            return
        if(user_input == ""):
            chosen_modes[vocabulary] = ["traduzione"]
            return

        user_input = [mode.strip() for mode in user_input.split(",")]
        retry = False
        for mode in user_input:
            if(mode in available_modes):
                chosen_modes[vocabulary].append(mode)
            else:
                cprint("Nome non valido, reinserisci tutto", "yellow")
                retry = True

        if retry:
            continue  
        break
    print("Hai scelto: ", end="")
    cprint(", ".join(chosen_modes[vocabulary]), "green")

def get_sorted_words(df):
    global words_sorted
    words = []
    priorities = []
    tries = []
    errors = []

    dir_in = directions.index(chosen_direction)

    for index, row in df.iterrows():
        if(row["tipo"] in chosen_vocabulary):
            word = row[labels[dir_in]] + "-" + row["tipo"]
            if word not in words:
                words.append(word)
                priorities.append(row["priorita"])
                tries.append(row["tentativi " + labels_statistics[dir_in]])
                errors.append(row["errori " + labels_statistics[dir_in]])
            else:
                priorities[words.index(word)] = max(priorities[words.index(word)], row["priorita"])
                tries[words.index(word)] = max(tries[words.index(word)], row["tentativi " + labels_statistics[dir_in]])
                errors[words.index(word)] = max(errors[words.index(word)], row["errori " + labels_statistics[dir_in]])

    sorting_indexes = process_sorting_indexes(priorities, tries, errors)
    words_sorted = [words[i] for i in sorting_indexes]

def start_exercise(df):
    global errors
    global words_sorted

    old_errors_n = 0
    ask_words_to_user(df, words_sorted)

    while len(errors) > old_errors_n:
        old_errors_n = len(errors)
        ask_words_to_user(df, errors[old_errors_n:])

    

def ask_words_to_user(df, words):
    global errors
    for word in words:
        type = word.split("-")[1]
        word = word.split("-")[0]
        if len(chosen_modes[type]) == 0:
            modes_to_ask = ["traduzione"]
        else:
            modes_to_ask = chosen_modes[type]
        
        print()
        cprint(word + get_clarification_if_present(word, type, df), "magenta")

        result = True
        for mode in modes_to_ask:
            if is_word_missing(df, word, type, mode):
                continue
            print("Inserisci ", end="")
            cprint(mode.upper(), "blue", end="")
            print(": ", end="")

            user_input = ""
            while True:
                try:
                    user_input = input().strip()
                    break
                except UnicodeDecodeError:
                    print("Upss, e' successo qualcosa di strano. Puoi reinserire?: ", end="")
                    continue

            if(user_input == "q"):
                return "exit"
            
            mode_result = check_answer(df, word, type, user_input, mode)
            result = result and mode_result

        increment_tries(df, word, type)

        if(not result):
            errors.append(word + "-" + type)
            add_error(df, word, type)


def get_clarification_if_present(word, type, df):
    dir_in = directions.index(chosen_direction)
    for index, row in df.iterrows():
        if(row["tipo"] == type and row[labels[dir_in]] == word and str(row["precisazione " + labels[dir_in]]) != "nan"):
            return " (" + row["precisazione " + labels[dir_in]] + ")"
    return ""

def is_word_missing(df, word, type, mode):
    if(mode == "traduzione"):
        return False
    dir_in = directions.index(chosen_direction)
    for index, row in df.iterrows():
        if(row["tipo"] == type and row[labels[dir_in]] == word and row[mode] == "/"):
            return True
        

def check_answer(df, word, type, user_input, mode):
    dir_in = directions.index(chosen_direction)
    correct_answer = []
    for index, row in df.iterrows():
        if(row["tipo"] == type and row[labels[dir_in]] == word):
            if mode == "traduzione":
                correct_answer.append(row[labels[1-dir_in]])
            else:
                correct_answer.append(row[mode])

    user_input = user_input.split(",")

    missing = set(correct_answer) - set(user_input)
    wrong = set(user_input) - set(correct_answer)
    if (len(missing) == 0 and len(wrong) == 0):
        cprint("Corretto!", "green")
        return True
    else:
        cprint("Sbagliato!", "red")
        if(len(missing) > 0):
            print("Mancano: ", end="")
            cprint(", ".join(missing), "red")

        if(len(wrong) > 0):
            print("Sbagliati: ", end="")
            cprint(", ".join(wrong), "red")
        print()
        return False
    
            
def increment_tries(df, word, type):
    dir_in = directions.index(chosen_direction)

    for index, row in df.iterrows():
        if(row["tipo"] == type and row[labels[dir_in]] == word):
            df.at[index, "tentativi " + labels_statistics[dir_in]] += 1    

def add_error(df, word, type):
    dir_in = directions.index(chosen_direction)

    for index, row in df.iterrows():
        if(row["tipo"] == type and row[labels[dir_in]] == word):
            df.at[index, "errori " + labels_statistics[dir_in]] += 1

def print_errors():
    global errors
    print()
    if(len(errors) == 0):
        cprint("TUTTO GIUSTO!", "green")
        return
    else:
        cprint("ERRORI:\n", "red")

    for i in range(len(vocabulary_ids)):
        if(vocabulary_ids[i] not in chosen_vocabulary):
            continue
        cprint(vocabulary_descriptions[i].upper(), "magenta")
        
        sub_errors = [error.split("-")[0] for error in errors if error.split("-")[1] == vocabulary_ids[i]]
        if(len(sub_errors) == 0):
            cprint("Tutto giusto!\n", "green")
        else:
            cprint(", ".join(sub_errors) + "\n", "yellow")


def write_data(df):
    df.to_csv(csv_filepath, index=False)
    return 

main()