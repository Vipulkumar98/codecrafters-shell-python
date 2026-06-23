import sys
import os


def tokenize_command(command_line):
    tokens = []
    current_token = []
    in_single_quotes = False
    in_double_quotes = False
    i = 0
    
    while i < len(command_line):
        char = command_line[i]

        # Handle escaped characters
        if char == '\\' and not in_single_quotes and not in_double_quotes:
            i += 1
            if i < len(command_line):
                current_token.append(command_line[i])
                i += 1
            else:
                current_token.append('\\')
                i += 1
            continue

        
        if char == "'" and not in_double_quotes:
            # Start of quoted section
            in_single_quotes = not in_single_quotes
            i += 1
            continue
        elif char == '"' and not in_single_quotes:
            # Start of quoted section
            in_double_quotes = not in_double_quotes
            i += 1
            continue
        # elif in_single_quotes or in_double_quotes:
        #     # Inside quotes: treat everything literally
        #     current_token.append(char)
        #     i += 1
        elif in_single_quotes:
            # Inside quotes: treat everything literally
            current_token.append(char)
            i += 1
        elif in_double_quotes:
            if char == '\\':
                i += 1
                if i < len(command_line):
                    next_char = command_line[i]
                    if next_char in ('"', '\\'):        
                        current_token.append(next_char) 
                    else:
                        # For all other characters after \, keep BOTH \ and the char
                        current_token.append('\\')
                        current_token.append(next_char)
                    i += 1
                else:
                    # \ at the very end of input → keep the \
                    current_token.append('\\')
            else:
                # normal character inside ""
                current_token.append(char)
                i += 1
        elif char in (' ', '\t'):
            # Whitespace outside quotes: token delimiter
            if current_token:
                tokens.append(''.join(current_token))
                current_token = []
            i += 1
        else:
            # Regular character outside quotes
            current_token.append(char)
            i += 1
    
    # Add the last token if any
    if current_token:
        tokens.append(''.join(current_token))
    
    return tokens

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


def parse_redirect(args):
    clean_tokens = []
    stdout_file = stderr_file = None
    stdout_append = stderr_append = False
    i = 0
    while i < len(args):
        token = args[i]
        if token in ('>', '1>', '>>', '1>>'):
            if i + 1 >= len(args):
                print("Syntax error: expected filename after redirection operator")
                return None, None, None, False, False
            stdout_file = args[i + 1]
            stdout_append = token in ('>>', '1>>')
            i += 2
        elif token in ('2>', '2>>'):
            if i + 1 >= len(args):
                print("Syntax error: expected filename after redirection operator")
                return None, None, None, False, False
            stderr_file = args[i + 1]
            stderr_append = (token == '2>>')
            i += 2
        else:
            clean_tokens.append(token)
            i += 1
    return clean_tokens, stdout_file, stderr_file, stdout_append, stderr_append

def apply_redirect(stdout_file=None, stderr_file=None, stdout_append=False, stderr_append=False):
    if stdout_file:
        flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if stdout_append else os.O_TRUNC)
        fd = os.open(stdout_file, flags, 0o644)
        os.dup2(fd, 1)
        os.close(fd)
    if stderr_file:
        flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if stderr_append else os.O_TRUNC)
        fd = os.open(stderr_file, flags, 0o644)
        os.dup2(fd, 2)
        os.close(fd)

def run_external(cmd, args, stdout_file=None, stderr_file=None, stdout_append=False, stderr_append=False):
    executable = find_executable(cmd)
    if executable is None:
        print(f"{cmd}: command not found")
        return
    # Fork a child process to run the external command
    pid = os.fork()
    # In the child process, apply redirection and execute the command
    if pid == 0:
        apply_redirect(stdout_file, stderr_file, stdout_append, stderr_append)
        try:
            # Replace the current process with the external command
            os.execv(executable, [cmd] + args)
        except Exception as e:
            print(f"exec error: {e}", file=sys.stderr)
            os._exit(1)
    else:
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
            # command = input().split()

            command = tokenize_command(input())

            # if not command:
            #     continue


            cmd = command[0]
            args = command[1:]

            clean_args, stdout_file, stderr_file, stdout_append, stderr_append = parse_redirect(args)

            if clean_args is None:
                continue

            if cmd in BUILTINS:
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                out_f = err_f = None
                try:
                    if stdout_file:
                        out_f = open(stdout_file, 'a' if stdout_append else 'w')
                        sys.stdout = out_f
                    if stderr_file:
                        err_f = open(stderr_file, 'a' if stderr_append else 'w')
                        sys.stderr = err_f
                    BUILTINS[cmd](*clean_args)
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                    if out_f:
                        out_f.close()
                    if err_f:
                        err_f.close()
            else:
                run_external(cmd, clean_args, stdout_file, stderr_file, stdout_append, stderr_append)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()


if __name__ == "__main__":
    main()
