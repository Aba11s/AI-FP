import os
print(f"Current directory: {os.getcwd()}")
print(f"Target directory: {os.path.abspath('../output/test1')}")

# List what exists
if os.path.exists("../output"):
    print("'output' directory exists")
    if os.path.exists("../output/test1"):
        print("'test1' directory exists")
        files = os.listdir("../output/test1")
        print(f"Files in test1: {files}")