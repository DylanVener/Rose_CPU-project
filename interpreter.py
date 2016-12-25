import re
import sys
from assembler import assemble

class intepreter:
    def __init__(self,file):
        with open(file) as f:
            self.instructions = f.read()
        if self.instructions.isnumeric():
            self.memory = list(map(lambda x: int(x,2),self.instructions.split('\n')))
        else:
            self.memory = assemble(self.instructions,True)
        self.memory.extend([0]*1000)
        self.pc = 0
        self.pctop = 0
        self.stack = []
        self.acc = 0
        self.port = 0
        self.display = 0
        self.step_count = 0
        self.cycle_count = 0

    def step(self):
        self.step_count += 1
        inst = bin(self.memory[self.pc])[2:].zfill(16)
        if inst[:4] == '0000': #I-type
            if inst[4:8] == '0000': #pushi
                self.stack.append(int(inst,2))
                self.cycle_count+=2
            elif inst[4:8] == '0001': #pushui
                self.stack[-1] = (int(inst[8:],2)<<8) + stack[-1]
                self.cycle_count+=2
            elif inst[4:8] == '0010': #sll
                self.stack[-1] = self.stack[-1]<<int(inst[8:],2)
                self.cycle_count+=4
            elif inst[4:8] == '0011': #srl
                self.stack[-1] = self.stack[-1]>>int(inst[8:],2)
                self.cycle_count+=4
            elif inst[4:8] == '0100': #ori
                self.stack[-1] = self.stack[-1]>>int(inst[8:],2)
                self.cycle_count+=4
            elif inst[4:8] == '0101': #andi
                self.stack[-1] = self.stack[-1]&int(inst[8:],2)
                self.cycle_count+=4
            elif inst[4:8] == '0110': #addi
                self.stack[-1] = self.stack[-1]+int(inst[8:],2)
                self.cycle_count+=4
            elif inst[4:8] == '0111': #subi
                self.stack[-1] = self.stack[-1]-int(inst[8:],2)
                self.cycle_count+=4
            elif inst[4:8] == '1000': #pra
                self.stack.append(self.pc+1+int(inst[8:],2))
                self.cycle_count+=4
        
        if inst[:4] == '0001': #S-type
            if inst[4:12] == '00000000': #sas
                self.acc, self.stack[-1] = self.stack[-1], self.acc
                self.cycle_count+=3
            elif inst[4:12] == '00000001': #tts
                self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
                self.cycle_count+=2
            elif inst[4:12] == '00000010': #dup
                self.stack.append(self.stack[-1])
                self.cycle_count+=2
            elif inst[4:12] == '00000011': #peek
                self.acc = self.stack[-1]
                self.cycle_count+=2
            elif inst[4:12] == '00000100': #pop
                self.acc = self.stack.pop()
                self.cycle_count+=2
            elif inst[4:12] == '00000101': #push
                self.stack.append(self.acc)
                self.cycle_count+=2
            elif inst[4:12] == '00000110': #or
                self.stack.append(self.stack.pop() | self.stack.pop())
                self.cycle_count+=4
            elif inst[4:12] == '00000111': #and
                self.stack.append(self.stack.pop() & self.stack.pop())
                self.cycle_count+=4
            elif inst[4:12] == '00001000': #add
                self.stack.append(self.stack.pop() + self.stack.pop())
                self.cycle_count+=4
            elif inst[4:12] == '00001001': #sub
                self.stack.append(self.stack.pop() - self.stack.pop())
                self.cycle_count+=4
            elif inst[4:12] == '00001010': #xor
                self.stack.append(self.stack.pop() ^ self.stack.pop())
                self.cycle_count+=4
            elif inst[4:12] == '00001011': #eq
                self.stack.append(self.stack.pop() == self.stack.pop())
                self.cycle_count+=4
            elif inst[4:12] == '00001100': #slt
                self.stack.append(self.stack.pop() < self.stack.pop())
                self.cycle_count+=4
            elif inst[4:12] == '00001101': #iszero
                self.stack.append(self.stack.pop() == 0)
                self.cycle_count+=4
            elif inst[4:12] == '00001110': #dlt
                self.stack.pop()
                self.cycle_count+=2
            elif inst[4:12] == '00001111': #bang
                self.stack.append(self.stack.pop() ^ (2**16))
                self.cycle_count+=4
            elif inst[4:12] == '00010000': #jtos
                self.pc = self.stack.pop() - 1
                self.cycle_count+=2
            elif inst[4:12] == '00010001': #top
                self.pctop = int(inst[12:],2)
                self.cycle_count+=2
            elif inst[4:12] == '00010010': #settop
                self.pctop = self.pc>>8
                self.cycle_count+=2

        if inst[:4] == '0010': #bt
            if self.stack.pop():
                self.pc = int(inst[4:],2) - 1
            self.cycle_count+=4

        if inst[:4] == '0011': #bf
            if not self.stack.pop():
                self.pc = int(inst[4:],2) - 1
            self.cycle_count+=4

        if inst[:4] == '0100': #j
            self.pc = int(inst[4:],2) - 1
            self.cycle_count+=2

        if inst[:4] == '0101': #lacc
            self.acc = self.memory[int(inst[12:],2)]
            self.cycle_count+=3
        if inst[:4] == '0110': #sacc
            self.memory[int(inst[4:],2)] = self.acc
            self.cycle_count+=3
        if inst[:4] == '0111': #ltos
            self.stack.append(self.memory[int(inst[12:]),2])
            self.cycle_count+=2
        if inst[:4] == '1000': #stos
            self.memory[int(inst[4:],2)] = self.stack.pop()
            self.cycle_count+=2
        if inst[:4] == '1001': #writeport
            self.port = self.acc
            self.cycle_count+=2
        if inst[:4] == '1010': #readport
            self.acc = self.port
            self.cycle_count+=2
        if inst[:4] == '1011': #writedisp
            self.display = self.acc
            self.cycle_count+=2
            print(self.display)
        if inst[:4] == '1100': #readdisp
            self.acc = self.display
            self.cycle_count+=2
        
        self.pc += 1 
    
    def reset(self):
        self.pc = 0
        self.pctop = 0
        self.step_count = 0
        self.port = 0
        self.display = 0
        self.stack = []
        self.acc = 0
        self.memory = assemble(self.instructions,True)
        self.memory.extend([0]*1000)
            
if __name__ == '__main__':
    infile = input('Assembly File: ')
    inter = intepreter(infile)
    breaks = []
    while True:
        com = input('Command: ').lower()
        if com == 'step':
            inter.step()
        elif com == 'debug':
            print('pc: {0}'.format(inter.pc))
            print('Stack: {0}'.format(inter.stack))
            print('Accumulator: {0}'.format(inter.acc))
            print('port: {0}'.format(inter.port))
            print('display: {0}'.format(inter.display))
            print('step: {0}'.format(inter.step_count))
            print('cycle: {0}'.format(inter.cycle_count))
            print('CPI: {0}'.format(inter.cycle_count/inter.step_count))
        elif com == 'pc':
            print('pc: {0}'.format(inter.pc))
        elif com == 'stack':
            print('Stack: {0}'.format(inter.stack))
        elif com == 'acc':
            print('Accumulator: {0}'.format(inter.acc))
        elif com == 'port':
            print('port: {0}'.format(inter.port))
        elif com == 'display':
            print('display: {0}'.format(inter.display))
        elif com == 'steps':
            print('step: {0}'.format(inter.step_count))
        elif com == 'cycles':
            print('cycle: {0}'.format(inter.cycle_count))
        elif com == 'cpi':
            print('CPI: {0}'.format(inter.cycle_count/inter.step_count))
        elif com == 'run':
            while(inter.pc not in breaks):
                inter.step()
        elif com == 'continue':
            inter.step()
            while(inter.pc not in breaks):
                inter.step()
        elif com == 'set break':
            breaks.append(int(input('break point: ')))
        elif com == 'clear breaks':
            breaks = []
        elif com == 'set port':
            inter.port = int(input(':'))
        elif com == 'reset':
            inter.reset()
        elif com == 'quit':
            break
        else:
            print('Allowed Commands:')
            print('step, debug, pc, acc, port, display steps, cycles, cpi run, set break, clear breaks, set port, reset, quit, help')
