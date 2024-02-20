import sys, os
compilers = ("pemu", "plow")
compilers_location = "" # meaning cwd 
compilers_flags = [
                    ["--unstable", "--notimefeedback", "--nodeletewaste", "--norun"],
                    ["--unstable",  "--notimefeedback", "--nodeletewaste", "--norun"]
                ]
version = 1.0
match len(sys.argv):
    case 1: # just .\pemu
        if input("Display docs\\README.txt? (y/n)").lower() == "y":
            if os.path.isfile("docs\\README.txt"):
                print("README.txt will be displayed in terminal soon...")
                with open("docs\\README.txt") as readme:
                    print(readme.read())
            else:
                print("Could not find README.txt file")
    case 2: # .\pemu [compiler]
        if not sys.argv[1] in compilers:
            match sys.argv[1]:
                case "getPATH":
                    print(os.environ.get("PATH", "").replace(";", "\n"))
                case "getRamSize":
                    import psutil
                    print(f"total memory in GB: {psutil.virtual_memory().total / 1_000_000_000}")
                case _:
                    print(f"unknown compiler, please check version. This is version {version}")
        else:
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
    case 3: # .\pemu [compiler] [source code]
        if sys.argv[1] in compilers:
            if os.path.isfile(sys.argv[2]):
                print("please enter an output file")
            else:
                print("the entered source code is not a valid file, and an output file was not specified")
        else:
            print(f"unknown compiler, please check version. This is version {version}")
        print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
    case 4: # .\pemu [compiler] [source code] [output] STANDARD COMPILATION
        if not sys.argv[1] in compilers:
            print(f"unknown compiler, please check version. This is version {version}")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if not os.path.isfile(sys.argv[2]):
            print("source code file not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if os.path.isfile("compilers\\pemu.py"):
           from compilers import pemu
        else:
            print("compilers\\pemu.py compiler not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if os.path.isfile("compilers\\plow.py"):
            from compilers import plow
        else:
            print("compilers\\plow.py compiler not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        match sys.argv[1]:
            case "pemu":
                pemu.get_pemu_file_independent(os, sys.argv[2], ".".join(sys.argv[2].split(".")[:-1]))
            case "plow":
                pemu.get_pemu_file_dependant(os, plow.compile(sys.argv[2], sys), sys.argv[2], ".".join(sys.argv[3].split(".")[:-1]))
    case 5: # .\pemu [compiler] [source code] [output] [flags]
        if not sys.argv[1] in compilers:
            print(f"unknown compiler, please check version. This is version {version}")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if not os.path.isfile(sys.argv[2]):
            print("source code file not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if os.path.isfile("compilers\\pemu.py"):
           from compilers import pemu
        else:
            print("compilers\\pemu.py compiler not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if os.path.isfile("compilers\\plow.py"):
            from compilers import plow
        else:
            print("compilers\\plow.py compiler not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        match sys.argv[1]:
            case "pemu":
                pemu_flags = sys.argv[4:]
                if all([v in compilers_flags[0] for v in pemu_flags]):
                    if "--unstable" in pemu_flags:
                        unstable = True
                    else:
                        unstable = False
                    if "--notimefeedback" in sys.argv:
                        show_time = False
                    else:
                        show_time = True
                    if "--nodeletewaste" in sys.argv:
                        delete_waste = False
                    else:
                        delete_waste = True
                    if "--norun" in sys.argv:
                        run = False
                    else:
                        run = True
                else:
                    print("unknown flag in flags")
                    sys.exit(1)
                pemu.get_pemu_file_independent(os, sys.argv[2], ".".join(sys.argv[2].split(".")[:-1]), show_time, delete_waste, unstable, run)
            case "plow":
                plow_flags = sys.argv[4:]
                if all([v in compilers_flags[1] for v in plow_flags]):
                    if "--unstable" in plow_flags:
                        unstable = True
                    else:
                        unstable = False
                    if "--notimefeedback" in sys.argv:
                        show_time = False
                    else:
                        show_time = True
                    if "--nodeletewaste" in sys.argv:
                        delete_waste = False
                    else:
                        delete_waste = True
                    if "--norun" in sys.argv:
                        run = False
                    else:
                        run = True
                else:
                    print("unknown flag in flags")
                    sys.exit(1)
                plow_program = plow.compile(sys.argv[2], sys)
                pemu.get_pemu_file_dependant(os, plow_program, sys.argv[2], ".".join(sys.argv[3].split(".")[:-1]), show_time, delete_waste, unstable, run)
