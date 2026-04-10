#Plannerd Errors
# Writing to instruction memory- dont dare do that
# Writing to memory location that doesn't exist- don't do that
# invalid opcode
import sys

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

def decimal_to_binary(num, size=32):
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
    bin_to_hex = {'0000': '0','0001': '1','0010': '2','0011': '3', '0100': '4', '0101': '5', '0110': '6', '0111': '7', '1000': 
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
registerFile['00010']= decimal_to_binary(0x0000017C) #set sp to 380
Memory= dict.fromkeys([decimal_to_binary(x, 32) for x in range(0x0000000,  0x001007F, 4)], '0'*32)

def generateControlSignals(instruction):
    global controlSignals
    opcode= instruction[-7:]
    funct3= instruction[-15:-12]
    funct7= instruction[:7]
    controlSignals['zero']=0
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
        str_imm= instruction[0]+instruction[24]+instruction[1:7]+instruction[20:24]+'0'
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
def aluExecute(pc_str, rs1, rs2, imm):
    control= controlSignals['ALUControl']
    #add/sub/sll/slt/sltu/xor/srl/or/and
    #beq/bne/blt/bge/bltu/bgeu
    #lui
    #ALUSrcA- Reg, Imm, PC
    #ALUSrcB- Reg, Imm, PC
    srcA= ''
    srcB= ''
    controlA= controlSignals['ALUSrcA']
    controlB= controlSignals['ALUSrcB']
    output=""

    if(controlA=='Reg'):
        srcA=rs1
    elif(controlA=='PC'):
        srcA=pc_str

    if (controlB=='Imm'):
        srcB=imm
    elif (controlB=='Reg'):
        srcB=rs2


    if (control=='add'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        final_val= (val_srcA+val_srcB) & (0xFFFFFFFF)
        output= decimal_to_binary(int(final_val))

    elif (control=='sub'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        final_val= (val_srcA-val_srcB) & (0xFFFFFFFF)
        output= decimal_to_binary(int(final_val))

    elif (control=='sll'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_unsigned_decimal(srcB[-5:])
        final_val= (val_srcA<<val_srcB) & (0xFFFFFFFF)
        output= decimal_to_binary(int(final_val))

    elif (control=='slt'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        final_val= (val_srcA<val_srcB)
        output= decimal_to_binary(int(final_val))
    
    elif (control=='sltu'):
        val_srcA= binary_to_unsigned_decimal(srcA)
        val_srcB= binary_to_unsigned_decimal(srcB)
        final_val= (val_srcA<val_srcB)
        output= decimal_to_binary(int(final_val))
    
    elif (control=='xor'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        final_val= (val_srcA^val_srcB) & (0xFFFFFFFF)
        output= decimal_to_binary(int(final_val))
    
    elif (control=='srl'):
        val_srcA= binary_to_unsigned_decimal(srcA)
        val_srcB= binary_to_unsigned_decimal(srcB[-5:])
        final_val= (val_srcA>>val_srcB) & (0xFFFFFFFF)
        output= decimal_to_binary(int(final_val))


    elif (control=='and'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        final_val= (val_srcA&val_srcB) & (0xFFFFFFFF)
        output= decimal_to_binary(int(final_val))

    elif (control=='or'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        final_val= (val_srcA|val_srcB) & (0xFFFFFFFF)
        output= decimal_to_binary(int(final_val))

    elif (control=='lui'):
        output= srcB

    #branch instructions
    elif (control=='beq'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        controlSignals['zero']= (val_srcA==val_srcB)
    elif (control=='bne'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        controlSignals['zero']= (val_srcA!=val_srcB)
    elif (control=='blt'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        controlSignals['zero']= (val_srcA<val_srcB)
    elif (control=='bge'):
        val_srcA= binary_to_signed_decimal(srcA)
        val_srcB= binary_to_signed_decimal(srcB)
        controlSignals['zero']= (val_srcA>=val_srcB)
    elif (control=='bltu'):
        val_srcA= binary_to_unsigned_decimal(srcA)
        val_srcB= binary_to_unsigned_decimal(srcB)
        controlSignals['zero']= (val_srcA<val_srcB)
    elif (control=='bgeu'):
        val_srcA= binary_to_unsigned_decimal(srcA)
        val_srcB= binary_to_unsigned_decimal(srcB)
        controlSignals['zero']= (val_srcA>=val_srcB)
    branch= controlSignals['Branch']
    jump= controlSignals['Jump']
    
    if (controlSignals['zero'] and branch):
        controlSignals['PCSrc']='pc+target'
    elif (controlSignals['zero']==False and branch):
        controlSignals['PCSrc']='next'
    
    return output


def run(input_file, output_file):
    error=False
    f= open(input_file)
    l= f.readlines()
    cnt=0
    for line in l:
        Memory[decimal_to_binary(cnt)]=line.strip()
        cnt+=4
    f.close()

    halt_instr = '00000000000000000000000001100011'
    PC=0
    instr_num=0
    f= open(output_file, 'w')
    while (True):
        #fetch 
        instr_num+=1
        pc_str= decimal_to_binary(PC)
        instr= Memory[pc_str]
        if (instr==halt_instr):
            f.write('0b'+decimal_to_binary(PC)+' ')
            for val in sorted(registerFile):
                f.write('0b'+registerFile[val]+' ')
            f.write('\n')
            break

        #decode instruction
        generateControlSignals(instr)
        rd, rs1, rs2= readRegisterFile(instr)
        val_rs1= registerFile[rs1]
        val_rs2= registerFile[rs2]
        imm= extend(instr)
        #execute stage

        aluResult= aluExecute(pc_str, val_rs1, val_rs2, imm)
        pcPlusTarget= decimal_to_binary(PC+binary_to_signed_decimal(imm))
        #memory stage
        if (controlSignals["MemWrite"]==1 or controlSignals["ResultSrc"]=="Mem"):
            num= binary_to_unsigned_decimal(aluResult)
            if ((not (0x00000100<= num and num<=0x0000017F)) and (not (0x00010000<= num and num <= 0x0001007F)) or num%4!=0):
                error=True
                break
        try:
            mem_val= Memory[aluResult]
        except:
            mem_val='0'*32
        if (controlSignals['MemWrite']):
            num= binary_to_unsigned_decimal(aluResult)
            Memory[aluResult]= val_rs2

        #Reg Write
        #Ctrl Signals ALU, Mem, PCplus4
        write_val=''
        if (controlSignals['RegWrite']):
            if controlSignals['ResultSrc']=='ALU':
                write_val= aluResult
            elif controlSignals['ResultSrc']=='Mem':
                write_val= mem_val
            elif controlSignals['ResultSrc']=='PCplus4':
                write_val= decimal_to_binary(PC+4)
        
        if rd!='00000' and controlSignals['RegWrite']:
            registerFile[rd]= write_val
        #Now move to next instruction
        if controlSignals['PCSrc']== 'next':
            PC=PC+4
        elif controlSignals['PCSrc']=='ALUResult':
            PC= binary_to_unsigned_decimal(aluResult)
        elif controlSignals['PCSrc']=='pc+target':
            PC= binary_to_unsigned_decimal(pcPlusTarget)
        f.write('0b'+decimal_to_binary(PC)+' ')
        for val in sorted(registerFile):
            f.write('0b'+registerFile[val]+' ')
        f.write('\n')
    #print memory
    if (not error):
        for address in range(0x00010000, 0x00010080, 4):
            bin_address= decimal_to_binary(address)
            hex_address= binary_to_hex(bin_address)
            f.write(hex_address+':'+'0b'+Memory[bin_address]+'\n')
    f.close()

def run(input_file, output_file):
    has_error= False

    #this will fetch the memory properly to avoid crashes
    with open(input_file, 'r') as fin:
        addr=0
        for line in fin:
            Memory[decimal_to_binary(addr)] = line.strip()
            addr+= 4

    HALT='00000000000000000000000001100011'
    PC=0

    with open(output_file, 'w') as fout:
        while True:
            pc_bin=decimal_to_binary(PC)
            instr=Memory.get(pc_bin, '0' * 32)
            if instr==HALT:
                fout.write('0b' + pc_bin + ' ')
                for reg in sorted(registerFile):
                    fout.write('0b' + registerFile[reg] + ' ')
                fout.write('\n')
                break

            generateControlSignals(instr)
            rd, rs1, rs2=readRegisterFile(instr)

            val1=registerFile[rs1]
            val2=registerFile[rs2]
            imm=extend(instr)

            alu_out=aluExecute(pc_bin, val1, val2, imm)

            if controlSignals["MemWrite"] or controlSignals["ResultSrc"] == "Mem":
                addr_val=binary_to_unsigned_decimal(alu_out)

                if ((not (0x00000100 <= addr_val<= 0x0000017F) and not (0x00010000 <= addr_val <=0x0001007F)) or (addr_val% 4!= 0)):
                    has_error=True
                    break
            mem_val=Memory.get(alu_out, '0'*32)

            if controlSignals['MemWrite']:
                Memory[alu_out]= val2

            if controlSignals['RegWrite']:
                if controlSignals['ResultSrc']=='ALU':
                    write_val = alu_out
                elif controlSignals['ResultSrc']=='Mem':
                    write_val = mem_val
                else:
                    write_val = decimal_to_binary(PC + 4)

                # never write to x0
                if rd!='00000':
                    registerFile[rd] = write_val

            mode=controlSignals['PCSrc']

            if mode=='next':
                PC+=4
            elif mode=='ALUResult':
                PC=binary_to_unsigned_decimal(alu_out)
            elif mode=='pc+target':
                if controlSignals['Jump'] == 1:
                    #JAL handling
                    PC= PC+binary_to_signed_decimal(imm)
                else:
                    #Branch handlung
                    PC=PC+binary_to_signed_decimal(imm)

            fout.write('0b' + decimal_to_binary(PC) + ' ')
            for reg in sorted(registerFile):
                fout.write('0b' + registerFile[reg]+ ' ')
            fout.write('\n')

        #printing memory
        if not has_error:
            for addr in range(0x00010000, 0x00010080, 4):
                bin_addr= decimal_to_binary(addr)
                fout.write(
                    binary_to_hex(bin_addr) + ':' + '0b' + Memory[bin_addr] + '\n'
                )


run(sys.argv[1], sys.argv[2])