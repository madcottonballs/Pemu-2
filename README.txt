Pemu:
    Pemu is a simulated computer that compiles its recieved machine instructions to rust code for maximum speed.
    compilation flags:
        "--unstable":
            Increases speed of generated code, but will not throw an error if one occurs, 
            instead likely an internal error will occur and a bug search will be close to impossible.
        "--notimefeedback":
            Removes the counter that says how long the generated executable took to run, for user input it's suggested.
        "--nodeletewaste":
            Usually waste files like the generated Rust file and the pdb file are deleted, but with this setting they are not deleted.
            Can be used for determining the exact combination of code that produces the best Rust code.
        "--norun":
            Doesn't run the generated executable.
    Registers (there are 27 (00000000 - 00011010)):
        rpr (00000000):
            Stands for "register pointer ram", is auto-loaded with values such as the pointer to the first new ram location after a ram allocation.
        parr (00000001):
            Stands for "pointer to arguements in ram register" and it'll be used for, well, a pointer to the arguements in ram.
        car (00000010):
            Stands for "call address register", and is used in a branching instruction as the address of the destination insturction.
        rar (00000011):
            Stands for "return address register", and is used as the instruction after the last branch instruction and is loaded automatically.
        ltr0 (00000100):
            Stands for "ltr0" and hold values that rarely change or that aren't used for computation. Can be thought of as a variable.
        ltr1 (00000101):
            Stands for "ltr1" and hold values that rarely change or that aren't used for computation. Can be thought of as a variable.
        ltr2 (00000110):
            Stands for "ltr2" and hold values that rarely change or that aren't used for computation. Can be thought of as a variable.
        ltr3 (00000111):
            Stands for "ltr3" and hold values that rarely change or that aren't used for computation. Can be thought of as a variable.
        prvr (00001000):
            Pointer to Return Values in Ram, same as parr except for return values
        fr0 (00001001):
            Stands for "function register 0" and can be used as anything but usually compuation.
        fr1 (00001010):
            Stands for "function register 1" and can be used as anything but usually compuation.            
        fr2 (00001011):
            Stands for "function register 2" and can be used as anything but usually compuation.
        fr3 (00001100):
            Stands for "function register 3" and can be used as anything but usually compuation.
        fr4 (00001101):
            Stands for "function register 4" and can be used as anything but usually compuation.
        gpr0 (00001110):
            Stands for "general purpose register 0" and can be used as anything but usually compuation.
        gpr1 (00001111):
            Stands for "general purpose register 1" and can be used as anything but usually compuation.
        gpr2 (00010000):
            Stands for "general purpose register 2" and can be used as anything but usually compuation.
        gpr3 (0010001):
            Stands for "general purpose register 3" and can be used as anything but usually compuation.
        gpr4 (00010010):
            Stands for "general purpose register 4" and can be used as anything but usually compuation.            
        gpr5 (00010011):
            Stands for "general purpose register 5" and can be used as anything but usually compuation.
        gpr6 (00010100):
            Stands for "general purpose register 6" and can be used as anything but usually compuation.
        gpr7 (00010101):
            Stands for "general purpose register 7" and can be used as anything but usually compuation.
        gpr8 (00010110):
            Stands for "general purpose register 8" and can be used as anything but usually compuation.
        gpr9 (00010111):
            Stands for "general purpose register 9" and can be used as anything but usually compuation.
        gpr10 (00011000):
            Stands for "general purpose register 10" and can be used as anything but usually compuation.
        gpr11 (00011001):
            Stands for "general purpose register 11" and can be used as anything but usually compuation.
        gpr12 (00011010):
            Stands for "general purpose register 12" and can be used as anything but usually compuation.
    cpu flags:
        ls_flag (00000000):
            says that in the last compare instruction, the first arguement was less than the second
        gt_flag  (00000001):
            says that in the last compare instruction, the first arguement was greater than the second
        e_flag   (00000010):
            says that in the last compare instruction, the first arguement was equal to the second
        ne_flag  (00000011):
            says that in the last compare instruction, the first arguement was not equal to the second
        over_flag (00000100):
            says that in the Arithmatic instruction, the result overflowed
        undr_flag (00000101):
            says that in the last Arithmatic instruction, the result underflowed
    If there is an immediate, it's number of bits will be listed next to it.
    instructions:
        Exits:
            0  | exit_reg (reg)                          | Exits with the code in the register 
            1  | exit_imm (imm16)                        | Exits with the code of the immediate entered
        Data movement:         
            2  | ldi (reg) (imm32)                       | Loads an immediate into a register
            3  | mov (reg) (reg)                         | Moves the value in the second register to the first
            4  | mov_ram_reg_reg (reg) (reg)             | moves the value in ram specified by the first register to the ram location specified by the second register
            5  | mov_ram_reg_imm (reg) (imm32)           | moves the value in ram specified by the register to the ram location specified by the immediate
            6  | mov_ram_imm_reg (imm32) (reg)           | moves the value in ram specified by the immediate to the ram location specified by the register
            7  | mov_ram_imm_imm (imm32) (imm32)         | moves the value in ram specified by the first immediate to the ram location specified by the second immediate
            8  | write_ram_reg_reg (reg) (reg)           | writes the value in the first register to the ram location specified by the second register
            9  | write_ram_imm_reg (imm32) (reg)         | writes the immediate to the ram location specified by the register
            10 | write_ram_reg_imm (reg) (imm32)         | writes the value in the register to the ram location specified by the imm
            11 | write_ram_imm_imm (imm32) (imm32)       | writes the first immediate to the ram location specified by the second immediates
            12 | load_ram_reg_reg (reg) (reg)            | loads the value in the ram location specified by the first register into the second register
            13 | load_ram_imm_reg (imm32) (reg)          | loads the value in the ram location specified by the immediate into the register
            14 | load_flag_to_reg (flag) (reg)           | moves the value of the flag to the register
            15 | load_flag_to_ram (flag) (reg)           | moves the value of the flag to the ram location specified by the register
        AU:   
            16 | add_reg (reg) (reg) (reg)               | adds the values in the first two registers, saves it in the final register
            17 | add_imm (reg) (imm) (reg)               | adds the immediate and the first register, saves it in the final register
            18 | sub_reg (reg) (reg) (reg)               | subtracts the value in the second register from the first, saves it in the final register
            19 | sub_imm (reg) (imm) (reg)               | subtracts the immediate from the first register, saves it in the final register
            20 | mult_reg (reg) (reg) (reg)              | multiplies the values in the first two registers, saves it in the final register
            21 | mult_imm (reg) (imm) (reg)              | multiplies the immediate and the first register, saves it in the final register
            22 | div_reg (reg) (reg) (reg)               | divides the values in the first two registers, saves it in the final register
            23 | div_imm (reg) (imm) (reg)               | divides the immediate and the first register, saves it in the final register
            24 | shl_reg_reg (reg) (reg)                 | shifts the bits in the first register over to the left by the value in the second register
            25 | shl_reg_imm (reg) (imm)                 | shifts the bits in the register over to the left by the immediate
            26 | shl_ram_reg (reg) (reg)                 | shifts the bits in the ram location described by the first register over to the left by the value in the second register
            27 | shl_ram_imm (reg) (imm)                 | shifts the bits in the ram location described by the register over to the left by the immediate
            28 | shr_reg_reg (reg) (reg)                 | shifts the bits in the first register over to the right by the value in the second register
            29 | shr_reg_imm (reg) (imm)                 | shifts the bits in the register over to the right by the immediate
            30 | shr_ram_reg (reg) (reg)                 | shifts the bits in the ram location described by the right register over to the left by the value in the second register
            31 | shr_ram_imm (reg) (imm)                 | shifts the bits in the ram location described by the register over to the right by the immediate
            32 | inc_reg (reg)                           | increments the register by 1
            33 | inc_ram_reg (reg)                       | increments the ram location described by the register by 1
            34 | inc_ram_imm (imm)                       | increments the ram location described by the immediate by 1
            35 | dec_reg (reg)                           | decrements the register by 1
            36 | dec_ram_reg (reg)                       | decrements the ram location described by the register by 1
            37 | dec_ram_imm (imm)                       | decrements the ram location described by the immediate by 1
        LU:
            38 | cmp_reg_imm (reg) (imm)                 | sets the cpu flags to how the register relates to the immediate (example: if the register contains 5 and the immediate is 8, lst_flag is set to true) 
            39 | cmp_reg_reg (reg) (reg)                 | sets the cpu flags to how the first register relates to the second register (example: if the first register contains 5 and the second register contains 8, lst_flag is set to true) 
            40 | or_reg_reg (reg) (reg) (reg)            | sets the final register to if the first register or the second register is 1
            41 | or_reg_flag (reg) (flag) (reg)          | sets the final register to if the first register or the flag is 1
            42 | or_flag_flag (flag) (flag) (reg)        | sets the register to if the first flag or the second flag is 1
            43 | and_reg_reg (reg) (reg) (reg)           | sets the final register to if the first register and the second register is 1
            44 | and_reg_flag (flag) (flag) (reg)        | sets the register to if the first flag and the second flag is 1
            45 | and_flag_flag (reg) (flag) (reg)        | sets the final register to if the first register and the flag is 1
            46 | xor_reg_reg (reg) (reg) (reg)           | sets the final register to 1 if the first register is not equal to the second register
            47 | xor_reg_flag (reg) (flag) (reg)         | sets the final register to 1 if the first register is not equal to the flag
            48 | xor_flag_flag (flag) (flag) (reg)       | sets the register to 1 if the first flag is not equal to the second flag
            49 | not_reg (reg) (reg)                     | sets the final register to 1 if the first register is 0 and 0 if it's 1
            50 | not_flag (flag) (reg)                   | sets the register to 1 if the flag is 0 and 0 if it's 1
        CLI:
            51 | print_integer_reg (reg)                 | prints the value in the register
            52 | print_integer_imm (imm)                 | prints the immediate
            53 | print_integer_ram_reg (reg)             | prints the value in the ram location specified by the register
            54 | print_integer_ram_imm (imm)             | prints the value in the ram location specified by the immediate
            55 | print_char_reg (reg)                    | prints the value in the register as a charactor according to its ascii index
            56 | print_char_imm (imm)                    | prints the immediate as a charactor according to its ascii index
            
            57 | print_str (string)                      | the bytes following the opcode is interpreted as charactor data, null-terminated
            58 | print_char_ram_reg (reg)                | prints the value in the ram location specified by the register as a charactor according to its ascii index
            59 | print_char_ram_imm (imm)                | prints the value in the ram location specified by the immediate as a charactor according to its ascii index
            60 | input                                   | pauses script execution and gets a string of charactors from the terminal, the string is turned into a array of their ascii indexes and appened to the end of ram. Pointer to first location saved in rpr
            61 | run_command_reg (reg) (reg)             | Interprets the data in ram between the two registers as a string and runs that string in powershell (using .., so exclusive on the right side)
            62 | run_command_imm (imm) (imm)             | Interprets the data in ram between the two immediates as a string and runs that string in powershell (using .., so exclusive on the right side)
        File I/O:
            63 | open_file_into_buf (reg) (reg) (reg)    | opens the file specified by the string between the first two registers in ram into the filebuf, filebuf index placed in final reg
            64 | read_from_file_buf (reg) (reg) (reg)    | the first register is the index in the filebuf of the file, the second register is the index of the byte you want to read from the file, and the last register is the destination
            65 | get_size_of_file (reg) (reg)            | the first register is the index of the file in the filebuf and the last register is the destination of the size
            66 | write_reg_to_file_buf (reg) (reg) (reg) | the first register is the file index in the filebuf, the second register is the index in the buffer
        Misc:
            67 | get_ram_size (reg)                      | the size of the ram is put in the register
            68 | expand_ram_reg (reg)                    | ram is expanded by the value in the register, also a pointer to the first of the new locations is saved in rpr
            69 | expand_ram_imm (imm32)                  | ram is expanded by the immediate, also a pointer to the first of the new locations is saved in rpr
            70 | set_stack_size (imm64)                  | sets the stack size to whatever value is entered, advisable to keep it low
            71 | import_library (string)                 | loads the codebase of the pemu file described by the string directly into that spot, used for libaries
        Branching:
            72 | jmp_reg (reg)                           | jumps to the instruction index in the register, current instruction index loaded into rar
            73 | jmp_imm (imm32)                         | jumps to the immediate as a instruction index, current instruction index loaded into rar
            74 | jils_reg (reg)                          | jumps to the instruction index in the register if ls_flag is 1, current instruction index loaded into rar
            75 | jils_imm (imm32)                        | jumps to the immediate as a instruction index if ls_flag is 1, current instruction index loaded into rar
            76 | jigt_reg (reg)                          | jumps to the instruction index in the register if gt_flag is 1, current instruction index loaded into rar
            77 | jigt_imm (imm32)                        | jumps to the immediate as a instruction index if gt_flag is 1, current instruction index loaded into rar
            78 | jie_reg (reg)                           | jumps to the instruction index in the register if e_flag is 1, current instruction index loaded into rar
            79 | jie_imm (imm32)                         | jumps to the immediate as a instruction index if e_flag is 1, current instruction index loaded into rar
            80 | jine_reg (reg)                          | jumps to the instruction index in the register if ne_flag is 1, current instruction index loaded into rar
            81 | jine_imm (imm32)                        | jumps to the immediate as a instruction index if ne_flag is 1, current instruction index loaded into rar
            82 | jiover_reg (reg)                        | jumps to the instruction index in the register if over_flag is 1, current instruction index loaded into rar
            83 | jiover_imm (imm32)                      | jumps to the immediate as a instruction index if over_flag is 1, current instruction index loaded into rar
            84 | jiundr_reg (reg)                        | jumps to the instruction index in the register if undr_flag is 1, current instruction index loaded into rar
            85 | jiundr_imm (imm32)                      | jumps to the immediate as a instruction index if undr_flag is 1, current instruction index loaded into rar
            86 | assignlabel (string)                    | assigns the following line of code the null-terminated-string, for easy jumping
            87 | jmp_lbl (string)                        | jumps to the jmp_label, current instruction index loaded into rar
            88 | jils_lbl (string)                       | jumps to the label if the ls_flag is 1, current instruction index loaded into rar
            89 | jigt_lbl (string)                       | jumps to the label if the gt_flag is 1, current instruction index loaded into rar
            90 | jie_lbl (string)                        | jumps to the label if the e_flag is 1, current instruction index loaded into rar
            91 | jine_lbl (string)                       | jumps to the label if the ne_flag is 1, current instruction index loaded into rar
            92 | jiover_lbl (string)                     | jumps to the label if the over_flag is 1, current instruction index loaded into rar
            93 | jiundr_lbl (string)                     | jumps to the label if the undr_flag is 1, current instruction index loaded into rar
        Randomly added after I realized they would be useful:
            94 | flush                                   | flushes all data waiting in the terminal buffer, immediantly prints all awaiting data

Plow:
    In plow registers gpr11 and gpr12 are reserved.
    instructions:
        exit {ramloc | reg}:
            immediantly terminates program execution with the exit code contained in the register or ramloc
        pri {ramloc | reg | imm32}:
            prints the integer contained in the ramloc or reg or the imm32
        prc {ramloc | reg | char | imm32}:
            interprets the integer contained in the locations as a charactor
        prs {string}:
            prints the constant string, must be null terminated
        mov {ramloc | reg | imm32 | char} > {ramloc | reg}:
            moves data into the destination location (the arguement after the move operator)
        add ({ramloc | reg | imm32}, {ramloc | reg | imm32}) > {ramloc | reg}:
            adds the 2 arguements in parenthesis and saves it in the destination arguement (the final arguement)
        sub ({ramloc | reg | imm32}, {ramloc | reg | imm32}) > {ramloc | reg}:
            subtracts the 2nd arguement from the first, saves it in the destination arguement (the final arguement)
        mult ({ramloc | reg | imm32}, {ramloc | reg | imm32}) > {ramloc | reg}:
            multiplies the 2 arguements in parenthesis and saves it in the destination arguement (the final arguement)
        div ({ramloc | reg | imm32}, {ramloc | reg | imm32}) > {ramloc | reg}:
            divides arguement 1 by arguement 2 and saves it in the destination arguement (the final arguement)
        input {string}:
            prints the string as a prompt and returns the address of the new ram locations containing the raw string data in rpr