import sys

def checkArgv():
    if len(sys.argv)==1:
        print('Please set asm filename')
        exit()
    elif len(sys.argv)>=3:
        print('Please only set 1 argument for asm filename')
        exit()

def readAsmFile(filepath):
    f=open(filepath,'r')
    lines = f.readlines()
    f.close()
    return lines

def readAsmLine(line):
    line_split=line.split()#split 은 공백을 기준으로 나눠준다 split('_') 이건 _ 이걸 기준으로! 디폴트가 공백
    line_label = ''
    line_opcode = ''
    line_operand = ''

    if line[0] == '.' :
        return ['.','.','.']
    if len(line_split) == 1 :
        line_opcode = line_split[0]
    elif len(line_split) == 2 :
        line_opcode, line_operand = line_split
        line_opcode = line_split[0]
        line_operand = line_split[1]
    elif len(line_split) == 3 :
        line_label, line_opcode, line_operand = line_split
    return [line_label,line_opcode,line_operand]

#--------------------------------------
def assemble_type_find_sym(LOCCTR,SYMTAB,OPTAB,line_opreand,line_opcode,objectfile) :
    line_opreand_addr = SYMTAB[line_opreand]
    LOCCTR_h = hex(LOCCTR)
    LOCCTR_str = LOCCTR_h.split('0x')
    op_car=OPTAB[line_opcode]
    op_car = op_car | 3 # n = 1, i = 1
    op_car = op_car << 4 # x = 0, b = 0, p = 0, e = 0
    op_car = op_car | 2 # p = 1
    op_car = op_car << 12 # address 부분
    pc_relative = line_opreand_addr - 3 - LOCCTR
    op_car = op_car | pc_relative
    op_car_h = hex(op_car)
    final_op = op_car_h.split('0x')
    objectfile.append([LOCCTR_str[1].upper().zfill(5),final_op[1].upper().zfill(6),line_opcode])
#--------------------------------------

#--------------------------------------
def assemble_type_immediate(LOCCTR,OPTAB,line_opreand,line_opcode,objectfile) :
    t_str = line_opreand.split('#')
    line_opreand_imm = int(t_str[1])
    LOCCTR_h = hex(LOCCTR)
    LOCCTR_str = LOCCTR_h.split('0x')
    op_car = OPTAB[line_opcode]
    op_car = op_car | 1  # n = 0, i = 1
    op_car = op_car << 4  # x = 0, b = 0, p = 0, e = 0
    op_car = op_car << 12  # address 부분
    op_car = op_car | line_opreand_imm
    op_car_h = hex(op_car)
    final_op = op_car_h.split('0x')
    objectfile.append([LOCCTR_str[1].upper().zfill(5), final_op[1].upper().zfill(6), line_opcode])
#--------------------------------------

#--------------------------------------
def assemble_type_RSUB(LOCCTR,OPTAB,line_opcode,objectfile) :
    LOCCTR_h = hex(LOCCTR)
    LOCCTR_str = LOCCTR_h.split('0x')
    op_car = OPTAB[line_opcode]
    op_car = op_car | 3  # n = 1, i = 1
    op_car = op_car << 4  # x = 0, b = 0, p = 0, e = 0
    op_car = op_car << 12  # address 부분 RSUB 는 000
    op_car_h = hex(op_car)
    final_op = op_car_h.split('0x')
    objectfile.append([LOCCTR_str[1].upper().zfill(5), final_op[1].upper().zfill(6), line_opcode])
#--------------------------------------

#--------------------------------------
def assemble_type_BYTEorWORD(LOCCTR,line_opreand,objectfile) :
    line_opreand_int = int(line_opreand)
    LOCCTR_h = hex(LOCCTR)
    LOCCTR_str = LOCCTR_h.split('0x')
    line_opreand_hex = hex(line_opreand_int)
    line_opreand_str = line_opreand_hex.split('0x')
    objectfile.append([LOCCTR_str[1].upper().zfill(5), line_opreand_str[1].upper().zfill(6), 'LDA'])
#--------------------------------------

def main():
    checkArgv()
    #initialization
    intermediate_file = []
    #dictionary
    SYMTAB={}
    #OP Table
    OPTAB = {'START' : '','LDA':0x00 ,'STA' : 0x0C, 'ADD' : 0x18, 'RSUB' : 0x4C}
    # --------pass 1-----------------
    LOCCTR = 0
    way = 'D:\\pycharm\\untitled\\asmtest.asm'
    lines = readAsmFile(way)
    for line in lines:
        line_label,line_opcode,line_opreand = readAsmLine(line)
        if line_opcode == 'START':
            start_addr = int(line_opreand)
            LOCCTR = start_addr
            intermediate_file.append(['',line_label,line_opcode,line_opreand])
        elif line_opcode != 'END' :
            if not line_label == '.' :
                if not line_label == '' :
                    if line_label in SYMTAB:
                        print('ERROR : duplicated symbol')
                        exit()
                    else :
                        SYMTAB[line_label] = LOCCTR

                intermediate_file.append([LOCCTR, line_label, line_opcode, line_opreand])
                if line_opcode in OPTAB :
                    LOCCTR+=3
                elif line_opcode =='WORD' :
                    LOCCTR+=3
                elif line_opcode == 'RESW' :
                    LOCCTR+=3*int(line_opreand)
                elif line_opcode =='RESB' :
                    LOCCTR+=int(line_opreand)
                elif line_opcode == 'BYTE' :
                    print('implement later')
                else :
                    print("Error : invalid operation code")
                    exit()

    program_length = LOCCTR - start_addr
    print (SYMTAB.items())
    for line in intermediate_file :
        print(line)
#--------------------------pass2-------------------------------
    for line in intermediate_file :
        objectfile=[]
        LOCCTR, line_label, line_opcode, line_opreand = line
        if line_opcode =='START':
            print("Do nothing")
        if line_opcode != 'END' :
            if line not in objectfile : # not a comment line then
                if line_opcode in OPTAB :
                    if not line_opreand == '' :
                        if line_opreand in SYMTAB :
                            #어셈블 ( 심볼을 찾은경우 )
                            assemble_type_find_sym(LOCCTR, SYMTAB, OPTAB, line_opreand, line_opcode, objectfile)
                        elif line_opreand.find('#')+1 :
                            # '#~~'처리 값이 없을 경우 -1
                            # 있는경우는 #이 무조건 처음에 나와서 0을 리턴함으로 + 1로 문장 실행
                            assemble_type_immediate(LOCCTR, OPTAB, line_opreand, line_opcode, objectfile)
                        else :
                            line_opreand = 0
                            # 아직 상황 없음 ( 예외? )
                    else :
                        line_opreand = 0
                        #함수이용 어셈블 ( RSUB )
                        assemble_type_RSUB(LOCCTR, OPTAB, line_opcode, objectfile)
                elif line_opcode == 'BYTE' or line_opcode == 'WORD' :
                    #함수이용 어셈블 ( 바이트 워드 )
                    assemble_type_BYTEorWORD(LOCCTR, line_opreand, objectfile)
                else : # RESW loccor값만 처리함으로 따로 함수 x
                    LOCCTR_h = hex(LOCCTR)
                    LOCCTR_str = LOCCTR_h.split('0x')
                    objectfile.append([LOCCTR_str[1].upper().zfill(5), '000000', 'LDA'])

        for line in objectfile:
            print(line)


main()