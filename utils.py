import os


def clear_screen():
    # Clear command as function of OS
    command = "cls" if os.name == "nt" else "clear"
    # Execute command to clear the screen
    os.system(command)
