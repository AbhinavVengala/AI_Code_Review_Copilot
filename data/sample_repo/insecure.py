def unsafe_eval(user_input):
    eval(user_input)  # security risk

def delete_file(file_path):
    import os
    os.remove(file_path)  # potentially dangerous
