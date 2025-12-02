import os
import json
import subprocess

# Intentional Flake8 issues: missing whitespace, unused import
def complex_logic(x,y):
    if x > 10:
        if y < 5:
            for i in range(x):
                if i % 2 == 0:
                    print("Even")
                else:
                    if y == 0:
                        print("Zero")
                    else:
                        print("Odd")
        else:
            print("Y is big")
    else:
        print("X is small")

def process_user_input(data):
    # Intentional Security Issue: eval() (Bandit)
    result = eval(data)
    return result

def connect_db():
    # Intentional Security Issue: Hardcoded password
    password = "admin_password_123"
    print(f"Connecting with {password}")

def main():
    user_input = input("Enter command: ")
    process_user_input(user_input)
    complex_logic(15, 3)

if __name__ == "__main__":
    main()
