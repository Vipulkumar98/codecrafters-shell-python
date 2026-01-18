import sys


BUILTINS = {
    "type": lambda x: print(f"{x} is a shell builtin" if x in BUILTINS else f"{x}: not found"),
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
