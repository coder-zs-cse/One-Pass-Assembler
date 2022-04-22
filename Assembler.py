from re import S


OPTAB = {'ADD': '18', 'COMP': '28', 'DIV': '24', 'J': '3C',
         'JEQ':'30', 'JGT': '34', 'JLT': '38', 'JSUB': '48', 
         'LDA': '00', 'LDCH': '50', 'LDL': '08', 'LDX': '04',
         'MUL': '20', 'OR': '44', 'RD': 'D8', 'RSUB': '4C', 
         'STA': '0C', 'STCH': '54', 'STL': '14', 'STSW': 'E8',
         'STX': '10', 'SUB': '1C', 'TD': 'E0', 'TIX': '2C', 'WD': 'DC'}

with open('input.txt', 'r') as file:
    data = file.readlines()
    
loc = data[0].split()[-1]

objCode = {}
labels = {}
forRef = {}

file = open("output.txt", 'w')


for line in data:
    words = line.split()
    if(words[0] == '.'):
        continue
    
    wline = "T^00" + loc + "^03"
    if len(words) == 3: # add label and address
        
        if words[0] in forRef:
            pass
        labels[words[0]] = str.upper(loc)
    
    if len(words) == 1: # for RSUB
        objCode[str.upper(loc)] = OPTAB[words[-1]] + '0000'
        wline += "^" + objCode[str.upper(loc)]
        loc = str(hex(int(loc, 16) + 3)[2:])
        continue
    
    # Handle the case of buffer and array lengths
    if words[-2] == 'START' or words[-2] == 'END':
        
        if words[-2] == 'START':
            # file.write("H^", words[-3])
            wline = 'H^'
            if(len(words[0])<6):
                wline += words[0] + (" ")*(6-len(words[0]))
                wline += "^00" + loc + "^"
                
            file.write(wline+"\n")
        
        if words[-2] == 'END':
            labels[words[-2]] = str.upper(loc)
        continue
    
    if words[-2] == 'RESW':
        size = int(words[-1])*3
        loc = str(hex(int(loc, 16) + size)[2:]) 
    
    elif words[-2] == 'RESB':
        size = int(words[-1])
        loc = str(hex(int(loc, 16) + size)[2:])
    
    elif words[-2] == 'BYTE':
        if words[-3] == 'EOF':
            objCode[str.upper(loc)] = '454F46'
            loc = str(hex(int(loc, 16) + 3)[2:])
        else:
            objCode[str.upper(loc)] = str.upper(words[-1][-3:-1])
            loc = str(hex(int(loc, 16) + 1)[2:])
    
    elif words[-2] != 'START':
        
        if words[-2] == 'WORD':
            objCode[str.upper(loc)] = str.upper('000000' + str(hex(int(words[-1])))[2:])[-6:]
    
        else:
            if ',' in words[-1]:
                if words[-1][:-2] in labels:
                    objCode[str.upper(loc)] = OPTAB[words[-2]] + str.upper(str(hex(int(labels[words[-1][:-2]], 16) + 32768))[2:])
                else:
                    if words[-1][:-2] in forRef:
                        forRef[words[-1][:-2]].append(str.upper(loc))
                    else:
                        forRef[words[-1][:-2]] = [str.upper(loc)]
                    objCode[str.upper(loc)] = OPTAB[words[-2]] + "8000"
                    
                
            elif words[-1] in labels:
                objCode[str.upper(loc)] = OPTAB[words[-2]] + labels[words[-1]]
                
            else:
                if words[-1] in forRef:
                    forRef[words[-1]].append(str.upper(loc))
                else:
                    forRef[words[-1]] = [str.upper(loc)]
                objCode[str.upper(loc)] = OPTAB[words[-2]] + '0000'
            
        
        loc = str(hex(int(loc, 16) + 3)[2:])
    
    file.write(wline+"\n")
        
# print(labels)
# print("Object Code: ", objCode)
# print("Forward References: ", forRef)

file.close()

for key, value in labels.items():
    print(key, value, sep=" ")

for key, value in objCode.items():
    print(key, value, sep=" ")
    
for key, value in forRef.items():
    print(key, value, sep=" ")