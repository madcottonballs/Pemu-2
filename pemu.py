"""output file parameter is the name without the extension, so if the output file planned was a.exe, pass in 'a'"""

def read_binary_file(path: str) -> list[int]:
    with open(path, "rb") as file:
        return list(file.read())
    
def write_to_rs_file(output_file: str, rs: list[str]) -> None:
    with open(f"{output_file}.rs", "w") as file:
        file.write("\n".join(rs))

def next_instr(byte_index: int, num_of_operands: int) -> None:
    byte_index += num_of_operands + 1

def error(program: list[int], byte_index: int, details: str) -> None:
    print(f"PEMU: compilation error at byte {byte_index}: {details}")
    print(f"\t{program[byte_index]}")
    import sys
    sys.exit()

def bounds_check(program: list[int], byte_index: int, num_of_operands: int) -> None:
    if byte_index + num_of_operands > len(program):
        error(program, byte_index, "Invalid program, instruction cut off in middle")

def generate_start_of_instruction(instructions: int, rs: list[str]) -> None:
    rs.append(f"#[inline]\nfn instruction_{instructions}(registers: &mut [u32; 27], ram: &mut Vec<u32>, filebufs: &mut Vec<Vec<u8>>, flags: &mut [bool; 6]) " + r"{")

def generate_end_of_instruction(program: list[int], byte_index: int, number_of_operands: int, instructions: int, rs: list[str]) -> None:
    if byte_index + number_of_operands == len(program) - 1:
        rs.append("}")
    else:
        rs.append(f"\tinstruction_{instructions + 1}(registers, ram, filebufs, flags);")
        rs.append("}")

def make_16_bit(first: int, second: int) -> int:
    return int("0b" + format(first, "08b") + format(second, "08b"), base=0)

def make_24_bit(first: int, second: int, third: int) -> int:
    return int("0b" + format(first, "08b") + format(second, "08b") + format(third, "08b"), base=0)

def make_32_bit(first: int, second: int, third: int, fourth: int) -> int:
    return int("0b" + format(first, "08b") + format(second, "08b") + format(third, "08b") + format(fourth, "08b"), base=0)

def make_64_bit(first: int, second: int, third: int, fourth: int, fifth: int, sixth: int, seventh: int, eighth: int) -> int:
    return int("0b" + format(first, "08b") + format(second, "08b") + format(third, "08b") + format(fourth, "08b") +
               format(fifth, "08b") + format(sixth, "08b") + format(seventh, "08b") + format(eighth, "08b")
               , base=0)

class label:
    def __init__(self, line: int, substitution: list[int]) -> None:
        self.line = line
        self.sub = substitution


def compile_stable(program, path, show_time, os, delete_waste, unstable, run, output_file="a"):
    path_no_extension = ".".join(path.split(".")[:-1])
    print(f"PEMU: {path_no_extension}.pemu -> {output_file}.rs ", end="")
    import time
    compilation_start_time = time.time()
    rs: list[str] = []
    if len(program) == 0: # if you enter an empty binary file
        rs.append("use std::time::Instant;")
        rs.append("fn main() {println!(\"Code executed in {:.2?}\", Instant::now() - Instant::now())}")
        write_to_rs_file(path_no_extension, rs)
        return
    rs.append("#![recursion_limit=\"512\"]\n#![allow(warnings)]\nuse std::thread;")
    rs.append("fn main() {\n\tlet stack_size =")
    rs.append("25000000")
    rs.append(";\n\tlet builder = thread::Builder::new().stack_size(stack_size);\n\tlet handle = builder.spawn(|| {")
    if show_time:
        rs.append("\tlet stime = Instant::now();\n\tlet mut registers: [u32; 27] = [0 as u32; 27];\n\tlet mut ram: Vec<u32> = Vec::new();\n\tlet mut filebufs: Vec<Vec<u8>> = Vec::new();\n\tlet mut flags: [bool; 6] = [false; 6];\n\tinstruction_1(&mut registers, &mut ram, &mut filebufs, &mut flags);\n\tlet end_time = Instant::now();\n\tprintln!(\"Code executed in {:.2?}\", end_time - stime);")
    else:
        rs.append("\tlet mut registers: [u32; 27] = [0 as u32; 27];\n\tlet mut ram: Vec<u32> = Vec::new();\n\tlet mut filebufs: Vec<Vec<u8>> = Vec::new();\n\tlet mut flags: [bool; 6] = [false; 6];\n\tinstruction_1(&mut registers, &mut ram, &mut filebufs, &mut flags);")
    rs.append("\t}).expect(\"Failed to spawn\");\n\thandle.join().expect(\"Failed to join thread\");\n}")

    instructions = 0
    num_of_registers = 27
    num_of_flags = 6
    using_commands: bool = False
    using_path_buf: bool = False
    using_exit: bool = False
    using_jump: bool = False
    using_io: bool = False
    using_file_io: bool = False
    byte_index = 0
    labels = {}
    while byte_index < len(program):
        instructions += 1
        opcode = program[byte_index]
        match opcode:
            case 0: # exit reg
                using_exit = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\texit(registers[{program[byte_index + 1]}] as i32);")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2 
            case 1: # exit imm
                using_exit = True
                bounds_check(program, byte_index, 2)
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\texit({make_16_bit(program[byte_index + 1], program[byte_index + 2])});")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 2: # ldi
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")      
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 1]}] = {make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])};")
                generate_end_of_instruction(program, byte_index, 5, instructions, rs)
                byte_index += 6
            case 3: # mov
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 2]}] = registers[{program[byte_index + 1]}];")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 4: # mov_ram_reg_reg
                using_exit = True                
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif registers[{program[byte_index + 1]}] as usize >= ram.len() || registers[{program[byte_index + 2]}] as usize >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {"f"\tram[registers[{program[byte_index + 2]}] as usize] = ram[registers[{program[byte_index + 1]}] as usize];" + r"}")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 5: # mov_ram_reg_imm
                using_exit = True
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif {imm} >= ram.len() || registers[{program[byte_index + 5]}] as usize >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"ram[{imm}] = ram[registers[{program[byte_index + 1]}] as usize];" + r"}")
                generate_end_of_instruction(program, byte_index, 5, instructions, rs)
                byte_index += 6
            case 6: # mov_ram_imm_reg
                using_exit = True
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 5] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 5]} not valid")
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                rs.append(f"\tif {imm} >= ram.len() || registers[{program[byte_index + 1]}] as usize >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {")
                rs.append(f"\t\tram[registers[{program[byte_index + 5]}] as usize] = ram[{imm}];" + r"}")
                generate_end_of_instruction(program, byte_index, 5, instructions, rs)
                byte_index += 6
            case 7: # mov_ram_imm_imm
                using_exit = True
                bounds_check(program, byte_index, 8)
                if not program[byte_index + 5] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 5]} not valid")
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                imm2 = make_32_bit(program[byte_index + 5], program[byte_index + 6], program[byte_index + 7], program[byte_index + 8])
                rs.append(f"\tif {imm} >= ram.len() || {imm2} >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"ram[{imm2}] = ram[{imm2}];" + r"}")
                generate_end_of_instruction(program, byte_index, 8, instructions, rs)
                byte_index += 9
            case 8: # write_ram_reg_reg
                using_exit = True                
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif registers[{program[byte_index + 2]}] as usize >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"ram[registers[{program[byte_index + 2]}] as usize] = registers[{program[byte_index + 1]}];" + r"}")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 9: # write_ram_imm_reg
                using_exit = True                
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 5] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 5]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                
                rs.append(f"\tif registers[{program[byte_index + 5]}] as usize >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"ram[registers[{program[byte_index + 5]}] as usize] = {imm};" + r"}")
                generate_end_of_instruction(program, byte_index, 5, instructions, rs)
                byte_index += 6
            case 10: # write_ram_reg_imm
                using_exit = True                
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                
                rs.append(f"\tif {imm} >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"ram[{imm}] = registers[{program[byte_index + 1]}];" + r"}")
                generate_end_of_instruction(program, byte_index, 5, instructions, rs)
                byte_index += 6
            case 11: # write_ram_imm_imm
                using_exit = True                
                bounds_check(program, byte_index, 8)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                
                imm2 = make_32_bit(program[byte_index + 5], program[byte_index + 6], program[byte_index + 7], program[byte_index + 8])                
                rs.append(f"\tif {imm2} >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"ram[{imm2}] = {imm};" + r"}")
                generate_end_of_instruction(program, byte_index, 8, instructions, rs)
                byte_index += 9
            case 12: # load_ram_reg_reg
                using_exit = True
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif registers[{program[byte_index + 1]}] as usize >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"registers[{program[byte_index + 2]}] = ram[registers[{program[byte_index + 1]}] as usize];" + r"}")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 13: # load_ram_imm_reg
                using_exit = True                
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 5] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 5]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                
                rs.append(f"\tif {imm} >= ram.len()" + "{println!(\"entered an invalid ram address\"); exit(1);} else {" + f"registers[{program[byte_index + 5]}] = ram[{imm}];" + r"}")
                generate_end_of_instruction(program, byte_index, 5, instructions, rs)
                byte_index += 6
            case 14: # load_flag_to_reg
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 1]} not valid")      
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")      
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 2]}] = flags[{program[byte_index + 1]}] as u32;")
                generate_end_of_instruction(program, byte_index, 5, instructions, rs)
                byte_index += 3
            case 15: # load_flag_to_ram
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 1]} not valid")      
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")      
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tram[registers[{program[byte_index + 2]}] as usize] = flags[{program[byte_index + 1]}] as u32;")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 16: # add_reg
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = (registers[{program[byte_index + 1]}]).wrapping_add(registers[{program[byte_index + 2]}]);")
                rs.append(f"\tflags[4] = (registers[{program[byte_index + 1]}]).checked_add(registers[{program[byte_index + 2]}]).is_none();")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 17: # add_imm
                bounds_check(program, byte_index, 6)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 6] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 6]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                                
                rs.append(f"\tregisters[{program[byte_index + 6]}] = (registers[{program[byte_index + 1]}]).wrapping_add({imm});")
                rs.append(f"\tflags[4] = (registers[{program[byte_index + 1]}]).checked_add({imm}).is_none();")                
                generate_end_of_instruction(program, byte_index, 6, instructions, rs)
                byte_index += 7
            case 18: # sub_reg
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = (registers[{program[byte_index + 1]}]).wrapping_sub(registers[{program[byte_index + 2]}]);")
                rs.append(f"\tflags[5] = registers[{program[byte_index + 1]}] < registers[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 19: # sub_imm
                bounds_check(program, byte_index, 6)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 6] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 6]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                                
                rs.append(f"\tregisters[{program[byte_index + 6]}] = (registers[{program[byte_index + 1]}]).wrapping_sub({imm});")
                rs.append(f"\tflags[5] = registers[{program[byte_index + 1]}] < {imm};")                
                generate_end_of_instruction(program, byte_index, 6, instructions, rs)
                byte_index += 7
            case 20: # mult_reg
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = (registers[{program[byte_index + 1]}]).wrapping_mul(registers[{program[byte_index + 2]}]);")
                rs.append(f"\tflags[4] = (registers[{program[byte_index + 1]}]).checked_mul(registers[{program[byte_index + 2]}]).is_none();")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 21: # mult_imm
                bounds_check(program, byte_index, 6)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 6] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 6]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                                
                rs.append(f"\tregisters[{program[byte_index + 6]}] = (registers[{program[byte_index + 1]}]).wrapping_mul({imm});")
                rs.append(f"\tflags[4] = (registers[{program[byte_index + 1]}]).checked_mul({imm}).is_none();")                
                generate_end_of_instruction(program, byte_index, 6, instructions, rs)
                byte_index += 7
            case 22: # div_reg
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = registers[{program[byte_index + 1]}] / registers[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 23: # div_imm
                bounds_check(program, byte_index, 6)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 6] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 6]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                                
                rs.append(f"\tregisters[{program[byte_index + 6]}] = registers[{program[byte_index + 1]}] / {imm};")
                generate_end_of_instruction(program, byte_index, 6, instructions, rs)
                byte_index += 7
            case 24: # shl_reg_reg
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 1]}] = registers[{program[byte_index + 1]}] << registers[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 25: # shl_reg_imm
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                                
                rs.append(f"\tregisters[{program[byte_index + 1]}] = registers[{program[byte_index + 1]}] << {imm};")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 6
            case 26: # shl_ram_reg
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tram[registers[{program[byte_index + 1]}] as usize] = ram[registers[{program[byte_index + 1]}] as usize] << registers[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 27: # shl_ram_imm
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                                
                rs.append(f"\tram[registers[{program[byte_index + 1]}] as usize] = ram[registers[{program[byte_index + 1]}] as usize] << {imm};")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 6
            case 28: # shr_reg_reg
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 1]}] = registers[{program[byte_index + 1]}] >> registers[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 29: # shr_reg_imm
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                                
                rs.append(f"\tregisters[{program[byte_index + 1]}] = registers[{program[byte_index + 1]}] >> {imm};")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 6
            case 30: # shr_ram_reg
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tram[registers[{program[byte_index + 1]}] as usize] = ram[registers[{program[byte_index + 1]}] as usize] >> registers[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 31: # shr_ram_imm
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                             
                rs.append(f"\tram[registers[{program[byte_index + 1]}] as usize] = ram[registers[{program[byte_index + 1]}] as usize] >> {imm};")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 6
            case 32: # inc_reg 
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 1]}] += 1;")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 33: # inc_ram_reg 
                using_exit = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif registers[{program[byte_index + 1]}] as usize < ram.len()" "{ram[registers[" + f"{program[byte_index + 1]}] as usize] += 1;" + "} else {println!(\"Ram does not extend that far\"); exit(1);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 34: # inc_ram_imm 
                using_exit = True
                bounds_check(program, byte_index, 4)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                             
                rs.append(f"\tif {imm} < ram.len()" "{ram[" + f"{imm}] += 1;" + "} else {println!(\"Ram does not extend that far\"); exit(1);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 5
            case 35: # dec_reg 
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 1]}] -= 1;")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 36: # dec_ram_reg 
                using_exit = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif registers[{program[byte_index + 1]}] as usize < ram.len()" "{ram[registers[" + f"{program[byte_index + 1]}] as usize] -= 1;" + "} else {println!(\"Ram does not extend that far\"); exit(1);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 37: # dec_ram_imm 
                using_exit = True
                bounds_check(program, byte_index, 4)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                             
                rs.append(f"\tif {imm} < ram.len()" "{ram[" + f"{imm}] -= 1;" + "} else {println!(\"Ram does not extend that far\"); exit(1);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 5
            case 38: # cmp_reg_imm
                bounds_check(program, byte_index, 5)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                imm = make_32_bit(program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5])                             
                generate_start_of_instruction(instructions, rs)
                rs.append(f"flags[0] = registers[{program[byte_index + 1]}] < {imm};")
                rs.append(f"flags[1] = registers[{program[byte_index + 1]}] > {imm};")
                rs.append(f"flags[2] = registers[{program[byte_index + 1]}] == {imm};")
                rs.append(f"flags[3] = !flags[2];")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 6
            case 39: # cmp_reg_reg
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"flags[0] = registers[{program[byte_index + 1]}] < registers[{program[byte_index + 2]}];")
                rs.append(f"flags[1] = registers[{program[byte_index + 1]}] > registers[{program[byte_index + 2]}];")
                rs.append(f"flags[2] = registers[{program[byte_index + 1]}] == registers[{program[byte_index + 2]}];")
                rs.append(f"flags[3] = !flags[2];")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 40: # or_reg_reg
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = registers[{program[byte_index + 1]}] == 1 || registers[{program[byte_index + 2]}] == 1;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 41: # or_reg_flag
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = registers[{program[byte_index + 1]}] == 1 || flags[{program[byte_index + 2]}] == 1;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 42: # or_flag_flag
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = flags[{program[byte_index + 1]}] == 1 || flags[{program[byte_index + 2]}] == 1;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 43: # and_reg_reg
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = registers[{program[byte_index + 1]}] == 1 && registers[{program[byte_index + 2]}] == 1;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 44: # and_reg_flag
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = registers[{program[byte_index + 1]}] == 1 && flags[{program[byte_index + 2]}] == 1;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 45: # and_flag_flag
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = flags[{program[byte_index + 1]}] == 1 && flags[{program[byte_index + 2]}] == 1;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 46: # xor_reg_reg
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = registers[{program[byte_index + 1]}] != registers[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 47: # xor_reg_flag
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = registers[{program[byte_index + 1]}] != flags[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 48: # xor_flag_flag
                bounds_check(program, byte_index, 3)
                if not program[byte_index + 1] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 2]} not valid")                
                if not program[byte_index + 3] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 3]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = flags[{program[byte_index + 1]}] != flags[{program[byte_index + 2]}];")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            case 49: # not_reg_reg
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 2]}] = (registers[{program[byte_index + 1]}] == 0) as u32;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 3
            case 50: # not_flag
                bounds_check(program, byte_index, 2)
                if not program[byte_index + 1] < num_of_flags:
                    error(program, byte_index, f"Flag idx {program[byte_index + 1]} not valid")                
                if not program[byte_index + 2] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 2]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 3]}] = (!flags[{program[byte_index + 2]}]) as u32;")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 3
            case 51: # print_integer_reg
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tprint!(\"{"{" + "}"}\", registers[{program[byte_index + 1]}]);")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 52: # print_integer_imm
                bounds_check(program, byte_index, 4)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                             
                rs.append(f"\tprint!(\"{imm}\");")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 53: # print_integer_ram_reg
                using_exit = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif registers[{program[byte_index + 1]}] < ram.len() " + "{")
                rs.append(f"\t\tprint!(\"{"{" + "}"}\", ram[registers[{program[byte_index + 1]}] as usize]);")
                rs.append("\t} else {")
                rs.append("\t\tprintln!(\"during a print integer from ram instruction, you entered a index larger than ram\");")
                rs.append("\t}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 54: # print_integer_ram_imm
                bounds_check(program, byte_index, 4)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                             
                rs.append(f"\tif {imm} < ram.len() " + "{")
                rs.append(f"\t\tprint!(\"{"{" + "}"}\", ram[{imm}]);")
                rs.append("\t} else {")
                rs.append("\t\tprintln!(\"during a print integer from ram instruction, you entered a index larger than ram\");")
                rs.append("\t}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5            
            case 55: # print_char_reg
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tprint!(\"{"{" + "}"}\", char::from_u32(registers[{program[byte_index + 1]}]).expect(\"PEMU RUNTIME ERR: err at byte {byte_index}: could not convert the value in the register to a charactor\"));")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 56: # print_char_imm
                bounds_check(program, byte_index, 4)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                             
                rs.append(f"\tprint!(\"{chr(imm)}\");")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 57: # print_str
                try:
                    end = program.index(0, byte_index + 1)
                except:
                    error(program, byte_index, "end of string not found")
                generate_start_of_instruction(instructions, rs)
                temp = "".join([chr(v) for v in program[byte_index + 1:end]])
                rs.append(f"\tprint!(\"{temp}\");")
                generate_end_of_instruction(program, byte_index, end - byte_index, instructions, rs)
                byte_index += end - byte_index + 1
            case 58: # print_char_ram_reg
                using_exit = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif registers[{program[byte_index + 1]}] < ram.len() " + "{")
                rs.append(f"\t\tprint!(\"{"{" + "}"}\", ram[registers[{program[byte_index + 1]}] as usize] as char);")
                rs.append("\t} else {")
                rs.append("\t\tprintln!(\"during a print integer from ram instruction, you entered a index larger than ram\");")
                rs.append("\t}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 59: # print_char_ram_imm
                bounds_check(program, byte_index, 4)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                             
                rs.append(f"\tif {imm} < ram.len() " + "{")
                rs.append(f"\t\tprint!(\"{"{" + "}"}\", ram[{imm}] as char);")
                rs.append("\t} else {")
                rs.append("\t\tprintln!(\"during a print integer from ram instruction, you entered a index larger than ram\");")
                rs.append("\t}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5            
            case 60: # input
                using_io = True
                generate_start_of_instruction(instructions, rs)
                rs.append('\tregisters[0] = ram.len() as u32;')
                rs.append("\tio::stdout().flush().expect(\"failed to flush\");")
                rs.append("\tlet mut input = String::new();")
                rs.append("\tio::stdin().read_line(&mut input).expect(\"Failed to read line\");")
                rs.append("\tinput = input.trim().to_string();")
                rs.append("\tram.resize(ram.len() + input.len(), 0);")
                rs.append("\tfor (i, v) in input.chars().enumerate() {")
                rs.append("\t\tram[registers[0] as usize + i] = v as u32;")
                rs.append("\t}")
                generate_end_of_instruction(program, byte_index, 0, instructions, rs)
                byte_index += 1
            case 61: # run_command_reg
                using_commands = True
                using_exit = True
                bounds_check(program, byte_index, 2)                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif !(registers[{program[byte_index + 1]}] < registers[{program[byte_index + 2]}]) " + "{")
                rs.append("\t\tprintln!(\"value in the register described by the first opperand cannot be >= to the value in the register described by the second opperand\");")
                rs.append("\texit(1);")
                rs.append("\t}")
                rs.append(f"\tif !((registers[{program[byte_index + 2]}] as usize) < _ram.len()) " + "{")
                rs.append("\t\tprintln!(\"value in the register described by the second opperand is larger than the size of ram\")")
                rs.append("\t}")
                rs.append(f"\tlet described: String = ram[(registers[{program[byte_index + 1]}] as usize)..(registers[{program[byte_index + 2]}] as usize)].iter().map(|&u| u as char).collect();")
                rs.append("\tif !(file_exists(&described)) {")
                rs.append("\t\tprintln!(\"File '{}' does not exist\", described);")
                rs.append("\t\texit(1);")
                rs.append("\t}")
                rs.append("\tlet _ = execute_cmd_command(&format!(\".\\{}\", described));")
                generate_end_of_instruction(program, byte_index, 2, instructions, rs)
                byte_index += 3
            case 62: # run_command_imm
                using_commands = True
                using_exit = True
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                imm2 = make_32_bit(program[byte_index + 5], program[byte_index + 6], program[byte_index + 7], program[byte_index + 8])
                bounds_check(program, byte_index, 8)
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif {imm} >= {imm2} " + "{")
                rs.append("\t\tprintln!(\"value in the register described by the first opperand cannot be >= to the value in the register described by the second opperand\");")
                rs.append("\texit(1);")
                rs.append("\t}")
                rs.append(f"\tif {imm2} >= _ram.len() " + "{")
                rs.append("\t\tprintln!(\"value in the register described by the second opperand is larger than the size of ram\")")
                rs.append("\t}")
                rs.append(f"\tlet described: String = ram[{imm}..{imm2}].iter().map(|&u| u as char).collect();")
                rs.append("\tif !(file_exists(&described)) {")
                rs.append("\t\tprintln!(\"File '{}' does not exist\", described);")
                rs.append("\t\texit(1);")
                rs.append("\t}")
                rs.append("\tlet _ = execute_cmd_command(&format!(\".\\{}\", described));")
                generate_end_of_instruction(program, byte_index, 8, instructions, rs)
                byte_index += 9
            case 63: # read_file_into_buf
                using_commands = True
                using_exit = True
                bounds_check(program, byte_index, 3)                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tif !(registers[{program[byte_index + 1]}] < registers[{program[byte_index + 2]}]) " + "{")
                rs.append("\t\tprintln!(\"value in the register described by the first opperand cannot be >= to the value in the register described by the second opperand\");")
                rs.append("\texit(1);")
                rs.append("\t}")
                rs.append(f"\tif !((registers[{program[byte_index + 2]}] as usize) < _ram.len()) " + "{")
                rs.append("\t\tprintln!(\"value in the register described by the second opperand is larger than the size of ram\")")
                rs.append("\t}")
                rs.append(f"\tlet described: String = ram[(registers[{program[byte_index + 1]}] as usize)..(registers[{program[byte_index + 2]}] as usize)].iter().map(|&u| u as char).collect();")
                rs.append("\tif !(file_exists(&described)) {")
                rs.append("\t\tprintln!(\"File '{}' does not exist\", described);")
                rs.append("\t\texit(1);")
                rs.append("\t}")
                rs.append(f"\tregisters[{program[byte_index + 3]}] = filebufs.len();")
                rs.append("\tlet mut file = File::open(described).expect(\"could not open file\");")
                rs.append("\tlet mut temp: Vec<u8> = Vec::new();")
                rs.append("\tfilebufs.push(temp.clone());")
                rs.append("\tfile.read_to_end(&mut filebufs[filebufs.len() - 1]).expect(\"could not read file\")")
                generate_end_of_instruction(program, byte_index, 3, instructions, rs)
                byte_index += 4
            
            case 67: # get_ram_size
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tregisters[{program[byte_index + 1]}] = ram.len() as u32;")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 68: # expand_ram_reg
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")                
                generate_start_of_instruction(instructions, rs)
                rs.append("\tregisters[0] = ram.len() as u32;")
                rs.append(f"\tram.resize(ram.len() + registers[{program[byte_index + 1]}], 0);")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 69: # expand_ram_imm
                bounds_check(program, byte_index, 4)
                generate_start_of_instruction(instructions, rs)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])                
                if imm > 0:
                    if imm > 1:
                        rs.append("\tregisters[0] = ram.len() as u32;")
                        rs.append(f"\tram.resize(ram.len() + {imm}, 0);")
                    else:
                        rs.append("\tregisters[0] = ram.len() as u32;")
                        rs.append("\tram.append(0);")
                else:
                    rs.append("\tregisters[0] = (ram.len() - 1) as u32;")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 70: # set_stack_size
                bounds_check(program, byte_index, 8)
                imm = make_64_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4], program[byte_index + 5], program[byte_index + 6], program[byte_index + 7], program[byte_index + 8])                
                rs[2] = str(imm)
                generate_start_of_instruction(instructions, rs)
                generate_end_of_instruction(program, byte_index, 8, instructions, rs)
                byte_index += 9
            case 71: # import library
                try:
                    end = program.index(0, byte_index + 1)
                except:
                    error(program, byte_index, "end of string not found")
                generate_start_of_instruction(instructions, rs)
                temp = "".join([chr(v) for v in program[byte_index + 1:end]])
                if not os.path.isfile(temp):
                    error(program, byte_index, f"Attempted to read in library '{temp}', which was not found")
                file_extension = temp.split(".")[-1]
                if file_extension != "pemu":
                    error(program, byte_index, f"library must be of file extension 'pemu', not '{file_extension}'")
                program.insert(end - byte_index + 1, read_binary_file())                
                generate_end_of_instruction(program, byte_index, end - byte_index, instructions, rs)
                byte_index += end - byte_index + 1
            case 72: # jmp_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tjump(registers[{program[byte_index + 1]}], registers, ram, filebufs, flags);" )
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2 
            case 73: # jmp_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tjump({imm}, registers, ram, filebufs, flags);" )
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 74: # jils_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[0] {jump(registers[" f"{program[byte_index + 1]}" "], registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 75: # jils_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[0] {jump(" f"{imm}" ", registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 74: # jils_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[0] {jump(registers[" f"{program[byte_index + 1]}" "], registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 75: # jils_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[0] {jump(" f"{imm}" ", registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 76: # jigt_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[1] {jump(registers[" f"{program[byte_index + 1]}" "], registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 77: # jigt_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[1] {jump(" f"{imm}" ", registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 78: # jie_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[2] {jump(registers[" f"{program[byte_index + 1]}" "], registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 79: # jie_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[2] {jump(" f"{imm}" ", registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 80: # jine_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[3] {jump(registers[" f"{program[byte_index + 1]}" "], registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 81: # jine_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[3] {jump(" f"{imm}" ", registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 82: # jiover_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[4] {jump(registers[" f"{program[byte_index + 1]}" "], registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 83: # jiover_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[4] {jump(" f"{imm}" ", registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 84: # jiundr_reg
                using_jump = True
                bounds_check(program, byte_index, 1)
                if not program[byte_index + 1] < num_of_registers:
                    error(program, byte_index, f"Register idx {program[byte_index + 1]} not valid")
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[5] {jump(registers[" f"{program[byte_index + 1]}" "], registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 1, instructions, rs)
                byte_index += 2
            case 85: # jiundr_imm
                using_jump = True
                bounds_check(program, byte_index, 4)
                imm = make_32_bit(program[byte_index + 1], program[byte_index + 2], program[byte_index + 3], program[byte_index + 4])
                generate_start_of_instruction(instructions, rs)
                rs.append("\tif flags[5] {jump(" f"{imm}" ", registers, ram, filebufs, flags);}")
                generate_end_of_instruction(program, byte_index, 4, instructions, rs)
                byte_index += 5
            case 86: # assign_label
                try:
                    end = program.index(0, byte_index + 1)
                except:
                    error(program, byte_index, "end of string not found")
                generate_start_of_instruction(instructions, rs)
                labels[program[byte_index + 1:end]] = instruction + 1
                generate_end_of_instruction(program, byte_index, end - byte_index, instructions, rs)
                byte_index += end - byte_index + 1
            case 87: # jmp_label
                try:
                    end = program.index(0, byte_index + 1)
                except:
                    error(program, byte_index, "end of string not found")
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tjump({labels[program[byte_index + 1:end]]}, registers, ram, fliebufs, flags);")
                generate_end_of_instruction(program, byte_index, end - byte_index, instructions, rs)
                byte_index += end - byte_index + 1
            case 93: # flush
                using_io = True
                bounds_check(program, byte_index, 0)
                generate_start_of_instruction(instructions, rs)
                rs.append(f"\tio::stdout().flush().unwrap();")
                generate_end_of_instruction(program, byte_index, 0, instructions, rs)
                byte_index += 1
            case _:
                error(program, byte_index, "instruction not yet implemented")
    if using_commands:
        rs.insert(1, "fn execute_cmd_command(command: &String) {\n\tlet status = Command::new(\"powershell\").args(&[\"-Command\", &command]).status().expect(\"Failed to execute command\");\n}")
    if using_jump:
        temp = "\nfn jump(func: u32, registers: &mut [u32; 27], ram: &mut Vec<u32>, filebufs: &mut Vec<Vec<u8>>, flags: &mut [bool; 6]) {"
        temp += "\n\tmatch func {"
        for instruction in range(instructions):
            temp += f"\n\t\t{instruction} => " + "{" + f"instruction_{instruction + 1}(registers, ram, filebufs, flags)" + "}"
        temp += "\n\t\t_ => {exit(0);}\n\t}\n}"
        rs.insert(1, temp)
        using_exit = True
    if using_exit:
        if using_commands:
            rs.insert(1, "use std::process::{exit, Command};")
        else:
            rs.insert(1, "use std::process::exit;")
    else:
        if using_commands:
            rs.insert(1, "use std::process::Command;")
    if show_time:
        rs.insert(1, "use std::time::Instant;")
    if using_io:
        rs.insert(1, r"use std::io::{Write, self};")
        
    compilation_end_time = time.time()
    print(f"finished in {(compilation_end_time - compilation_start_time) * 1000}ms")
    write_to_rs_file(output_file, rs)
    print(f"RUST: {output_file}.rs -> .ll -> .o -> {output_file}.exe")
    if delete_waste:
        if os.system(f"rustc -O {output_file}.rs"):
            print("could not compile")
        if os.system(f"del {output_file}.pdb"):
            print("Could not delete pdb file")
        if os.system(f"del {output_file}.rs"):
            print("Could not delete rs file")
        if os.path.isfile(f"{output_file}.s"):
            if os.system(f"del {output_file}.s"):
                print("Could not delete asm file")
    else:
        if os.system(f"rustc -O {output_file}.rs"):
            print("could not compile")
        if os.system(f"rustc --emit=asm {output_file}.rs"):
            print("could not compile")
    if run:
        print(F"PEMU: {output_file}.exe OUTPUT:")
        os.system(f".\\{output_file}")

def get_pemu_file_independent(os, path: str, output_file: str, show_time: bool=True, delete_waste: bool=True, unstable: bool=False, run: bool=True) -> None:
    program: list[int] = read_binary_file(path)
    compile_stable(program, path, show_time, os, delete_waste, unstable, run, output_file)

def get_pemu_file_dependant(os, program, path, output_file: str, show_time: bool=True, delete_waste: bool=True, unstable: bool=False, run: bool=True) -> None:
    compile_stable(program, path, show_time, os, delete_waste, unstable, run, output_file)
def cli():
    import sys
    import os
    match len(sys.argv):
        case 1: # running the exe
            while True:
                command = input("'cls' to exit, please enter pemu file: ")
                if command == "cls":
                    break
                if not os.path.isfile(command):
                    print("not a valid file")
                    continue
                file_extension = command.split(".")[-1]
                if file_extension != "pemu":
                    print("please enter a pemu file")
                    continue
                get_pemu_file_independent(os, command)
        case 2: # default compilation for a file
            if not os.path.isfile(sys.argv[1]):
                print("not a valid file")
                sys.exit(1)
            file_extension = sys.argv[1].split(".")[-1]
            if file_extension != "pemu":
                print("please enter a pemu file")
                sys.exit(1)
            get_pemu_file_independent(os, sys.argv[1])
        case _: # custom compilation for a file
            if not os.path.isfile(sys.argv[1]):
                print("not a valid file")
                sys.exit(1)
            file_extension = sys.argv[1].split(".")[-1]
            if file_extension != "pemu":
                print("please enter a pemu file")
                sys.exit(1)
            if "--notimefeedback" in sys.argv:
                show_time = False
            else:
                show_time = True
            if "--nodeletewaste" in sys.argv:
                delete_waste = False
            else:
                delete_waste = True
            if "--unstable" in sys.argv:
                unstable = True
            else:
                unstable = False
            if "--norun" in sys.argv:
                run = False
            else:
                run = True
            get_pemu_file_independent(os, sys.argv[1], show_time, delete_waste, unstable, run)

if __name__ == "__main__":  
    cli()