def binary_to_signed_decimal(binary_string):
    pass

def decimal_to_binary(num, size):
    #must handle both signed and unsigned representation
    #unsignedrange-> 0 to 2^32-1
    #signedrange-> -2^31 to 2^31-1
    #copied from assembler code and modified a little
    s=''
    num= num%(2**size)
    while (num!=0):
        if (num%2==0):
            s='0'+s
        else:
            s='1'+s
        num=num//2
    s=(size-len(s))*'0'+s
    return s

def unsigned_decimal_to_hex(num):
    s=''
    while (num!=0):
        if ((num%16)<=9):
            s=str(num%16)+s
        else:
            s=chr(num%16+ord('A')-10)+s
        num=num//16
    s=(8-len(s))*'0'+s
    return s

#Memory is globally accessed by all function

registerFile= {}
dataMemory= {}
instructionMemory= []
controlSignals= {'ResultSRC': 'ALU', 'MemWrite': 0, 'ALUSrc': 'Register', 'RegWrite': 0, 'ALUControl': 'add',  'ImmSrc': 'I', 'Branch': 0, 'Jump': 0, 'PCSrc':'next'}

# ResultSrc can be ALUResult, Memory(lw) or PCplus4(jal instruction)
# ALUSrc can be Register or Immediate
# ImmSrc can be B U I J S
# PCSrc can be next instruction(+4 bytes), pc+target, aluResult

# you will have to handle overflow aluexecute
# never write to x0


registerFile= dict.fromkeys([decimal_to_binary(x, 5) for x in range(32)], '0'*32)
registerFile['00010']= '00000000000000000000000101111100' #set sp to 380

dataMemory= dict.fromkeys([unsigned_decimal_to_hex(x) for x in range(0x00010000, 0x00010080, 4)], '0'*32)

print(dataMemory)

#Decode Phase
def generateControlSignals(instruction):
    #32 bit instructionString
    #updates control signals dictionary
    pass

def readRegisterFile(instruction):
    #Ansh
    #32 bit instructionString
    #extracts rd
    #extracts rs1
    #extracts rs2
    #return rd, rs1, rs2 as tuple each of these are binary string of length 5
    pass

def extend(instruction):
    #extracts immediate based on control signal
    #returns binary string
    #12 bit immediate- branch instruction
    #20 bit immediate- jump imstruction
    pass

#Execute phase
def aluExecute(rs1, rs2, imm):
    #performs operation
    #these are all strings rs1->32 bit string
    #these are all strings rs2->32 bit string
    #return string_imm
    pass

def pcPlusTargetCompute(pc, imm):
    #pc+(imm)*2
    pass

def run(input_file):
    f= open(input_file)
    instructionMemory= f.read().split("\n")
    f.close()
    PC=4    
    halt= False
    while (halt!=True):
        pass
    #memory stage is not here
    #write back to register file