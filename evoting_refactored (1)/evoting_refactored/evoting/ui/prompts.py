"""
User input helpers: prompt, masked password input, pause, clear screen.
"""

import os
import sys

from ui.colors import RESET, DIM, BRIGHT_WHITE, YELLOW


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n  {DIM}Press Enter to continue...{RESET}")


def prompt(text):
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text="Password: "):
    """Read a password from stdin, masking each character with '*'."""
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""

    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print()
                break
            elif ch in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{YELLOW}*{RESET}")
                sys.stdout.flush()
    else:
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print()
                    break
                elif ch in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{YELLOW}*{RESET}")
                    sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return password
