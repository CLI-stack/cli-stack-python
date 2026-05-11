"""
Script: Interactive CLI Menu
What it does: Creates a menu-driven command-line application.
The user navigates options in a loop until they choose to exit.
This pattern is used in many command-line tools and scripts.
"""

import os
import json

# Simple in-memory todo list
todos = []

def clear_screen():
    """Clear the terminal screen (works on both Windows and Linux)."""
    os.system("cls" if os.name == "nt" else "clear")

def show_banner():
    print("=" * 40)
    print("       TODO LIST MANAGER")
    print("=" * 40)
    print()

def show_menu():
    print("\n--- MENU ---")
    print("  1. View all todos")
    print("  2. Add new todo")
    print("  3. Mark as done")
    print("  4. Delete todo")
    print("  5. Clear all")
    print("  0. Exit")
    print()

def view_todos():
    if not todos:
        print("No todos yet! Add one first.")
        return
    print(f"\nYour todos ({len(todos)} total):")
    for i, todo in enumerate(todos):
        status = "[✓]" if todo["done"] else "[ ]"
        print(f"  {i+1}. {status} {todo['text']}")

def add_todo():
    text = input("Enter todo text: ").strip()
    if text:
        todos.append({"text": text, "done": False})
        print(f"Added: '{text}'")
    else:
        print("Cannot add empty todo.")

def mark_done():
    view_todos()
    if todos:
        try:
            idx = int(input("Enter todo number to mark done: ")) - 1
            if 0 <= idx < len(todos):
                todos[idx]["done"] = True
                print(f"Marked as done: '{todos[idx]['text']}'")
            else:
                print("Invalid number.")
        except ValueError:
            print("Please enter a valid number.")

def delete_todo():
    view_todos()
    if todos:
        try:
            idx = int(input("Enter todo number to delete: ")) - 1
            if 0 <= idx < len(todos):
                removed = todos.pop(idx)
                print(f"Deleted: '{removed['text']}'")
            else:
                print("Invalid number.")
        except ValueError:
            print("Please enter a valid number.")

# --- Main loop ---
while True:
    show_banner()
    show_menu()

    choice = input("Enter choice: ").strip()

    if choice == "1":
        view_todos()
    elif choice == "2":
        add_todo()
    elif choice == "3":
        mark_done()
    elif choice == "4":
        delete_todo()
    elif choice == "5":
        todos.clear()
        print("All todos cleared.")
    elif choice == "0":
        print("\nGoodbye!")
        break
    else:
        print("Invalid choice. Please try again.")

    input("\nPress Enter to continue...")
