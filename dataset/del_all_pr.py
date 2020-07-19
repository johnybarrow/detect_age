import os

for file in os.listdir():
    if '_process.jpg' in file:
        print(file)
        os.remove(file)
