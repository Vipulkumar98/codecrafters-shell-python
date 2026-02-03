import sys
import os

def type_command(cmd):
    if cmd in BUILTINS:
        print(f"{cmd} is a shell builtin")
        return
    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(os.pathsep):
        if not directory:
            continue
        full_path = os.path.join(directory, cmd)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            print(f"{cmd} is {full_path}")
            return
    print(f"{cmd}: not found")


def find_executable(cmd):
    path_env = os.environ.get("PATH", "")
    for directory in path_env.split(os.pathsep):
        if not directory:
            continue
        full_path = os.path.join(directory, cmd)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None

def run_external(cmd, args):
    executable = find_executable(cmd)

    if executable is None:
        print(f"{cmd}: command not found")
        return

    pid = os.fork()

    if pid == 0:
        # Child process
        try:
            os.execv(executable, [cmd] + args)
        except Exception as e:
            print(f"exec error: {e}", file=sys.stderr)
            os._exit(1)
    else:
        # Parent process waits
        os.waitpid(pid, 0)


BUILTINS = {
    "type": type_command,
    "echo": lambda *args: print(" ".join(args)),
    "exit": lambda code=0, *_: sys.exit(int(code)),
    "pwd": lambda: print(os.getcwd()),
    "cd": lambda path=".": (
        os.chdir(os.path.expanduser(path)) if os.path.isdir(os.path.expanduser(path))
        else print(f"cd: {path}: No such file or directory")
    ),

}

def main():
    # Uncomment this block to pass the first stage

    while True:
        try:

            sys.stdout.write("$ ")
            sys.stdout.flush()

            # Wait for user input
            command = input().split()
            cmd = command[0]
            args = command[1:]

            if cmd in BUILTINS:
                BUILTINS[cmd](*args)
            else:
                # print(f"{cmd}: command not found")
                run_external(cmd, args)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    main()
