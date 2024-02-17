class ramloc:
    def __init__(self, loc):
        self.loc = loc
        self.val = self.loc
    def add_to_exe(self, exe, regs, sys, file, program, idx, dest_reg="gpr11"): # loads the value in the ram location to gpr12
        if self.loc in regs.keys(): # accessing a register
            exe.append("00001100" + regs[self.loc] + regs[dest_reg])
        else: # accessing using imm
            exe.append("00001101" + num_to_32b(self.loc, find_base(self.loc), sys, file, program, idx) + regs[dest_reg])

class register:
    def __init__(self, reg, regs):
        self.reg = reg
        self.bin = regs[reg]
        self.val = reg

class other:
    def __init__(self, val):
        self.val = val

class string:
    def __init__(self, val):
        self.val = val.replace(r"\n", "\n").replace(r"\t", "\t").replace(r"\0", "\0").replace(r"\\", "\\").replace(r"\'", "\'").replace(r"\"", "\"")
        self.len = len(self.val)

def err(message, sys, filename, program, idx):
    print(f"\nplow ERR: {message} in {filename}:{idx+1}")
    print(f"{idx+1}\t{program[idx]}")
    sys.exit(1)

def reg_err(sys, filename, program, idx):
    err("not a valid register", sys, filename, program, idx)

def num_to_32b(num: str, base: int, sys, filename, program, idx):
    if int(num, base) > 2**32:
        err(f"Number '{num}' (dec: '{int(num, base)}') over u32 capcity of '{2**32}'", sys, filename, program, idx)
    return format(int(num, base), "032b")

def num_to_64b(num: str, base: int, sys, filename, program, idx, multiplyby=1):
    if int(num, base) * multiplyby > 2**64:
        err(f"Number '{num}' (dec: '{int(num, base) * multiplyby}') over u64 capcity of '{2**64}'", sys, filename, program, idx)
    return format(int(num, base) * multiplyby, "064b")

def num_to_8b(num: str, base: int, sys, filename, program, idx):
    if int(num, base) > 2**8:
        err(f"Number '{num}' (dec: '{int(num, base)}') over u8 capcity of '{2**8}'", sys, filename, program, idx)
    return format(int(num, base), "08b")

def num_to_16b(num: str, base: int, sys, filename, program, idx):
    if int(num, base) > 2**16:
        err(f"Number '{num}' (dec: '{int(num, base)}') over u16 capcity of '{2**16}'", sys, filename, program, idx)
    return format(int(num, base), "016b")

def is_int(val):
    return all(v in "0123456789" for v in val)

def find_base(token):
    if len(token) >= 2 and token[0:2].lower() in ("0b", "0x"):
        if token[0:2].lower() == "0b":
            return 2
        return 16
    else:
        return 10

def isLocation(value):
    if typeof(value) in ("ramloc", "register"):
        return True
    return False

def opcode(opcode: int) -> str:
    return format(opcode, "08b")

def imm8(imm: int) -> str:
    return format(imm, "08b")

def typeof(val) -> str:
    return type(val).__name__

def compile(file: str, sys):
    import time
    start_time = time.time()
    with open(file, "r") as actual_file:
        program = actual_file.readlines()
        actual_file.close()
    file_no_ext = ".".join(file.split(".")[:-1])
    program = [line.strip() for line in program]
    print(f"PLOW: {file} -> {file_no_ext}.pemu", end="")
    tokens = [""]

    exe = []
    regs = {"rpr": "00000000", "parr":"00000001", "car":"00000010", "rar":"00000011", "ltr0":"00000100", "ltr1":"00000101", "ltr2": "00000110", "ltr3":"00000111",
            "prvr":"00001000", "fr0":"00001001", "fr1":"00001010", "fr2":"00001011", "fr3":"00001100", "fr4":"00001101", "gpr0":"00001110", "gpr1":"00001111",
            "gpr2":"00010000", "gpr3":"00010001", "gpr4":"00010010", "gpr5":"00010011", "gpr6":"00010100", "gpr7":"00010101", "gpr8":"00010110", "gpr9":"00010111",
            "gpr10":"00011000", "gpr11":"00011001", "gpr12":"00011010"}
    for idx, line in enumerate(program):
        if len(line) < 4:
            continue
        if line[0:2] == "//" or line[0] == "#":
            continue
        instring = False
        del tokens
        tokens: list[ramloc | other | register | string] = [""]
        for i, v in enumerate(line):
            if not instring:
                match v:
                    case " ":
                        tokens.append("")
                    case '"':
                        tokens.append('"')
                        instring = True
                    case "(" | ")" | "," | ">":
                        tokens.append(v)
                        tokens.append("")
                    case _:
                        tokens[len(tokens) - 1] += v
            else:
                match v:
                    case '"':
                        tokens[len(tokens) - 1] += '"'
                        instring = False
                        tokens.append("")
                    case _:
                        tokens[len(tokens) - 1] += v
        i = 0
        while i < len(tokens):
            if tokens[i] == "":
                del tokens[i]
            else:
                i += 1

        print(tokens)
        # token parser
        for i, v in enumerate(tokens):
            if len(v) > 2 and v[0] == "[" and v[-1] == "]": # ram location ref
                tokens[i] = ramloc(v[1:-1])
            else:
                if v in regs.keys():
                    tokens[i] = register(v, regs)
                else:
                    if len(v) > 2 and (v[0] == '"' or v[0] == "'") and (v[-1] == '"' or v[-1] == "'"):
                        tokens[i] = string(v[1:-1])
                    else:
                        tokens[i] = other(v)
                
        if typeof(tokens[0]) != "other":
            err("unknown instruction", sys, file, program, idx)
        match tokens[0].val:
            case "exit":
                if len(tokens) != 2:
                    err("not enough tokens", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "register":
                        exe.append("00000000" + tokens[1].bin)
                    case "ramloc":
                        tokens[1].add_to_exe(exe, regs, sys, file, program, idx)
                        exe.append("00000000" + regs["gpr11"])
                    case "other":
                        exe.append("00000001" + num_to_16b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                    case "string":
                        err("cannot exit with string", sys, file, program, idx)
            case "mov":
                if len(tokens) != 4:
                    err("not enough tokens", sys, file, program, idx)
                if typeof(tokens[2]) != "other" or tokens[2].val != ">":
                    err("there must be a move operator between the source and destination", sys, file, program, idx)
                match f"{typeof(tokens[1])} {typeof(tokens[3])}":
                    case "other other":
                        if not tokens[3].val in ("stackSizeB", "stackSizeKB", "stackSizeKiB", "stackSizeMB", "stackSizeMiB"):
                            err("not a valid destination register", sys, file, program, idx)
                        match tokens[3].val:
                            case "stackSizeB":
                                exe.append(opcode(70) + num_to_64b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                            case "stackSizeKB":
                                exe.append(opcode(70) + (num_to_64b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx, 1000)))
                            case "stackSizeKiB":
                                exe.append(opcode(70) + (num_to_64b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx, 1024)))
                            case "stackSizeMB":
                                exe.append(opcode(70) + (num_to_64b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx, 1_000_000)))
                            case "stackSizeMiB":
                                exe.append(opcode(70) + (num_to_64b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx, 1_048_576)))
                    case "string register":
                        if tokens[1].len != 1:
                            err("cannot move a multi char string into a register", sys, file, program, idx)
                        exe.append("00000010" + tokens[3].bin + num_to_32b(str(ord(tokens[1].val)), find_base(str(ord(tokens[1].val))), sys, file, program, idx))    
                    case "other register":
                        if tokens[1].val == "CARL":
                            exe.append("01000011" + tokens[3].bin)
                        else:
                            exe.append("00000010" + tokens[3].bin + num_to_32b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                    case "register register":
                        exe.append("00000011" + tokens[1].bin + tokens[3].bin)
                    case "ramloc register":
                        tokens[1].add_to_exe(exe, regs, sys, file, program, idx, dest_reg=tokens[3].reg)
                    case "register ramloc":
                        if tokens[3].loc in regs.keys(): # accessing a register
                            exe.append(opcode(8) + tokens[1].bin + regs[tokens[3].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + tokens[1].bin + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx))
                    case "other ramloc":
                        if tokens[3].loc in regs.keys(): # accessing a register
                            exe.append(opcode(8) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs[tokens[3].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx))
                    case _:
                        err()
            case "pri":
                if len(tokens) != 2:
                    err("not enough tokens", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "other":
                        exe.append("00110100" + num_to_32b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                    case "register":
                        exe.append("00110011" + tokens[1].bin)
                    case "ramloc":
                        if tokens[1].loc in regs.keys(): # accessing a register
                            exe.append("00110101" + regs[tokens[1].loc])
                        else: # accessing using imm
                            exe.append("00110110" + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx))
                    case "string":
                        err(f"pri prints an integer, not string: '{tokens[1].val}'", sys, file, program, idx)
            case "prc":
                if len(tokens) != 2:
                    err("not enough tokens", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "other":
                        exe.append("00111000" + num_to_32b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                    case "register":
                        exe.append("00110111" + tokens[1].bin)
                    case "ramloc":
                        if tokens[1].loc in regs.keys(): # accessing a register
                            exe.append("00111010" + regs[tokens[1].loc])
                        else: # accessing using imm
                            exe.append("00111011" + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx))
                    case "string":
                        if tokens[1].len != 1:
                            err(f"Cannot print a string ('{tokens[1].val}') with a length of {tokens[1].len}, only a string with the length 1", sys, file, program, idx)
                        exe.append(opcode(56) + format(ord(tokens[1].val), "032b"))
            case "prs":
                if len(tokens) != 2:
                    err(f"not enough tokens, expected 2 but found {len(tokens)}", sys, file, program, idx)
                if typeof(tokens[1]) != "string":
                    err("cannot print a non-string string", sys, file, program, idx)
                exe.append(opcode(57) + "".join(format(ord(v), "08b") for v in tokens[1].val))
            case "input":
                if len(tokens) == 1:
                    exe.append(opcode(60))
                elif len(tokens) == 2:
                    if typeof(tokens[1]) != "string":
                        err()
                    exe.append(opcode(57) + "".join(format(ord(v), "08b") for v in tokens[1].val))
                    exe.append(opcode(60))
                else:
                    err("not enough tokens", sys, file, program, idx)
            case "add": # add ( 5 , 7 ) > gpr0
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 9 but found {len(tokens)}", sys, file, program, idx)
                if not (typeof(tokens[1]) == typeof(tokens[3]) == typeof(tokens[5]) == typeof(tokens[6]) == "other"):
                    err("Unknown syntax", sys, file, program, idx)
                if tokens[1].val != "(":
                    err("An open parenthesis must be the 2nd token", sys, file, program, idx)
                if tokens[3].val != ",":
                    err("There must be a comma seperating arguments", sys, file, program, idx)
                if tokens[5].val != ")":
                    err("Closing parenthesis not found after 2nd arguement". sys, file, program, idx)
                if tokens[6].val != ">":
                    err("Move operator '>' not found after arguements in parenthesis", sys, file, program, idx)
                if not isLocation(tokens[7]):
                    err("Not a valid destination for result", sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])} {typeof(tokens[7])}":
                    case "other other register":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(17) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register other register":
                        exe.append(opcode(17) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(16) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "other register register":
                        exe.append(opcode(17) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(17) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register other ramloc":
                        exe.append(opcode(17) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(16) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        exe.append(opcode(17) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case _:
                        err(f"could not add data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "sub": # add ( 5 , 7 ) > gpr0
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 9 but found {len(tokens)}", sys, file, program, idx)
                if not (typeof(tokens[1]) == typeof(tokens[3]) == typeof(tokens[5]) == typeof(tokens[6]) == "other"):
                    err("Unknown syntax", sys, file, program, idx)
                if tokens[1].val != "(":
                    err("An open parenthesis must be the 2nd token", sys, file, program, idx)
                if tokens[3].val != ",":
                    err("There must be a comma seperating arguments", sys, file, program, idx)
                if tokens[5].val != ")":
                    err("Closing parenthesis not found after 2nd arguement". sys, file, program, idx)
                if tokens[6].val != ">":
                    err("Move operator '>' not found after arguements in parenthesis", sys, file, program, idx)
                if not isLocation(tokens[7]):
                    err("Not a valid destination for result", sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])} {typeof(tokens[7])}":
                    case "other other register":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(19) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register other register":
                        exe.append(opcode(19) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(18) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "other register register":
                        exe.append(opcode(19) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(19) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register other ramloc":
                        exe.append(opcode(19) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(18) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(19) + regs["gpr11"] + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case _:
                        err(f"could not subtract data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "mult": # add ( 5 , 7 ) > gpr0
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 9 but found {len(tokens)}", sys, file, program, idx)
                if not (typeof(tokens[1]) == typeof(tokens[3]) == typeof(tokens[5]) == typeof(tokens[6]) == "other"):
                    err("Unknown syntax", sys, file, program, idx)
                if tokens[1].val != "(":
                    err("An open parenthesis must be the 2nd token", sys, file, program, idx)
                if tokens[3].val != ",":
                    err("There must be a comma seperating arguments", sys, file, program, idx)
                if tokens[5].val != ")":
                    err("Closing parenthesis not found after 2nd arguement". sys, file, program, idx)
                if tokens[6].val != ">":
                    err("Move operator '>' not found after arguements in parenthesis", sys, file, program, idx)
                if not isLocation(tokens[7]):
                    err("Not a valid destination for result", sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])} {typeof(tokens[7])}":
                    case "other other register":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(21) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register other register":
                        exe.append(opcode(21) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(20) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "other register register":
                        exe.append(opcode(21) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(21) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register other ramloc":
                        exe.append(opcode(21) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(20) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        exe.append(opcode(21) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case _:
                        err(f"could not multiply data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "div": # add ( 5 , 7 ) > gpr0
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 9 but found {len(tokens)}", sys, file, program, idx)
                if not (typeof(tokens[1]) == typeof(tokens[3]) == typeof(tokens[5]) == typeof(tokens[6]) == "other"):
                    err("Unknown syntax", sys, file, program, idx)
                if tokens[1].val != "(":
                    err("An open parenthesis must be the 2nd token", sys, file, program, idx)
                if tokens[3].val != ",":
                    err("There must be a comma seperating arguments", sys, file, program, idx)
                if tokens[5].val != ")":
                    err("Closing parenthesis not found after 2nd arguement". sys, file, program, idx)
                if tokens[6].val != ">":
                    err("Move operator '>' not found after arguements in parenthesis", sys, file, program, idx)
                if not isLocation(tokens[7]):
                    err("Not a valid destination for result", sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])} {typeof(tokens[7])}":
                    case "other other register":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(23) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register other register":
                        exe.append(opcode(23) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(22) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "other register register":
                        exe.append(opcode(23) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(23) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register other ramloc":
                        exe.append(opcode(23) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(22) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(23) + regs["gpr11"] + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a register
                            exe.append(opcode(4) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(5) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case _:
                        err(f"could not add data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case _:
                err("unknown instruction", sys, file, program, idx)
    print(", completed in {}ms".format((time.time() - start_time) * 1000))
    exe = "".join(exe)
    exe = bytes([int(exe[i:i+8], 2) for i in range(0, len(exe), 8)])
    if __name__ == "__main__":
        with open(f"{file_no_ext}.pemu", "wb") as file:
            file.write(exe)
            file.close()
    else:
        return exe