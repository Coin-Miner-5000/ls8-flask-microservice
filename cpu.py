"""CPU functionality."""

import sys
NOP = 0
AND = 0b10101000
NOT = 0b01101001
XOR = 0b10101011
HLT = 1
LDI = 130
LD = 131
PRN = 71
MUL = 162
PUSH = 69
POP = 70
CALL = 80
ADD = 160
RET = 17
CMP = 167
JEQ = 85
JNE = 86
JMP = 84
PRA = 72
INC = 101
DEC = 102
SUB = None
DIV = None

SP = 7  # Stack Pointer


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        # Program Counter
        self.pc = 0
        # Stack Pointer, initialized 1 spot above the beginning of stack when empty
        self.reg[SP] = 0xF4
        # Flags register
        self.FL = 0b00000000

    def load(self):
        """Load a program into memory."""
        # Error handling
        # if len(sys.argv) != 2:
        #     print("usage: ls8.py filename")
        #     sys.exit(1)

        # progname = sys.argv[1]
        progname = "room.ls8"
        address = 0

        with open(progname) as f:
            # iterate through each line in the program
            for line in f:
                # remove any comments
                line = line.split("#")[0]
                # remove whitespace
                line = line.strip()
                # skip empty lines
                if line == "":
                    continue

                value = int(line, 2)
                # set the binary instruction to memory
                self.ram[address] = value
                address += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        # MAR = Memory Address Register, contains the address that is being read or written to
        # MDR =  Memory Data Register, contains the data that was read or the data to write
        self.ram[MAR] = MDR

    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""
        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                # set the E flag to 1
                self.FL = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                # set the L flag to 1
                self.FL = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                # set the G flag to 1
                self.FL = 0b00000010
        elif op == INC:
            # increment the value in the given register
            self.reg[reg_a] += 1
        elif op == DEC:
            # decrement the value in the given register
            self.reg[reg_a] -= 1
        elif op == AND:
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == NOT:
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == XOR:
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == DIV:
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # load the program
        self.load()

        response = ""

        while True:
            # Instruction Register, contains a copy of the currently executing instruction
            IR = self.ram_read(self.pc)
            # AABCDDDD
            # Grab AA of the program instruction for the operand count
            operand_count = IR >> 6
            # Grab C of the program instruction for if the instruction sets PC counter
            sets_pc = IR >> 4 & 0b0001
            # Grab B of the program instruction for if the instruction is an ALU command
            is_alu = IR >> 5 & 0b001

            if IR == LDI:
                address = self.ram_read(self.pc + 1)
                value = self.ram_read(self.pc + 2)
                # store the data
                self.reg[address] = value
                # increment the PC by 3 to skip the arguments

            elif IR == LD:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                # Loads registerA with the value at the memory address stored in registerB
                # self.reg[reg_a] = self.reg[reg_b]
                self.reg[reg_a] = self.ram_read(self.reg[reg_b])

            elif IR == PRN:
                data = self.ram_read(self.pc + 1)
                # print the data
                print(self.reg[data])
                # increment the PC by 2 to skip the argument

            elif is_alu == 1:
                if operand_count == 2:
                    reg_a = self.ram_read(self.pc + 1)
                    reg_b = self.ram_read(self.pc + 2)
                    self.alu(IR, reg_a, reg_b)
                else:
                    reg_a = self.ram_read(self.pc + 1)
                    self.alu(IR, reg_a)
            elif IR == PUSH:
                # grab the register operand
                reg = self.ram_read(self.pc + 1)
                # to get the value in register
                val = self.reg[reg]
                # decrement the SP
                self.reg[SP] -= 1
                # Copy the value from the given register to RAM at the SP index
                self.ram_write(self.reg[SP], val)

            elif IR == POP:
                # grab the address of where to store the value in register
                reg = self.ram_read(self.pc + 1)
                # get the last value in the stack
                last_value = self.ram_read(self.reg[SP])
                # assign that value in the register at the provided address
                self.reg[reg] = last_value
                # increment the SP
                self.reg[SP] += 1

            elif IR == CALL:
                self.reg[SP] -= 1
                self.ram_write(self.reg[SP], self.pc + 2)
                reg = self.ram_read(self.pc + 1)
                self.pc = self.reg[reg]

            elif IR == RET:
                self.pc = self.ram_read(self.reg[SP])
                self.reg[SP] += 1

            elif IR == JEQ:
                # get the 1st operand, the register address
                reg = self.ram_read(self.pc + 1)
                # if the E flag is true
                if self.FL & 0b00000001 == 1:
                    # jump to the address stored at the given register
                    self.pc = self.reg[reg]
                else:
                    self.pc += operand_count + 1

            elif IR == JNE:
                # get the 1st operand, the register address
                reg = self.ram_read(self.pc + 1)
                # if the E flag is false
                if self.FL & 0b00000001 == 0:
                    # jump to the address stored at the given register
                    self.pc = self.reg[reg]
                else:
                    self.pc += operand_count + 1

            elif IR == JMP:
                reg = self.ram_read(self.pc + 1)
                # Jump to the address stored in the given register.
                # Set the PC to the address stored in the given register.
                self.pc = self.reg[reg]

            elif IR == PRA:
                # get the 1st operand, the register address
                reg = self.ram_read(self.pc + 1)
                # Print to the console the ASCII character corresponding to the value in the RAM.
                # print(chr(self.ram_read(self.reg[reg])), end="")
                # print(chr(self.reg[reg]), end="")
                response += chr(self.reg[reg])

            elif IR == NOP:
                self.pc += 0

            elif IR == HLT:
                # sys.exit(0)
                return response

            else:
                print(f"I did not understand that command: {IR}")
                sys.exit(1)

            if sets_pc == 0:
                self.pc += operand_count + 1

