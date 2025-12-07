import os

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'admins.txt')

with open(file_path, 'r') as f:
    admins = f.read().splitlines()

print("Admins loaded:", admins)
