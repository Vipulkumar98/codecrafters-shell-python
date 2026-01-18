import sys
import os

def type_command(cmd):
    if cmd in BUILTINS:
        print(f"{cmd} is a shell builtin")
        return
    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(os.pathsep):
        full_path = os.path.join(directory, cmd)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            print(f"{cmd} is {full_path}")
            return
    print(f"{cmd}: not found")

BUILTINS = {
    "type": type_command,
    "echo": lambda *args: print(" ".join(args)),
    "exit": lambda code=0, *_: sys.exit(int(code)),
}

def main():
    # Uncomment this block to pass the first stage

    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()

        # Wait for user input
        command = input().split()
        cmd = command[0]
        args = command[1:]

        if cmd in BUILTINS:
            BUILTINS[cmd](*args)
        else:
            print(f"{cmd}: command not found")



if __name__ == "__main__":
    main()
