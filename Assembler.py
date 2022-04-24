import sys
from OpTable import OPTAB 
# OPTAB - Opcode Table

def TR_size(curr):
    '''
    Function to return the size of the passed Text Record
    
    cur - Current Text Record of the form -> "T^00ABCD^^00xxxx^00yyyy^"
    
    Length = (len(cur) - (len("T") + len("00ABCD") + count("^")))//2
    (Length is divided by 2 because a 6 bit object code is of the size 3 bytes)
    '''
    return (len(curr)-7-curr.count("^"))//2

def init_current(addr):
    '''
    Function to initialize the current Text Record starting from the current loc
    
    addr - Current Location
    
    Text record initialised as -> "T^00addr^"
    '''
    return "T^00"+addr+"^" 
    
def final_current(curr):
    '''
    Function to finalise the current Text Record by inserting its length and returns the final Text Record
    
    curr - current Text Record
    
    length -> Hex(TR_size(curr)) in 2 bits
    After Insertion, TE -> "T^00ABCD^xx^00yyyy^...."
    '''
    length = str(hex(TR_size(curr)))[2:].zfill(2).upper()
    return curr[:9] + length + curr[9:] + "\n" # newline to write in file

def update_loc(loc, n, bytes):
    '''
    Function to update the current location value with the passed parameters and return the loc value
    
    loc - Current Location
    n - No. of words
    bytes - Size of each word
    
    Current address is converted back to int from hex, size is added, then converted back to hex and returned
    '''
    size = int(n)*bytes
    return str(hex(int(loc, 16) + size)[2:]).upper()

def add_to_forRef(fR, key, addr):
    '''
    Function to add/append a Forward Reference to the forRef dictionary and return the dictionary
    
    fR - Forward Reference Dictionary
    key - Name of the Forward Reference
    addr - Address corresponding to the Forward Reference
    
    if key is in fR, then addr is appended to the existing list,
    else create a new list with the passed key
    
    Address stored in list will be 1 more than the addr passed (to make for the OPCODE)
    '''
    if key in fR:
        fR[key].append(str(hex(int(addr,16)+1))[2:].upper())
    else:
        fR[key] = [str(hex(int(addr,16)+1))[2:].upper()]
    
    return fR
 
def write_to_file(curr, f):
    '''
    Function to write a Text Record to file
    
    curr - Text Record
    f - File Pointer in write/write+ mode
    '''
    if TR_size(curr) != 0: # make sure to not write an empty Text Record
        f.write(final_current(curr)) 

if __name__ == "__main__": # main method
    
    if(len(sys.argv) < 2): # name of input file needs to be mentioned as a command line argument
        print("Enter filename as command line argument.")
        exit() 
        
    with open(sys.argv[1], 'r') as file:
        data = file.readlines() # the input file lines read and stored in a list
        
    loc = data[0].split()[-1].upper() # starting address stored
    start  = loc
        
    labels = {} # dictionary for storing Labels
    forRef = {} # dictionary for storing Forward References
    current = "" # for current Text Record

    file = open("output.txt", 'w+') # open a file in write+ mode

    for line in data: 
        words = line.split() # split each line of input into list of words
        if(words[0] == '.'): 
            continue # comment in the input file, ignore line
        
        if len(words) > 1 and words[-2] not in ['RESW', 'RESB'] and current == "": 
            # if Operand is not RESW or RESB, and Text Record is currently null, then initialize Text Record with the the current location
            current = init_current(loc)
            
        if len(words) == 3: # line with a label
            
            if words[0] in forRef.keys(): # if a Forward Reference is caught
                write_to_file(current, file) # write the current text record, 
                for objc in forRef[words[0]]: # write all forwards references as Text Records to file
                    current = init_current(objc) + "02^" + loc
                    file.write(current + "\n")
                    
                del forRef[words[0]] # delete the Forward Reference from the dictionary
                current = init_current(loc) # initialize 

            labels[words[0]] = loc
        
        if len(words) == 1: # for RSUB
            if TR_size(current) + 3 > 30: # size checking of Text Record
                write_to_file(current, file) 
                current = init_current(loc) 
                
            current += "^" + OPTAB[words[-1]] + '0000' # append to text record
            loc = update_loc(loc, 1, 3) # update loc
            continue
        
        # Handle the case of buffer and array lengths
        if words[-2] in ['START', 'END']:
            
            if words[-2] == 'START':
                current = 'H^' + words[0][:6]
                if(len(words[0])<6):
                    current += (" ")*(6-len(words[0]))
                current += ("^00" + loc)*2
                    
                file.write(current + "\n")
                current = ""
            
            else:
                labels[words[-2]] = loc
                write_to_file(current, file)
                current = "E^00" + labels[words[-1]] + "\n"
                file.write(current)
        
        elif words[-2] in ["RESW", "RESB"]:
            if current != "":
                write_to_file(current, file)
                current = ""
                
            if words[-2] == 'RESW':
                loc = update_loc(loc, words[-1], 3) 
            else: 
                loc = update_loc(loc, words[-1], 1)
                    
        elif words[-2] == 'BYTE':
            if words[-1][0]=='C':
                if TR_size(current) + 3 > 30:
                    write_to_file(current, file)
                    current = init_current(loc)
                        
                current += "^" + (''.join([hex(ord(x))[2:] for x in words[-1][2:-1]]).upper() + "000000")[:6]    # generate Object code from the the ASCII equivalent of the character
                loc = update_loc(loc, 1, 3)  
                
            else:
                if TR_size(current) + 1 > 30:
                    write_to_file(current, file)
                    current = init_current(loc)
                        
                current += "^" + words[-1][2:-1].upper()
                loc = update_loc(loc, 1, 1)
        
        else:
            if TR_size(current) + 3 > 30:
                write_to_file(current, file)            
                current = init_current(loc)
            
            if words[-2] == 'WORD':
                current += "^" + str(hex(int(words[-1])))[2:].zfill(6)    
            else:
                if ',' in words[-1]:
                    if words[-1][:-2] in labels:
                        current += '^' + OPTAB[words[-2]] + hex(int(labels[words[-1][:-2]],16) | int("8000",16))[2:].zfill(4).upper()
                    else:
                        forRef = add_to_forRef(forRef, words[-1][:-2], loc)
                        current += "^" + OPTAB[words[-2]] + "8000"   

                elif words[-1] in labels:
                    current += '^' + OPTAB[words[-2]] + hex(int(labels[words[-1]],16) & int("7FFF",16))[2:].zfill(4).upper()    
                    
                else:
                    forRef = add_to_forRef(forRef, words[-1], loc)
                    current += "^" + OPTAB[words[-2]] + '0000'    
                
            loc = update_loc(loc, 1, 3)

    end = loc
    file.seek(0)
    file.seek((file.readline()).rindex("^")+1)
    current = str(hex(int(end,16) - int(start,16)))[2:].upper().zfill(6)

    file.write(current)
    file.close()
