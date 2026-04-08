#Plannerd Errors
# Writing to instruction memory- dont dare do that
# Writing to memory location that doesn't exist- don't do that
# invalid opcode


def binary_to_signed_decimal(binary_string):
    num=0
    bit= binary_string[0]
    num= (num<<1)-int(bit)
    for bit in binary_string[1:]:
        num= (num<<1)+int(bit)
    return num

def binary_to_unsigned_decimal(binary_string):
    num=0
    for bit in binary_string:
        num= (num<<1)+int(bit)
    return num

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

def binary_to_hex(binary_string):
    bin_to_hex = {'0000': '0', '0001': '1', '0010': '2', '0011': '3', '0100': '4', '0101': '5', '0110': '6', '0111': '7', '1000': 
    '8', '1001': '9', '1010': 'A', '1011': 'B', '1100': 'C', '1101': 'D', '1110': 'E', '1111': 'F'}

    length= len(binary_string)
    rem= length%4

    if (rem!=0):
        binary_string= (4-rem)*'0'+binary_string
    
    hex_str = ''
    for i in range(0, len(binary_string), 4):
        four_bits= binary_string[i:i+4]
        hex_str+= bin_to_hex[four_bits]
    return '0x'+hex_str


#Memory is globally accessed by all function

#zero is branch flag
# ResultSrc can be ALU, Memory(lw) or PCplus4(jal instruction)
# ALUSrc can be Register or Immediate
# ImmSrc can be B U I J S
# PCSrc can be next: instruction(+4 bytes), pc+target, aluResult

# you will have to handle overflow aluexecute
# never write to x0

controlSignals= {'ResultSrc': 'ALU', 'MemWrite': 0, 'ALUSrcA': 'Reg','ALUSrcB': 'Reg', 'RegWrite': 0, 'ALUControl': 'add',  'ImmSrc': 'I', 'Branch': 0, 'Jump': 0, 'PCSrc':'next', 'zero': 0}
registerFile= dict.fromkeys([decimal_to_binary(x, 5) for x in range(32)], '0'*32)
registerFile['00010']= '00000000000000000000000101111100' #set sp to 380
Memory= dict.fromkeys([decimal_to_binary(x, 32) for x in range(0x0000000,  0x001007F, 4)], '0'*32)

def generateControlSignals(instruction):
    global controlSignals
    opcodes = ['0110011','0010011','0000011','0100011','1100011','1101111','1100111','0110111','0010111','0001111','1110011']
    opcode= instruction[-7:]
    funct3= instruction[-15:-12]
    funct7= instruction[:7]
    assert opcode in opcodes, "Invalid Opcode"
    #R Type
    if opcode=='0110011':
        #Main Decoder
        controlSignals['RegWrite']= 1
        controlSignals['ALUSrcA']= 'Reg'
        controlSignals['ALUSrcB']= 'Reg'
        controlSignals['MemWrite']= 0
        controlSignals['ResultSrc']='ALU'
        controlSignals['Branch']=0
        controlSignals['Jump']=0
        controlSignals['PCSrc']='next'

        #Alu Decoder-> requires opcode+funct3+funct7
        if funct3== '000':
            if funct7== '0100000':
                controlSignals['ALUControl']= 'sub'
            else:
                controlSignals['ALUControl']= 'add'
        elif funct3=='001':
            controlSignals['ALUControl']= 'sll'
        elif (funct3=='010'):
            controlSignals['ALUControl']= 'slt'
        elif (funct3=='011'):
             controlSignals['ALUControl']= 'sltu'
        elif funct3=='100':
             controlSignals['ALUControl']= 'xor'
        elif funct3=='101':
             controlSignals['ALUControl']= 'srl'
        elif funct3=='110':
            controlSignals['ALUControl']= 'or'
        elif funct3== '111':
            controlSignals['ALUControl'] = 'and'
    
    #I Type
    elif opcode== '0010011':
        #addi and sltiu
        controlSignals['RegWrite'] = 1
        controlSignals['ALUSrcA']= 'Reg'
        controlSignals['ALUSrcB'] = 'Imm'
        controlSignals['ImmSrc'] = 'I'
        controlSignals['MemWrite']= 0
        controlSignals['ResultSrc']='ALU'
        controlSignals['Branch']=0
        controlSignals['Jump']=0
        controlSignals['PCSrc']='next'

        if funct3 == '000':
            controlSignals['ALUControl'] = 'add'
        elif funct3 == '011':
            controlSignals['ALUControl'] = 'sltu'
    
    elif opcode== '0000011':
        #lw instruction
        controlSignals['RegWrite']= 1
        controlSignals['ALUSrcA']= 'Reg'
        controlSignals['ALUSrcB']= 'Imm'
        controlSignals['ImmSrc']= 'I'
        controlSignals['MemWrite']= 0
        controlSignals['ResultSrc'] = 'Mem'
        controlSignals['Branch']=0
        controlSignals['Jump']=0
        controlSignals['ALUControl'] = 'add'
        controlSignals['PCSrc']='next'

    #jalr
    elif opcode== '1100111':
        controlSignals['RegWrite']= 1
        controlSignals['ALUSrcA']= 'Reg'
        controlSignals['ALUSrcB']= 'Imm'
        controlSignals['ImmSrc']= 'I'
        controlSignals['MemWrite']= 0
        controlSignals['ResultSrc'] = 'PCplus4'
        controlSignals['Branch']=0
        controlSignals['Jump']=0
        controlSignals['ALUControl'] = 'add'
        controlSignals['PCSrc']='ALUResult'
    
    #sw
    elif opcode=='0100011':
        controlSignals['RegWrite']= 0
        controlSignals['ALUSrcA']= 'Reg'
        controlSignals['ALUSrcB']= 'Imm'
        controlSignals['ImmSrc']= 'S'
        controlSignals['MemWrite']= 1
        controlSignals['Branch']=0
        controlSignals['Jump']=0
        controlSignals['ALUControl'] = 'add'
        controlSignals['PCSrc']='next'
    #B Type
    elif opcode=='1100011':
        controlSignals['RegWrite']= 0
        controlSignals['ALUSrcA']= 'Reg'
        controlSignals['ALUSrcB']= 'Reg'
        controlSignals['ImmSrc']= 'B'
        controlSignals['MemWrite']= 0
        controlSignals['Branch']=1
        controlSignals['Jump']=0
        #PC Src is determined at ALUExecution
        if funct3 == '000':
            controlSignals['ALUControl'] = 'beq'
        elif funct3 == '001':
            controlSignals['ALUControl'] = 'bne'
        elif funct3 == '100':
            controlSignals['ALUControl'] = 'blt'
        elif funct3 == '101':
            controlSignals['ALUControl'] = 'bge'
        elif funct3 == '110':
            controlSignals['ALUControl'] = 'bltu'
        elif funct3 == '111':
            controlSignals['ALUControl'] = 'bgeu'
    
    #jal
    elif opcode=='1101111':
        controlSignals['RegWrite']= 1
        controlSignals['ResultSrc'] = 'PCplus4'
        controlSignals['ImmSrc']= 'J'
        controlSignals['MemWrite']= 0
        controlSignals['Branch']=0
        controlSignals['Jump']=1
        controlSignals['ALUControl'] = 'None'
        controlSignals['PCSrc']='pc+target'
    
    #lui
    elif opcode=='0110111':
        controlSignals['RegWrite']= 1
        controlSignals['ResultSrc'] = 'ALU'
        controlSignals['ALUSrcA']= 'Reg'
        controlSignals['ALUSrcB']= 'Imm'
        controlSignals['ImmSrc']= 'U'
        controlSignals['MemWrite']= 0
        controlSignals['Branch']=0
        controlSignals['Jump']=0
        controlSignals['ALUControl'] = 'lui'
    elif opcode=='0010111':
        controlSignals['RegWrite']= 1
        controlSignals['ResultSrc'] = 'ALU'
        controlSignals['ALUSrcA']= 'PC'
        controlSignals['ALUSrcB']= 'Imm'
        controlSignals['ImmSrc']= 'U'
        controlSignals['MemWrite']= 0
        controlSignals['Branch']=0
        controlSignals['Jump']=0
        controlSignals['ALUControl'] = 'add'

def readRegisterFile(instruction):
    rd= instruction[-12:-7]
    rs1= instruction[-20:-15]
    rs2= instruction[-25:-20]
    return (rd, rs1, rs2)

def extend(instruction):
    control= controlSignals['ImmSrc']
    if control=='I':
        str_imm= instruction[:12]
        str_imm= str_imm[0]*(20)+str_imm
    elif control=='B':
        str_imm= instruction[-32]+instruction[-8]+instruction[-31:-25]+instruction[-12:-8]+'0'
        str_imm= str_imm[0]*(19)+str_imm
    elif control=='S':
        str_imm=instruction[:7]+instruction[-12:-7]
        str_imm= str_imm[0]*(20)+str_imm
    elif control=='U':
        str_imm=instruction[:20]
        str_imm= str_imm+'0'*12
    elif control=='J':
        str_imm=instruction[0]+instruction[12:20]+instruction[11]+instruction[1:11]+'0'
        str_imm= str_imm[0]*(11)+str_imm
    return str_imm


#Execute phase
def aluExecute(pc, rs1, rs2, imm):
    control= controlSignals['opcode']
    #add/sub/sll/slt/sltu/xor/srl/or/and
    #beq/bne/blt/bge/bltu/bgeu
    if (control=='add'):
        pass
    elif (control=='sub'):
        pass
    elif (control=='sll'):
        pass
    elif (control=='slt'):
        pass
    elif (control=='sltu'):
        pass
    elif (control=='xor'):
        pass
    elif (control=='srl'):
        pass
    elif (control=='and'):
        pass



def run(input_file):
    f= open(input_file)
    l= f.readlines()
    f.close()
    
    PC=0
    halt= False
    while (halt!=True):
        pass
    #memory stage is not written as a function
    #write back to register file