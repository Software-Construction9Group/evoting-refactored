"""
Reusable UI display components: headers, tables, menus, messages.
"""

from ui.colors import (
    RESET, BOLD, DIM, GRAY,
    RED, GREEN, YELLOW,
    THEME_ADMIN,
)


def header(title, theme_color):
    width = 58
    top = f"  {theme_color}{'═' * width}{RESET}"
    mid = f"  {theme_color}{BOLD} {title.center(width - 2)} {RESET}{theme_color} {RESET}"
    bot = f"  {theme_color}{'═' * width}{RESET}"
    print(top)
    print(mid)
    print(bot)


def subheader(title, theme_color):
    print(f"\n  {theme_color}{BOLD}▸ {title}{RESET}")


def table_header(format_str, theme_color):
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")


def table_divider(width, theme_color):
    print(f"  {theme_color}{'─' * width}{RESET}")


def menu_item(number, text, color):
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def error(msg):
    print(f"  {RED}{BOLD} {msg}{RESET}")


def success(msg):
    print(f"  {GREEN}{BOLD} {msg}{RESET}")


def warning(msg):
    print(f"  {YELLOW}{BOLD} {msg}{RESET}")


def info(msg):
    print(f"  {GRAY}{msg}{RESET}")
def status_badge(text, status="info"):
    """
    Displays a small label showing the status of something
    like ACTIVE, CLOSED, VERIFIED, etc.
    """

    if status == "success":
        return f"[✓ {text}]"
    elif status == "error":
        return f"[✗ {text}]"
    elif status == "warning":
        return f"[! {text}]"
    else:
        return f"[{text}]"