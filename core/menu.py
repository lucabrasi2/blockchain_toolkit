"""
Application Menus
"""


def main_menu():
    print()
    print("Choose Blockchain")
    print()
    print("1. Ethereum")
    print("2. Bitcoin")
    print("3. TRON")
    print("4. Exit")
    print()

    return input("Selection: ").strip()