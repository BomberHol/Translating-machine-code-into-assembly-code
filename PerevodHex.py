import pandas as pd

def DefiningDictionaryMaskOperands(st):
    operands = {}
    if 'd' in st:
        operands['d'] = ''
    if 'r' in st:
        operands['r'] = ''
    if 'K' in st:
        operands['K'] = ''
    if 'k' in st:
        operands['k'] = ''
    if 'P' in st:
        operands['P'] = ''
    if 's' in st:
        operands['s'] = ''
    if 'b' in st:
        operands['b'] = ''
    if 'q' in st:
        operands['q'] = ''
    return operands



#определение и обаботка таблицы
tablFile = pd.read_excel('ASM.xlsx', usecols=['Команда', 'Код операции'])
tabl = []
for x in range(len(tablFile)):
    mask = tablFile['Код операции'][x]
    mask = str(mask).replace(' ', '')
    com = tablFile['Команда'][x]
    command = ''
    for i in str(com):
        if i != ' ':
            command += i
        else:
            break
    tabl.append([mask, command])


hexFile = open('HexCod.txt').readlines()
#обрабатываю файл убирая из строк все ненужные символы
hexCommands = []
for x in hexFile:
    strock = x.replace('\n', '').replace(':', '')
    hexCommands.append(strock[8:-2:])



#разделяю команды по байтам или по два байта
hexByteCommands = []
s = ''
for st in hexCommands:
    for i in range(len(st)):
        s += st[i]
        if len(s)%4 == 0 and len(s) != 8:
            s = s[2:4] + s[0:2]
        elif len(s)%8 == 0:
            s = s[0:4] + s[6:8] + s[4:6]

        if (len(s) == 4 and ('94' not in s[0:2]) and ('94' not in s[2:4])) or len(s) == 8:
            hexByteCommands.append(s)
            s = ''



#перевод Hex в Bin
binByteCommands = []
for comHex in hexByteCommands:
    com = int(comHex, 16)
    comBin = bin(com)[2:]
    if len(comHex) == 4 and len(comBin) < 16:
        comBin = (16 - len(comBin)) * '0' + comBin
    elif len(comHex) == 8 and len(comBin) < 32:
        comBin = (32 - len(comBin)) * '0' + comBin
    binByteCommands.append(comBin)



#нахожу для каждого байта команду и маску
binByteAndSpCommands = []
for binCommand in binByteCommands:
    #заполняю список возможными командами их масками
    spPerhapsCommands = []
    for maskAndCom in tabl:
        if len(maskAndCom[0]) != len(binCommand):
            continue
        flag = True
        for i in range(len(binCommand)):
            if maskAndCom[0][i] == '1' or maskAndCom[0][i] == '0':
                if maskAndCom[0][i] == binCommand[i]:
                    continue
                else:
                    flag = False
                    break
        if flag:
            spPerhapsCommands.append([maskAndCom[0], maskAndCom[1]])
    binByteAndSpCommands.append([binCommand, spPerhapsCommands])



#находим для каждого операнда свое значение
binByteAndSpMasksCommandsOperands = []
for indexBinByteAndSpCommands in binByteAndSpCommands:
    spMaskCommandOperand = []
    for indexSpCommands in indexBinByteAndSpCommands[1]:
        operand = DefiningDictionaryMaskOperands(indexSpCommands[0])
        for i in range(len(indexBinByteAndSpCommands[0])):
            for key in operand.keys():
                if indexSpCommands[0][i] == str(key):
                    operand[key] += indexBinByteAndSpCommands[0][i]
        for key in operand.keys():
            if key == 'd' or key == 'r':
                if indexSpCommands[1] == 'ldi' or indexSpCommands[1] == 'subi' or indexSpCommands[1] == 'sbci':
                    operand[key] = 'R' + str(int(operand[key], 2) + 16)
                else:
                    operand[key] = 'R' + str(int(operand[key], 2))

            if key == 'b' or key == 's':
                operand[key] = int(operand[key], 2)

            if key == 'K' or key == 'k' or key == 'P' or key == 'q':
                if indexSpCommands[1] == '*jmp' or indexSpCommands[1] == '*call':
                    operand[key] = int(operand[key] + '0', 2)
                    operand[key] = hex(operand[key])
                else:
                    operand[key] = int(operand[key], 2)
                    operand[key] = hex(operand[key])

        spMaskCommandOperand.append([indexSpCommands[0], indexSpCommands[1], operand])
    binByteAndSpMasksCommandsOperands.append([indexBinByteAndSpCommands[0], spMaskCommandOperand])




#обратно перевожу команды в Hex код
for i in range(len(binByteAndSpMasksCommandsOperands)):
    binByteAndSpMasksCommandsOperands[i][0] = hex(int(binByteAndSpMasksCommandsOperands[i][0], 2))[2::]
    if len(binByteAndSpMasksCommandsOperands[i][0]) == 4:
        binByteAndSpMasksCommandsOperands[i][0] = binByteAndSpMasksCommandsOperands[i][0][2:4] + binByteAndSpMasksCommandsOperands[i][0][0:2]
    if len(binByteAndSpMasksCommandsOperands[i][0]) == 8:
        binByteAndSpMasksCommandsOperands[i][0] = binByteAndSpMasksCommandsOperands[i][0][2:4] + binByteAndSpMasksCommandsOperands[i][0][0:2] + binByteAndSpMasksCommandsOperands[i][0][6:8] + binByteAndSpMasksCommandsOperands[i][0][4:6]

#Вывод ответа
with open('Answer2.txt', "w") as file:
    count = '0x0'
    for indexCommand in range(len(binByteAndSpMasksCommandsOperands)):
        file.write("\n")
        if len(binByteAndSpMasksCommandsOperands[indexCommand][1]) == 1:
            file.write(f'{count}: {binByteAndSpMasksCommandsOperands[indexCommand][0]} {binByteAndSpMasksCommandsOperands[indexCommand][1][0][1]} {binByteAndSpMasksCommandsOperands[indexCommand][1][0][2]}')
        else:
            file.write(f'{count}: {binByteAndSpMasksCommandsOperands[indexCommand][0]}')
            for indexMasksCommand in binByteAndSpMasksCommandsOperands[indexCommand][1]:
                file.write(f'            {indexMasksCommand[1]}, {indexMasksCommand[2]}')

        if len(binByteAndSpMasksCommandsOperands[indexCommand][0]) == 4:
            count = hex(int(count[2::], 16) + 2)
        elif len(binByteAndSpMasksCommandsOperands[indexCommand][0]) == 8:
            count = hex(int(count[2::], 16) + 4)



