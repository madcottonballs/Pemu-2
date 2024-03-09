"""NOTES:
        still need to add entire LU
        need to add char functionality for cmp
        cmd is missing variable runtime commands
"""

class ramloc:
    def __init__(self, loc):
        self.loc = loc
        self.val = self.loc
    def get_value(self, exe, regs, sys, file, program, idx, dest_reg="gpr11"): # loads the value in the ram location to gpr11
        if self.loc in regs.keys(): # accessing a ram location using a register
            exe.append(opcode(12) + regs[self.loc] + regs[dest_reg])
        else: # accessing using imm
            exe.append(opcode(13) + num_to_32b(self.loc, find_base(self.loc), sys, file, program, idx) + regs[dest_reg])

class register:
    def __init__(self, reg, regs):
        self.bin = regs[reg]
        self.val = reg

class flag:
    def __init__(self, flag, flags):
        self.bin = flags[flag]
        self.val = flag

class other:
    def __init__(self, val):
        self.val = val
    def mov_to_reg32(self, exe, regs, reg):
        exe.append(opcode(2) + regs[reg] + num_to_32b(self.val, find_base(self.val)))

class string:
    def __init__(self, val: str):
        self.val = val.replace(
            r"\n", "\n").replace(
            r"\t", "\t").replace(
            r"\0", "\0").replace(
            r"\\", "\\").replace(
            r"\'", "\'").replace(
            r"\"", "\"").replace(
            r"\r", "\r")
        self.len = len(self.val)

def err(message, sys, filename, program, idx):
    print(f"\nplow compilation ERR: {message} in {filename}:{idx+1}")
    print(f"{idx+1}\t{program[idx]}")
    sys.exit(1)

def reg_err(sys, filename, program, idx):
    err("not a valid register", sys, filename, program, idx)

def num_to_32b(num: str, base: int, sys, filename, program, idx):
    is_int(num, base, sys, filename, program, idx)
    if int(num, base) > 2**32:
        err(f"Number '{num}' (dec: '{int(num, base)}') over u32 capcity of '{2**32}'", sys, filename, program, idx)
    return format(int(num, base), "032b")

def num_to_64b(num: str, base: int, sys, filename, program, idx, multiplyby=1):
    is_int(num, base, sys, filename, program, idx)
    if int(num, base) * multiplyby > 2**64:
        err(f"Number '{num}' (dec: '{int(num, base) * multiplyby}') over u64 capcity of '{2**64}'", sys, filename, program, idx)
    return format(int(num, base) * multiplyby, "064b")

def num_to_8b(num: str, base: int, sys, filename, program, idx):
    is_int(num, base, sys, filename, program, idx)
    if int(num, base) > 2**8:
        err(f"Number '{num}' (dec: '{int(num, base)}') over u8 capcity of '{2**8}'", sys, filename, program, idx)
    return format(int(num, base), "08b")

def num_to_16b(num: str, base: int, sys, filename, program, idx):
    is_int(num, base, sys, filename, program, idx)
    if int(num, base) > 2**16:
        err(f"Number '{num}' (dec: '{int(num, base)}') over u16 capcity of '{2**16}'", sys, filename, program, idx)
    return format(int(num, base), "016b")

def is_int(num, base, sys, filename, program, idx):
    if base == 0:
        err("Expected an integer but found invalid chars", sys, filename, program, idx)
    if base == 10:
        if not all(v in "0123456789" for v in str(num)[2:]):
            err("Expected an integer found invalid chars", sys, filename, program, idx)
    if base == 2:
        if not all(v in "01" for v in str(num)[2:]):
            err("Expected a binary int, found an invalid char", sys, filename, program, idx)
    if base == 16:
        if not all(v in "0123456789abcdefABCDEF" for v in str(num)[2:]):
            err("Expected a hexadecimal int, found an invalid char ", sys, filename, program, idx)

def find_base(token):
    if len(token) >= 2 and token[0:2].lower() in ("0b", "0x"):
        if token[0:2].lower() == "0b":
            return 2
        return 16
    if not all(v in "0123456789" for v in token[2:]):
        return 0
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
    flags = {"ls_flag":"00000000", "gt_flag":'00000001', "e_flag":"00000010", "ne_flag":"00000011", "over_flag":"00000100", "undr_flag":"00000101"}
    for idx, line in enumerate(program):
        if len(line) < 4: # skips if the line is empty
            continue
        if line[0:2] == "//" or line[0] == "#": # skips is the line is a comment
            continue
        instring = False
        del tokens
        tokens: list[ramloc | other | register | string | flag] = [""]
        for i, v in enumerate(line):
            if not instring:
                match v:
                    case " ":
                        tokens.append("")
                    case '"':
                        tokens.append('"')
                        instring = True
                    case "(" | ")" | "," | ">" | "." | ":":
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

        #print(tokens)
        # token parser
        for i, v in enumerate(tokens):
            if len(v) > 2 and v[0] == "[" and v[-1] == "]": # ram location ref
                tokens[i] = ramloc(v[1:-1])
            else:
                if v in regs.keys():
                    tokens[i] = register(v, regs)
                elif v in flags.keys():
                    tokens[i] = flag(v, flags)
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
                    err("unknown syntax structure", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "register":
                        exe.append("00000000" + tokens[1].bin)
                    case "ramloc":
                        tokens[1].get_value(exe, regs, sys, file, program, idx)
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
                    case "flag register":
                        exe.append(opcode(14) + tokens[1].bin + tokens[3].bin)
                    case "flag ramloc":
                        if tokens[3].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(15) + tokens[1].bin + regs[tokens[3].loc])
                        else: # accessing using imm
                            tokens[3].mov_to_reg32(exe, regs, "gpr11")
                            exe.append(opcode(15) + tokens[1].bin + regs["gpr11"])
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
                    
                    case "other register":
                        if tokens[1].val == "CARL":
                            exe.append(opcode(67) + tokens[3].bin)
                        else:
                            exe.append(opcode(2) + tokens[3].bin + num_to_32b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                    case "other ramloc":
                        if tokens[1].val == "CARL":
                            exe.append(opcode(67) + regs["gpr11"])
                            if tokens[3].loc in regs.keys(): # accessing a ram location using a register
                                exe.append(opcode(8) + regs[tokens[3].loc] + regs["gpr11"]) # green light
                            else: # accessing using imm
                                exe.append(opcode(9) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx) + regs["gpr11"])
                        else:
                            if tokens[3].loc in regs.keys(): # accessing a ram location using a register
                                exe.append(opcode(8) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs[tokens[3].loc])
                            else: # accessing using imm
                                exe.append(opcode(10) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx))
                    case "string register":
                        if tokens[1].len != 1:
                            err("cannot move a multi char string into a register", sys, file, program, idx)
                        exe.append("00000010" + tokens[3].bin + num_to_32b(str(ord(tokens[1].val)), find_base(str(ord(tokens[1].val))), sys, file, program, idx))    
                    case "string ramloc":
                        if tokens[1].len != 1:
                            err("cannot move a multi char string into a register", sys, file, program, idx)
                        if tokens[3].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + num_to_32b(str(ord(tokens[1].val)), 10, sys, file, program, idx) + regs[tokens[3].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + num_to_32b(str(ord(tokens[1].val)), 10, sys, file, program, idx) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx))                        
                    case "register register":
                        exe.append("00000011" + tokens[1].bin + tokens[3].bin)
                    case "register ramloc":
                        if tokens[3].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + tokens[1].bin + regs[tokens[3].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + tokens[1].bin + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx))
                    case "ramloc register":
                        tokens[1].get_value(exe, regs, sys, file, program, idx, dest_reg=tokens[3].reg)
                    case "ramloc ramloc":
                        if tokens[1].loc in regs.keys():
                            if tokens[3].loc in regs.keys(): # shl [gpr0], [gpr1]
                                exe.append(opcode(4) + regs[tokens[1].loc] + regs[tokens[2].loc])
                            else: # shl [gpr0], [0]
                                exe.append(opcode(5) + regs[tokens[1].loc] + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx))
                        else: # shl [0], 
                            if tokens[3].loc in regs.keys(): # shl [0], [gpr1]
                                exe.append(opcode(6) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs[tokens[3].loc])
                            else: # shl [0], [1]
                                exe.append(opcode(7) + 
                                            num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) +
                                            num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx))

                    case _:
                        err()
            case "bin":
                if len(tokens) != 2:
                    err("not enough tokens", sys, file, program, idx)
                if typeof(tokens[1]) != "string":
                    err("cannot conver that to a binary instruction", sys, file, program, idx)
                exe.append(tokens[1].val)
            case "cmp": # cmp ( val , val )
                if len(tokens) != 6:
                    err(f"not enough tokens, expected 6 but found {len(tokens)}", sys, file, program, idx)
                if not (typeof(tokens[1]) == typeof(tokens[3]) == typeof(tokens[5]) == "other"):
                    err("Unknown syntax", sys, file, program, idx)
                if tokens[1].val != "(":
                    err("An open parenthesis must be the 2nd token", sys, file, program, idx)
                if tokens[3].val != ",":
                    err("There must be a comma seperating arguments", sys, file, program, idx)
                if tokens[5].val != ")":
                    err("Closing parenthesis not found after 2nd arguement". sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])}":
                    case "other other":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(38) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx))
                    case "register other":
                        exe.append(opcode(38) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx))
                    case "register register":
                        exe.append(opcode(39) + tokens[2].bin + tokens[4].bin)
                    case "other register":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(39) + regs["gpr11"] + tokens[4].bin)
                    case "ramloc ramloc":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr12")
                        exe.append(opcode(39) + regs["gpr11"] + regs["gpr12"])
                    case "ramloc other":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(38) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx))
                    case "ramloc register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(39) + regs["gpr11"] + tokens[4].bin)
                    case "other ramloc":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[2].mov_to_reg32(exe, regs, "gpr12")
                        exe.append(opcode(39) + regs["gpr11"] + regs["gpr12"])
                    case "register ramloc":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(38) + regs["gpr11"] + tokens[2].bin)
                    case _:
                        err(f"could not add data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "pri":
                if len(tokens) != 2:
                    err("not enough tokens", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "other":
                        exe.append("00110100" + num_to_32b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                    case "register":
                        exe.append("00110011" + tokens[1].bin)
                    case "ramloc":
                        if tokens[1].loc in regs.keys(): # accessing a ram location using a register
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
                        if tokens[1].loc in regs.keys(): # accessing a ram location using a register
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
            case "implib":
                if len(tokens) != 2:
                    err(f"not enough tokens, expected 2 but found {len(tokens)}", sys, file, program, idx)
                if typeof(tokens[1]) != "string":
                    err("cannot print a non-string string", sys, file, program, idx)
                exe.append(opcode(71) + "".join(format(ord(v), "08b") for v in tokens[1].val))
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
            case "inc":
                if len(tokens) != 2:
                    err("not enough tokens", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "register":
                        exe.append(opcode(32) + tokens[1].bin)
                    case "ramloc":
                        if tokens[1].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(33) + tokens[1].bin)
                        else: # accessing using imm
                            exe.append(opcode(34) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx))
                    case _:
                        err(f"cannot increment a token of type '{typeof(tokens[1])}'", sys, file, program, idx)
            case "dec":
                if len(tokens) != 2:
                    err("not enough tokens", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "register":
                        exe.append(opcode(35) + tokens[1].bin)
                    case "ramloc":
                        if tokens[1].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(36) + tokens[1].bin)
                        else: # accessing using imm
                            exe.append(opcode(37) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx))
                    case _:
                        err(f"cannot increment a token of type '{typeof(tokens[1])}'", sys, file, program, idx)
            case "add": #DD SUB MULT DIV
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 8 but found {len(tokens)}", sys, file, program, idx)
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
                        result = int(num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx), 2) + int(num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx), 2)
                        exe.append(opcode(2) + tokens[7].bin + num_to_32b(str(result), 10, sys, file, program, idx))
                    case "other register register":
                        exe.append(opcode(17) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)
                    case "other ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(17) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)

                    case "register other register":
                        exe.append(opcode(17) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(16) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "register ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(16) + tokens[2].bin + regs["gpr11"] + tokens[7].bin)
                    
                    case "ramloc other register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(17) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "ramloc register register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(16) + regs["gpr11"] + tokens[4].bin + tokens[7].bin)
                    case "ramloc ramloc register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr12")
                        exe.append(opcode(16) + regs["gpr11"] + regs["gpr12"] + tokens[7].bin)
                    
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(17) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        exe.append(opcode(17) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other ramloc ramloc": # not done
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(17) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))

                    case "register other ramloc":
                        exe.append(opcode(17) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(16) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    
                    case _:
                        err(f"could not add data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "sub": #
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
                        result = int(num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx), 2) + int(num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx), 2)
                        exe.append(opcode(2) + tokens[7].bin + num_to_32b(str(result), 10, sys, file, program, idx))
                    case "other register register":
                        tokens[2].mov_to_reg32(exe, regs, "gpr11")
                        exe.append(opcode(18) + regs["gpr11"] + tokens[4].bin + tokens[7].bin)
                    case "other ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[2].mov_to_reg32(exe, regs, "gpr12")
                        exe.append(opcode(19) + regs["gpr12"] + regs["gpr11"] + tokens[7].bin)

                    case "register other register":
                        exe.append(opcode(19) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(18) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "register ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(18) + tokens[2].bin + regs["gpr11"] + tokens[7].bin)
                    
                    case "ramloc other register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(19) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "ramloc register register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(18) + regs["gpr11"] + tokens[4].bin + tokens[7].bin)
                    case "ramloc ramloc register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr12")
                        exe.append(opcode(18) + regs["gpr11"] + regs["gpr12"] + tokens[7].bin)
                    
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(19) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        tokens[2].mov_to_reg32(exe, regs, "gpr12")
                        exe.append(opcode(18) + regs["gpr12"] + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other ramloc ramloc": # not done
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[2].mov_to_reg32(exe, regs, "gpr12")
                        exe.append(opcode(18) + regs["gpr12"] + regs["gpr11"] + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))

                    case "register other ramloc":
                        exe.append(opcode(19) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(18) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    
                    case _:
                        err(f"could not add data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "mult": 
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
                        result = int(num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx), 2) + int(num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx), 2)
                        exe.append(opcode(2) + tokens[7].bin + num_to_32b(str(result), 10, sys, file, program, idx))
                    case "other register register":
                        exe.append(opcode(21) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)
                    case "other ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(21) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + tokens[7].bin)

                    case "register other register":
                        exe.append(opcode(21) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(20) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "register ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(20) + tokens[2].bin + regs["gpr11"] + tokens[7].bin)
                    
                    case "ramloc other register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(21) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "ramloc register register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(20) + regs["gpr11"] + tokens[4].bin + tokens[7].bin)
                    case "ramloc ramloc register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr12")
                        exe.append(opcode(20) + regs["gpr11"] + regs["gpr12"] + tokens[7].bin)
                    
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(21) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        exe.append(opcode(21) + tokens[4].bin + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other ramloc ramloc": # not done
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(21) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))

                    case "register other ramloc":
                        exe.append(opcode(21) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(20) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    
                    case _:
                        err(f"could not add data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "div": #
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
                        result = int(num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx), 2) + int(num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx), 2)
                        exe.append(opcode(2) + tokens[7].bin + num_to_32b(str(result), 10, sys, file, program, idx))
                    case "other register register":
                        tokens[2].mov_to_reg32(exe, regs, "gpr11")
                        exe.append(opcode(18) + regs["gpr11"] + tokens[4].bin + tokens[7].bin)
                    case "other ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[2].mov_to_reg32(exe, regs, "gpr12")
                        exe.append(opcode(19) + regs["gpr12"] + regs["gpr11"] + tokens[7].bin)

                    case "register other register":
                        exe.append(opcode(19) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "register register register":
                        exe.append(opcode(18) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "register ramloc register":
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(18) + tokens[2].bin + regs["gpr11"] + tokens[7].bin)
                    
                    case "ramloc other register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(19) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + tokens[7].bin)
                    case "ramloc register register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(18) + regs["gpr11"] + tokens[4].bin + tokens[7].bin)
                    case "ramloc ramloc register":
                        tokens[2].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr12")
                        exe.append(opcode(18) + regs["gpr11"] + regs["gpr12"] + tokens[7].bin)
                    
                    case "other other ramloc":
                        exe.append(opcode(2) + regs["gpr11"] + num_to_32b(tokens[2].val, find_base(tokens[2].val), sys, file, program, idx))
                        exe.append(opcode(19) + regs["gpr11"] + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other register ramloc":
                        tokens[2].mov_to_reg32(exe, regs, "gpr12")
                        exe.append(opcode(18) + regs["gpr12"] + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "other ramloc ramloc": # not done
                        tokens[4].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        tokens[2].mov_to_reg32(exe, regs, "gpr12")
                        exe.append(opcode(18) + regs["gpr12"] + regs["gpr11"] + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))

                    case "register other ramloc":
                        exe.append(opcode(19) + tokens[2].bin + num_to_32b(tokens[4].val, find_base(tokens[4].val), sys, file, program, idx) + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    case "register register ramloc":
                        exe.append(opcode(18) + tokens[2].bin + tokens[4].bin + regs["gpr11"])
                        if tokens[7].loc in regs.keys(): # accessing a ram location using a register
                            exe.append(opcode(8) + regs["gpr11"] + regs[tokens[7].loc])
                        else: # accessing using imm
                            exe.append(opcode(10) + regs["gpr11"] + num_to_32b(tokens[7].loc, find_base(tokens[7].loc), sys, file, program, idx))
                    
                    case _:
                        err(f"could not add data of type '{typeof(tokens[2])}' (with value of: '{tokens[2].val}') to type '{typeof(tokens[4])}' (with value of: '{tokens[4].val}')", sys, file, program, idx)
            case "or":
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 8 but found {len(tokens)}", sys, file, program, idx)
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
                if not typeof(tokens[7]) == "register":
                    err("Not a valid destination for result, must be a register", sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])}":
                    case "register register":
                        exe.append(opcode(40) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "register flag":
                        exe.append(opcode(41) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "flag flag":
                        exe.append(opcode(42) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "flag register":
                        err("Invalid type match, switch the opperands and it will work", sys, file, program, idx)
                    case _:
                        err("Invalid type match, valid combos are reg-reg, reg-flag, and flag-flag", sys, file, program, idx)
            case "and":
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 8 but found {len(tokens)}", sys, file, program, idx)
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
                if not typeof(tokens[7]) == "register":
                    err("Not a valid destination for result, must be a register", sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])}":
                    case "register register":
                        exe.append(opcode(43) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "register flag":
                        exe.append(opcode(44) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "flag flag":
                        exe.append(opcode(45) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "flag register":
                        err("Invalid type match, switch the opperands and it will work", sys, file, program, idx)
                    case _:
                        err("Invalid type match, valid combos are reg-reg, reg-flag, and flag-flag", sys, file, program, idx)
            case "xor":
                if len(tokens) != 8:
                    err(f"not enough tokens, expected 8 but found {len(tokens)}", sys, file, program, idx)
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
                if not typeof(tokens[7]) == "register":
                    err("Not a valid destination for result, must be a register", sys, file, program, idx)
                match f"{typeof(tokens[2])} {typeof(tokens[4])}":
                    case "register register":
                        exe.append(opcode(46) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "register flag":
                        exe.append(opcode(47) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "flag flag":
                        exe.append(opcode(48) + tokens[2].bin + tokens[4].bin + tokens[7].bin)
                    case "flag register":
                        err("Invalid type match, switch the opperands and it will work", sys, file, program, idx)
                    case _:
                        err("Invalid type match, valid combos are reg-reg, reg-flag, and flag-flag", sys, file, program, idx)
            case "not":
                if len(tokens) != 4:
                    err("not enough tokens", sys, file, program, idx)
                if typeof(tokens[2]) != "other" or tokens[2].val != ">":
                    err("there must be a move operator between the source and destination", sys, file, program, idx)
                if typeof(tokens[3]) != "register":
                    err("destination must be a register", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "register":
                        exe.append(opcode(49) + tokens[1].bin + tokens[3].bin)
                    case "flag":
                        exe.append(opcode(50) + tokens[1].bin + tokens[3].bin)
                    case _:
                        err("not a valid source location, must be a register or flag", sys, file, program, idx)
            case "ldstr":
                if len(tokens) != 2:
                    err("Unknown syntax found while loading a string into ram", sys, file, program, idx)
                if typeof(tokens[1]) != "string":
                    err("ldstr (load string) takes a string", sys, file, program, idx)
                exe.append(opcode(67) + regs["gpr11"]) # getramsize gpr11
                exe.append(opcode(69) + num_to_32b(str(tokens[1].len), 10, sys, file, program, idx)) # expandram {tokens[1].len}
                for idx, char in enumerate(tokens[1].val):
                    exe.append(opcode(9) + num_to_32b(str(ord(char)), 10, sys, file, program, idx) + regs["gpr11"]) # mov {ord(char)} > [gpr11]
                    exe.append(opcode(32) + regs["gpr11"]) # inc gpr11 (the point in the array we are writing to)
            case "cmd":
                if len(tokens) != 2:
                    err("Unknown syntax found while loading a string into ram", sys, file, program, idx)
                if typeof(tokens[1]) != "string":
                    err("ldstr (load string) takes a string", sys, file, program, idx)
                exe.append(opcode(82) + "".join([format(ord(i), "08b") for i in tokens[1].val])) # getramsize gpr11
            case "expram":
                if len(tokens) != 2:
                    err("Unknown syntax found while expanding ram", sys, file, program, idx)
                match typeof(tokens[1]):
                    case "other":
                        exe.append(opcode(69) + num_to_32b(tokens[1].val, find_base(tokens[1].val), sys, file, program, idx))
                    case "reg":
                        exe.append(opcode(68) + tokens[1].bin)
                    case "ramloc":
                        tokens[1].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(68) + regs["gpr11"])
                    case _:
                        err("expram only takes types other (int), reg, and ramloc", sys, file, program, idx)
            case "shl":
                if len(tokens) != 4:
                    err("Incorrect syntax", sys, file, program, idx)
                if not isLocation(tokens[1]):
                    err("The first arguement is both an input and the destination, so it must be a register or ramloc", sys, file, program, idx)
                if typeof(tokens[2]) != "other" or tokens[2].val != ",":
                    err("There must be a comma seperating the arguements", sys, file, program, idx)
                if typeof(tokens[3]) not in ("ramloc", "register", "other"):
                    err("2nd arguement: Type not supported for shifting", sys, file, program, idx)
                match f"{typeof(tokens[1])} {typeof(tokens[3])}":
                    case "register other": # shl gpr0, 5
                        exe.append(opcode(25) + tokens[1].bin + num_to_32b(tokens[3].val, find_base(tokens[3].val), sys, file, program, idx))
                    case "register register": # shl gpr0, gpr1
                        exe.append(opcode(24) + tokens[1].bin + tokens[3].bin)
                    case "register ramloc": # shl gpr0, [0]
                        tokens[3].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(24) + tokens[1].bin + regs["gpr11"])
                    case "ramloc other": # shl [0], 5
                        if tokens[1].loc in regs.keys(): # shl [gpr0], 5
                            tokens[3].mov_to_reg32(exe, regs, "gpr11")
                            exe.append(opcode(26) + regs[tokens[1].loc] + regs["gpr11"])
                        else: # shl [0], 5
                            tokens[3].mov_to_reg32(exe, regs, "gpr11")
                            exe.append(opcode(27) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs["gpr11"])
                    case "ramloc register": # shl [0], 5
                        if tokens[1].loc in regs.keys(): # shl [gpr0], gpr1
                            exe.append(opcode(26) + regs[tokens[1].loc] + tokens[3].bin)
                        else: # shl [0], gpr1
                            exe.append(opcode(27) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + tokens[3].bin)
                    case "ramloc ramloc":
                        if tokens[1].loc in regs.keys():
                            if tokens[3].loc in regs.keys(): # shl [gpr0], [gpr1]
                                exe.append(opcode(12) + regs[tokens[3].loc] + regs["gpr11"])
                                exe.append(opcode(26) + regs[tokens[1].loc] + regs["gpr11"])
                            else: # shl [gpr0], [0]
                                exe.append(opcode(13) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx) + regs["gpr11"])
                                exe.append(opcode(26) + regs[tokens[1].loc] + regs["gpr11"])
                        else: # shl [0], 
                            if tokens[3].loc in regs.keys(): # shl [0], [gpr1]
                                exe.append(opcode(12) + regs[tokens[3].loc] + regs["gpr11"])
                                exe.append(opcode(27) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs["gpr11"])
                            else: # shl [0], [1]
                                exe.append(opcode(13) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx) + regs["gpr11"])
                                exe.append(opcode(27) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs["gpr11"])
            case "shr":
                if len(tokens) != 4:
                    err("Incorrect syntax", sys, file, program, idx)
                if not isLocation(tokens[1]):
                    err("The first arguement is both an input and the destination, so it must be a register or ramloc", sys, file, program, idx)
                if typeof(tokens[2]) != "other" or tokens[2].val != ",":
                    err("There must be a comma seperating the arguements", sys, file, program, idx)
                if typeof(tokens[3]) not in ("ramloc", "register", "other"):
                    err("2nd arguement: Type not supported for shifting", sys, file, program, idx)
                match f"{typeof(tokens[1])} {typeof(tokens[3])}":
                    case "register other": # shl gpr0, 5
                        exe.append(opcode(29) + tokens[1].bin + num_to_32b(tokens[3].val, find_base(tokens[3].val), sys, file, program, idx))
                    case "register register": # shl gpr0, gpr1
                        exe.append(opcode(28) + tokens[1].bin + tokens[3].bin)
                    case "register ramloc": # shl gpr0, [0]
                        tokens[3].get_value(exe, regs, sys, file, program, idx, "gpr11")
                        exe.append(opcode(28) + tokens[1].bin + regs["gpr11"])
                    case "ramloc other": # shl [0], 5
                        if tokens[1].loc in regs.keys(): # shl [gpr0], 5
                            tokens[3].mov_to_reg32(exe, regs, "gpr11")
                            exe.append(opcode(30) + regs[tokens[1].loc] + regs["gpr11"])
                        else: # shl [0], 5
                            tokens[3].mov_to_reg32(exe, regs, "gpr11")
                            exe.append(opcode(31) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs["gpr11"])
                    case "ramloc register": # shl [0], 5
                        if tokens[1].loc in regs.keys(): # shl [gpr0], gpr1
                            exe.append(opcode(31) + regs[tokens[1].loc] + tokens[3].bin)
                        else: # shl [0], gpr1
                            exe.append(opcode(31) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + tokens[3].bin)
                    case "ramloc ramloc":
                        if tokens[1].loc in regs.keys():
                            if tokens[3].loc in regs.keys(): # shl [gpr0], [gpr1]
                                exe.append(opcode(12) + regs[tokens[3].loc] + regs["gpr11"])
                                exe.append(opcode(30) + regs[tokens[1].loc] + regs["gpr11"])
                            else: # shl [gpr0], [0]
                                exe.append(opcode(13) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx) + regs["gpr11"])
                                exe.append(opcode(30) + regs[tokens[1].loc] + regs["gpr11"])
                        else: # shl [0], 
                            if tokens[3].loc in regs.keys(): # shl [0], [gpr1]
                                exe.append(opcode(12) + regs[tokens[3].loc] + regs["gpr11"])
                                exe.append(opcode(31) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs["gpr11"])
                            else: # shl [0], [1]
                                exe.append(opcode(13) + num_to_32b(tokens[3].loc, find_base(tokens[3].loc), sys, file, program, idx) + regs["gpr11"])
                                exe.append(opcode(31) + num_to_32b(tokens[1].loc, find_base(tokens[1].loc), sys, file, program, idx) + regs["gpr11"])
            case ".":
                if len(tokens) != 3:
                    err("Unknown syntax found in label decleration", sys, file, program, idx)
                if typeof(tokens[2]) != "other":
                    err("Unknown syntax", sys, file, program, idx)
                if tokens[2].val != ":":
                    err("Unknown syntax", sys, file, program, idx)
                exe.append(opcode(72) + "".join([format(ord(char), "08b") for char in f".{tokens[1].val}\0"]))
            case "jmp" | "call" | "jine" | "jie" | "jils" | "jigt" | "jiover" | "jiundr":
                branchers = {"jmp":73, "call":73, "jine":78, "jie":77, "jils":75, "jigt":76, "jiover":79, "jiundr":80}
                if len(tokens) != 3:
                    err("Unknown syntax", sys, file, program, idx)
                if typeof(tokens[2]) != typeof(tokens[1]) != "other":
                    err("Unknown syntax", sys, file, program, idx)
                if tokens[1].val != ".":
                    err("Unrecognized label")
                exe.append(opcode(branchers[tokens[0].val]) + "".join([format(ord(char), "08b") for char in f".{tokens[2].val}\0"]))
            case "flush":
                if len(tokens) != 1:
                    err("Unknown syntax", sys, file, program, idx)
                exe.append(opcode(81))
            case "ret":
                if len(tokens) != 1:
                    err("Unknown token found", sys, file, program, idx)
                exe.append(opcode(74) + "00000011")
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
    