def binary_to_signed_decimal(binary_string):
    pass

def binary_to_unsigned_decimal(num):
    pass

def decimal_to_binary(num):
    #must handle both signed and unsigned representation
    #unsignedrange-> 0 to 2^32-1
    #signedrange-> - -2^31 to 2^31-1
    #copied from assembler code modified a little
    s=''
    num= num%(2**32)
    while (num!=0):
        if (num%2==0):
            s='0'+s
        else:
            s='1'+s
        num=num//2
    s=(32-len(s))*'0'+s
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
controlSignals= {}

#Decode Phase
def generateControlSignals(instruction):
    #32 bit instructionString
    #updates control signals dictionary
    pass

def readRegisterFile(instruction):
    #32 bit instructionString
    #extracts rd

    pass

def extend(instruction, immControl):
    pass

#Execute phase
def aluExecute(source1, source2, imm):
    pass

def pcPlusTargetExecute(PC, imm):
    #you are given jal immediate or branch immediate so you will have to multiply immediate by 2
    #when computing stuff
    pass



#Instruction Fetch and MemoryWrite and RegWrite phases are handled in the run function itself
'''
registerFile= {}
dataMemory= {}
instructionMemory= []
'''

def run(input_file):
    f= open(input_file)
    instructionMemory= f.read().split("\n")
    f.close()
    PC=4
    halt= False
    while (halt!=True):
        pass