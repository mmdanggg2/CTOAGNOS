import os
import re

def reg2num(line):
    for i, arg in enumerate(line):  #for each of the parts
        if arg == 'a':              #change letter registers to numbers
            line[i] = '%r1'
        elif arg == 'b':
            line[i] = '%r2'
        elif arg == 'c':
            line[i] = '%r3'
        elif arg == 'x':
            line[i] = '%r4'
        elif arg == 'y':
            line[i] = '%r5'
        elif arg == 'z':
            line[i] = '%r6'
        elif arg == 'i':
            line[i] = '%r7'
        elif arg == 'j':
            line[i] = '%r8'
        elif arg == '[a]':
            line[i] = '[%r1]'
        elif arg == '[b]':
            line[i] = '[%r2]'
        elif arg == '[c]':
            line[i] = '[%r3]'
        elif arg == '[x]':
            line[i] = '[%r4]'
        elif arg == '[y]':
            line[i] = '[%r5]'
        elif arg == '[z]':
            line[i] = '[%r6]'
        elif arg == '[i]':
            line[i] = '[%r7]'
        elif arg == '[j]':
            line[i] = '[%r8]'

def processfile(infile, outfile):
    inputfile = open(infile)
    outputfile = open(outfile, "wt")
    for line in inputfile:
        if 'dat ' in line:              #If data, dont modify
            line = line.replace('dat', '.DAT')
            outputfile.write(line)
            continue
        
        line = line.replace('\n', '')   #remove new lines
        parts = line.split(";", 1)      #split code from comment
        code = parts[0]
        if len(parts) > 1:              #if there's a comment add ;
            comment = ";" + parts[1]
        else:
            comment = ""
        m = re.search("^[ \t]*", line)
        if m:
            indent = m.group()
        else:
            indent = ""
        if code == '':                  #if no code, write comment
            outputfile.write(comment + "\n")
            continue
        
        line = code.replace(',', '')    #remove commas
        line = line.split()             #split the line into a list of words
        if line == []:                  #If blank line just make a new line
            outputfile.write("\n")
            continue
        if line[0] == 'jsr':            #jsr is now CALL
            line[0] = 'CALL'
        elif line[0] == 'set':          #set is used alot, so it has its own section
            if line[1] == 'pc' and line[2] == 'pop':    #if its popping pc, thats a RET
                line = ['RET']
            elif line[1] == 'pc':       #if its setting pc, thats a JMP
                line[0] = 'JMP'         #change set to JMP
                line.pop(1)             #remove the pc
            elif line[1] == 'push':     #if its pushing a value
                line.pop(1)             #remove the push
                line[0] = 'PUSH'        #change set to PUSH
            elif line[2] == 'pop':      #if its popping a value
                line.pop(2)             #remove the pop
                line[0] = 'POP'         #change set to POP
            else:
                line[0] = 'MOV'         #change set to MOV
        elif line[0] == 'ife':          #ife is now IFEQ
            line[0] = 'IFEQ'
        elif line[0] == 'ifn':          #ifn is now IFNEQ
            line[0] = 'IFNEQ'
        elif line[0] == 'ifl':          #ifl is now IFL
            line[0] = 'IFL'
        elif line[0] == 'ifg':          #ifg doesn't exist to use IFL but swap the args
            line[0] = 'IFL'
            arg1 = line[1]
            arg2 = line[2]
            line[1] = arg2
            line[2] = arg1
        elif line[0] == 'bor':          #bor is now OR but requires 3 args so copy first
            line[0] = 'OR'
            line.append(line[2])
            line[2] = line[1]
        elif line[0] == 'add':          #add is now ADD but requires 3 args so copy first
            line[0] = 'ADD'
            line.append(line[2])
            line[2] = line[1]
        elif line[0] == 'sub':          #sub is now SUB but requires 3 args so copy first
            line[0] = 'SUB'
            line.append(line[2])
            line[2] = line[1]
        reg2num(line)
        finline = indent + line[0]
        if len(line) > 1:
            finline += " " + ", ".join(line[1:])
        if comment != '':
            finline += '    ' + comment
        if line[0] in ('hwn', 'hwi', 'hwq'):
            finline = '; ' + finline + ' ;!!!!!!!!!!GIMME ATTANTION NOW!!!!!!!!!!'
        outputfile.write(finline + "\n")
    inputfile.close()
    outputfile.close()

while True:
    ext = raw_input('Input file extension (def=.10c): ')
    if not ext:
        ext = '.10c'
    if not ext.startswith('.'):
        ext = '.' + ext
    
    extout = raw_input('Output file extension (def=.asm): ')
    if not extout:
        extout = '.asm'
    if not extout.startswith('.'):
        extout = '.' + extout
    if ext == extout:
        print 'Input and output extension can\'t be the same!'
        continue
    break

filecount = 0

for inname in os.listdir('.'):
    if inname.endswith(ext):
        print 'Processing ' + inname + '...',
        outname = inname.replace(ext, extout)
        filecount += 1
        processfile(inname, outname)
        print 'Done!'

if filecount == 0:
    print 'No ' + ext + ' files found!'
else:
    print filecount, 'files processed!'
