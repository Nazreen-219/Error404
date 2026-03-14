def run_command(text):

    text = text.lower()

    if "जाति" in text or "caste" in text:
        print("Opening caste certificate form")
    elif "आय" in text or "income" in text:
        print("Opening income certificate form")
    else:
        print("Command not recognized")
