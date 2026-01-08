import sys


def main():
    # Uncomment this block to pass the first stage

    while True:
        sys.stdout.write("$ ")


        # Wait for user input
        command = input().strip()
        if command == "exit":
            sys.exit(0)

        if command.startswith("echo "):
            echo_text = command[5:]
            print(echo_text)
            continue

        print(f"{command}: command not found")



if __name__ == "__main__":
    main()
