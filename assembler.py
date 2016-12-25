import re
import sys

m_types = 'bt bf j lacc sacc ltos stos'.split(' ')
io_types = 'writeport readport writedisp readdisp'.split(' ')
i_types = 'pushi pushui sll srl ori andi addi subi pra'.split(' ')
s_types = 'sas tts dup peek pop push or and add sub xor eq slt iszero dlt bang jtos !null! settop'.split(' ')
si_types = 'top'.split(' ')
inst_set = m_types + io_types + i_types + s_types + si_types

class InvalidInstructionException(Exception):
    """Invalid Instruction"""

def trans_instructions(instructions,debug=False):
    result = [] 
    flags = {} 
    pos = 0
    count = 0
    for i in instructions[::-1]:
        if i[-1] == ':':
            flags[i[:-1]]=count
        elif (i in inst_set) :
            count+=1

    while len(instructions) > 0:
        if instructions[-1] in m_types:
            result.append(decode_m_types(instructions.pop(),instructions.pop(),flags,debug))
        elif instructions[-1] in io_types:
            result.append(decode_io_types(instructions.pop(),debug))
        elif instructions[-1] in i_types:
            result.append(decode_i_types(instructions.pop(),instructions.pop(),debug))
        elif instructions[-1] in s_types:
            result.append(decode_s_types(instructions.pop(),debug))
        elif instructions[-1] in si_types:
            result.append(decode_si_types(instructions.pop(),instructions.pop(),debug))
        elif instructions[-1][-1] == ':':
            instructions.pop()
            pos-=1
        else:
            print(instructions.pop())
            raise InvalidInstructionException('Invalid Instruction'+instructions.pop())
        pos+=1
    return result,flags

def decode_m_types(inst,inp,flags,debug=False):
    if debug:
        return inst+' '+inp
    return bin(m_types.index(inst)+2)[2:].zfill(4)+(bin(flags[inp])[2:] if inp in flags else bin(int(inp))[2:]).zfill(12)

def decode_io_types(inst,debug=False):
    if debug:
        return inst
    return bin(io_types.index(inst)+9)[2:].ljust(16,'0')

def decode_i_types(inst,inp,debug=False):
    if debug:
        return inst+' '+inp
    return '0000'+bin(i_types.index(inst))[2:].zfill(4)+bin(int(inp))[2:].zfill(8)

def decode_s_types(inst,debug=False):
    if debug:
        return inst
    return '0001'+bin(s_types.index(inst))[2:].zfill(8)+'0000'

def decode_si_types(inst,inp,debug=False):
    if debug:
        return inst
    return '000100010001'+bin(inp % 16)[2:0].zfill(4)

def assemble(assembly,binary = False):
    filtered = re.sub(r"#+.*","",assembly)
    result = trans_instructions(re.findall(r"[\w']+:*",filtered)[::-1])
    if binary:
        return list(map(lambda x: int(x,2),result[0]))
    return result

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        readIn = f.read()

    result = assemble(readIn)
    if len(sys.argv) == 3:
        with open(sys.argv[2],'w') as f:
            f.write('\n'.join(result[0]))
    else:
        print('\n'.join(result[0]))
