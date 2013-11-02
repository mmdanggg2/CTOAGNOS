import os

def reg2num(line):
	for i, arg in enumerate(line):	#for each of the parts
		if arg == 'a':				#change letter registers to numbers
			line[i] = '%r1'
		if arg == 'b':
			line[i] = '%r2'
		if arg == 'c':
			line[i] = '%r3'
		if arg == 'x':
			line[i] = '%r4'
		if arg == 'y':
			line[i] = '%r5'
		if arg == 'z':
			line[i] = '%r6'
		if arg == 'i':
			line[i] = '%r7'
		if arg == 'j':
			line[i] = '%r8'
		if arg == '[a]':
			line[i] = '[%r1]'
		if arg == '[b]':
			line[i] = '[%r2]'
		if arg == '[c]':
			line[i] = '[%r3]'
		if arg == '[x]':
			line[i] = '[%r4]'
		if arg == '[y]':
			line[i] = '[%r5]'
		if arg == '[z]':
			line[i] = '[%r6]'
		if arg == '[i]':
			line[i] = '[%r7]'
		if arg == '[j]':
			line[i] = '[%r8]'

inputfile = open("BIOS.10c")
outputfile = open("BIOS.asm", "wt")
for line in inputfile:
	if 'dat ' in line:				#If data, dont modify
		line = line.replace('dat', '.DAT')
		outputfile.write(line)
		continue
	line = line.replace(',', '')	#remove commas
	line = line.split()				#split the line into a list of words
	if line == []:					#If blank line make it so it dont crash
		line = ['']
	if line[0] == 'jsr':			#jsr is now CALL
		line[0] = 'CALL'
	if line[0] == 'set':			#set is used alot, so it has its own section
		if line[1] == 'pc' and line[2] == 'pop':	#if its popping pc, thats a RET
			line = ['RET']
		elif line[1] == 'pc':		#if its setting pc, thats a JMP
			line[0] = 'JMP'			#change set to JMP
			line.pop(1)				#remove the pc
		elif line[1] == 'push':		#if its pushing a value
			line.pop(1)				#remove the push
			line[0] = 'PUSH'		#change set to PUSH
		elif line[2] == 'pop':		#if its popping a value
			line.pop(2)				#remove the pop
			line[0] = 'POP'			#change set to POP
		else:
			line[0] = 'MOV'			#change set to MOV
			
	if line[0] == 'ife':			#ife is now IFEQ
		line[0] = 'IFEQ'
	if line[0] == 'ifn':			#ifn is now IFNEQ
		line[0] = 'IFNEQ'
	if line[0] == 'ifl':			#ifl is now IFL
		line[0] = 'IFL'
	if line[0] == 'ifg':			#ifg doesn't exist to use IFL but swap the args
		line[0] = 'IFL'
		arg1 = line[1]
		arg2 = line[2]
		line[1] = arg2
		line[2] = arg1
	if line[0] == 'bor':			#bor is now OR but requires 3 args so copy first
		line[0] = 'OR'
		line.append(line[2])
		line[2] = line[1]
	if line[0] == 'add':			#add is now ADD but requires 3 args so copy first
		line[0] = 'ADD'
		line.append(line[2])
		line[2] = line[1]
	if line[0] == 'sub':			#sub is now SUB but requires 3 args so copy first
		line[0] = 'SUB'
		line.append(line[2])
		line[2] = line[1]
	reg2num(line)
	finline = line[0]				#combine the list
	if len(line) >= 2:
		finline += ' ' + line[1]
	if len(line) >= 3:
		finline += ', ' + line[2]
	if len(line) >= 4:
		finline += ', ' + line[3]
	if line[0] == 'hwn' or line[0] == 'hwi' or line[0] == 'hwq':
		finline += ' ;!!!!!!!!!!GIMME ATTANTION NOW!!!!!!!!!!'
	finline += '\n'
	outputfile.write(finline)
inputfile.close()
outputfile.close()