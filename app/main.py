import sys


def main():
    # Uncomment this block to pass the first stage

    while True:
        sys.stdout.write("$ ")


        # Wait for user input
        command = input()
        if command == "exit":
            sys.exit(0)
        if command == "echo":
            print(command)
            

        print(f"{command}: command not found")



if __name__ == "__main__":
    main()
