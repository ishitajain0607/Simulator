def binary_to_signed_decimal(binary_string):
    pass

def binary_to_unsigned_decimal(num):
    pass

def decimal_to_binary(num, size):
    #must handle both signed and unsigned representation
    #unsignedrange-> 0 to 2^32-1
    #signedrange-> - -2^31 to 2^31-1
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
controlSignals= {}

registerFile= dict.fromkeys([decimal_to_binary(x, 5) for x in range(32)], '0'*32)
registerFile['00010']= '00000000000000000000000101111100' #set sp to 380

dataMemory= dict.fromkeys([unsigned_decimal_to_hex(x) for x in range(0x00010000, 0x00010080, 4)], '0'*32)


#Decode Phase
def generateControlSignals(instruction):
    #32 bit instructionString
    #updates control signals dictionary
    pass

def readRegisterFile(instruction):
    #32 bit instructionString
    #extracts rd
    #extracts rs1
    #extracts rs2
    pass

def extend(instruction):
    #extracts immediate based on control signal
    pass

#Execute phase
def aluExecute(source1, source2, imm):
    pass



def run(input_file):
    f= open(input_file)
    instructionMemory= f.read().split("\n")
    f.close()
    PC=4    
    halt= False
    while (halt!=True):
        pass