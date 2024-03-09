import sys, os
compilers = ("pemu", "plow")
compilers_location = "" # meaning cwd 
compilers_flags = [
                    ["--unstable", "--notimefeedback", "--nodeletewaste", "--norun"],
                    ["--unstable",  "--notimefeedback", "--nodeletewaste", "--norun", "--lib"]
                ]
version = 1.0
if not os.path.isfile("linker_settings.txt"):
    with open("linker_settings.txt", "w") as file:
        file.close()
with open("linker_settings.txt", "r") as file:
    settings = file.readlines()
if len(settings) != 1 or settings[0] not in ("False", "True"):
    print("Corrupted linker_settings.txt file, fixing corruption setting settings to default.")
    print("There will now be a delay between compilation steps.")
    with open("linker_settings.txt", "w") as fix_corruption:
        fix_corruption.write("True")
if settings[0] == "False":
    delay = False
else:
    delay = True
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
                case "getDelayEnabled":
                    if settings[0] == "False":
                        print("Compilation delay is off")
                    else:
                        print("Compilation delay is on")
                case "toggleDelay":
                    if settings[0] == "False":
                        with open("linker_settings.txt", "w") as file:
                            file.write("True")
                        print("Compilation delay turned on")
                    else:
                        with open("linker_settings.txt", "w") as file:
                            file.write("False")
                        print("Compilation delay turned off")
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
            if os.path.isfile(sys.argv[1]):
                match sys.argv[1].split(".")[-1]:
                    case "pemu":
                        print(f"You have forgotton to specify the compiler, here is the command you intended to run: \".\\pemu pemu {sys.argv[1]} {sys.argv[2]}\"")
                    case "plow":
                        print(f"You have forgotton to specify the compiler, here is the command you intended to run: \".\\pemu plow {sys.argv[1]} {sys.argv[2]}\"")
                    case _:
                        print(f"Please specify compiler, and {sys.argv[1].split(".")[-1]} is not a valid file extension for pemu or plow")
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
        if os.path.isfile("source code\\pemu.py"):
           from compilers import pemu
        else:
            print("source code\\pemu.py compiler not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if os.path.isfile("source code\\plow.py"):
            from compilers import plow
        else:
            print("source code\\plow.py compiler not found")
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
        if os.path.isfile("source code\\pemu.py"):
           from compilers import pemu
        else:
            print("source code\\pemu.py compiler not found")
            print("please run '.\\pemu' to get help, or read the README.txt file under the 'docs' directory")
            sys.exit(1)
        if os.path.isfile("source code\\plow.py"):
            from compilers import plow
        else:
            print("source code\\plow.py compiler not found")
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
                pemu_program = plow.compile(sys.argv[2], sys)
                if "--lib" in sys.argv:
                    with open(sys.argv[3], "wb") as pemu_file:
                        pemu_file.write(pemu_program)
                        pemu_file.close()
                else:
                    pemu.get_pemu_file_dependant(os, pemu_program, sys.argv[2], ".".join(sys.argv[3].split(".")[:-1]), show_time, delete_waste, unstable, run)
