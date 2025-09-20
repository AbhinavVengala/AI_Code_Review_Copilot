import os

def empty_function():
    pass

def unsafe_eval(user_input):
    eval(user_input)  # Security risk

def add(a, b):
    return a+b

print(add(2, 3))
