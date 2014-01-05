import os
import sys
import re
import collections

sysprint = sys.stdout.write

regmap = {"a":"%r1", "b":"%r2", "c":"%r3", "x":"%r4",
		"y":"%r5" ,"z":"%r6", "i":"%r7", "j":"%r8"}


# regex to break line into regions
rx1 = ("(?:\\s*:([^\\s;]+))?"   # possible label
	+ "(\\s*)"                  # indentation
	+ "([^;]*)"                 # code (up until ;)
	+ "(.*)"                    # comment
)
			
def ramaccess(arg1, arg2):
	if arg1.startswith("[") and arg1.endswith("]"):
		arg1 = arg1.replace('[','')
		arg1 = arg1.replace(']','')
		preline = 'LOAD %r10, ' + arg1
		postline = 'STORE ' + arg1 + ', %r10'
		arg1 = '%r10%'
		return preline, postline
	elif '[' and ']' in arg2:
		arg2 = '%r11'


def splitLine(line):
	try:
		m1 = re.match(rx1, line)
		if not m1:
			raise Exception("Can't parse line: " + repr(line))
		label, indent, code, comment = m1.groups()
		if code:
			parts = code.split(None, 1)
			opcode = parts[0]
			args = arg1 = arg2 = ""
			if len(parts) > 1:
				args = parts[1].split(",")
				arg1 = args[0].strip()
				if len(args) > 1:
					arg2 = args[1].strip()
			if arg1:
				if arg1.startswith("[") and arg1.endswith("]") and regmap.get(arg1[1:-1]):
					arg1 = '[' + regmap.get(arg1[1:-1], arg1) + ']'
				else:
					arg1 = regmap.get(arg1, arg1)
			if arg2:
				if arg2.startswith("[") and arg2.endswith("]") and regmap.get(arg2[1:-1]):
					arg2 = '[' + regmap.get(arg2[1:-1], arg2) + ']'
				else:
					arg2 = regmap.get(arg2, arg2)
		else:
			opcode = arg1 = arg2 = ''
		if label == None:
			label = ''
		if comment == None:
			comment = ''
		return label, indent, opcode, arg1, arg2, comment
	except:
		return label, indent, 'SPLIT_ERR', '', '', comment



def processfile(infile, outfile):
	inputfile = open(infile)
	outputfile = open(outfile, "wt")
	global linenum
	linenum = 0
	for line in inputfile:
		
		linenum += 1
		for i in range(len(str(linenum-1))+1):
			sysprint('\b')
		sysprint(str(linenum) + ' ')
		
		if 'dat ' in line:              #If data, dont modify
			if ':' in line[:1]:				#Fix labels
				line = line[1:]
				line = line.split(None,1)
				line[0] = line[0] + ':'
				line = ' '.join(line)
			line = line.replace('dat', '        .DAT')
			outputfile.write(line)
			continue
		
		arg3 = ''
		label, indent, opcode, arg1, arg2, comment = splitLine(line)
		#print splitLine(line), '\n'
		code = ''
		prelines = collections.OrderedDict()
		postlines = collections.OrderedDict()

		
		if opcode == 'SPLIT_ERR':
			sysprint(' Error Parsing line!\n')
			continue
		if opcode:
			pren = 1
			postn = 1
			#~ if arg1:
				#~ if arg1.startswith("[") and arg1.endswith("]") and not 'set' in opcode:
					#~ if 
					#~ arg1 = arg1[1:-1]
					#~ prelines['pre'+str(pren)] = 'LOAD %r10, ' + arg1
					#~ pren += 1
					#~ postlines['post'+str(postn)] = 'STORE ' + arg1 + ', %r10'
					#~ postn += 1
					#~ arg1 = '%r10%'
			#~ if arg2:
				#~ if arg2.startswith('[') and arg2.endswith(']') and not 'set' in opcode:
					#~ arg2 = arg2[1:-1:]
					#~ prelines['pre'+str(pren)] = 'LOAD %r11, ' + arg1
					#~ pren += 1
					#~ postlines['post'+str(postn)] = 'STORE ' + arg1 + ', %r11'
					#~ postn += 1
					#~ arg1 = '%r11%'
			
			if opcode == 'jsr':            #jsr is now CALL
				opcode = 'CALL'
			elif opcode == 'set':          #set is used alot, so it has its own section
				if arg1 == 'pc' and arg2 == 'pop':    #if its popping pc, thats a RET
					opcode = 'RET'
					arg1 = arg2 = ''
				elif arg1 == 'pc':       #if its setting pc, thats a JMP
					opcode = 'JMP'         #change set to JMP
					arg1 = arg2             #remove the pc
					arg2 = ''
				elif arg1 == 'push':     #if its pushing a value
					arg1 = arg2             #remove the push
					arg2 = ''
					opcode = 'PUSH'        #change set to PUSH
				elif arg2 == 'pop':      #if its popping a value
					arg2 = ''            #remove the pop
					opcode = 'POP'         #change set to POP
				else:
					if arg1.startswith('[') and arg1.endswith(']'):
						opcode = 'STORE'
						arg1 = arg1[1:-1]
					elif arg2.startswith('[') and arg2.endswith(']'):
						opcode = 'LOAD'
						arg2 = arg2[1:-1]
					else:
						opcode = 'MOV'         #change set to MOV
			elif opcode == 'ife':          #ife is now IFEQ
				opcode = 'IFEQ'
			elif opcode == 'ifn':          #ifn is now IFNEQ
				opcode = 'IFNEQ'
			elif opcode == 'ifl':          #ifl is now IFL
				opcode = 'IFL'
			elif opcode == 'ifg':          #ifg doesn't exist so use IFL but swap the args
				opcode = 'IFL'
				arg1, arg2 = arg2, arg1
			elif opcode == 'bor':          #bor is now OR but requires 3 args so copy first
				opcode = 'OR'
				arg1, arg2, arg3 = arg1, arg1, arg2
			elif opcode == 'add':          #add is now ADD but requires 3 args so copy first
				opcode = 'ADD'
				arg1, arg2, arg3 = arg1, arg1, arg2
			elif opcode == 'sub':          #sub is now SUB but requires 3 args so copy first
				opcode = 'SUB'
				arg1, arg2, arg3 = arg1, arg1, arg2
			if arg1:
				if arg2:
					if arg3:
						code = '%s %s, %s, %s' % (opcode, arg1, arg2, arg3)
					else:
						code = '%s %s, %s' % (opcode, arg1, arg2)
				else:
					code = '%s %s' % (opcode, arg1)
			else:
				code = opcode
		else:
			code = ''
		indent += '        '
		
		codelines = collections.OrderedDict()
		for name in prelines:
			code = prelines[name]
			codelines[name] = code
		codelines['code'] = code
		for name in postlines:
			code = postlines[name]
			codelines[name] = code
		outlines = []
		for lname in codelines:
			code = codelines[lname]
			#print lname, ':', code
			if lname == 'pre1' and label:    #first line gets label
				outlines.append(label + ': ' + indent + code)
				indent += " " * (len(label) + 2)
			if lname == 'code':	# code gets the comment
				if code:
					if not 'pre1' in codelines and label:    #if there isnt prelines label goes on code
						outlines.append(label + ": " + indent + code + ' ' + comment)
						indent += " " * (len(label) + 2)
					else:
						outlines.append(indent + code)
				elif label:
					outlines.append((label + ': ' + comment).strip())
				else:
					outlines.append(comment)
			else:	# subsequent lines
				outlines.append(indent + code)
		
		#print outlines
		for line in outlines:
			line = line.replace('\n', '')
			outputfile.write(line + '\n')
		
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
	if inname.endswith('BIOS.10c'):
		print 'Processing ' + inname + '...   ',
		outname = inname.replace(ext, extout)
		filecount += 1
		processfile(inname, outname)
		print 'Done!'

if filecount == 0:
	print 'No ' + ext + ' files found!'
else:
	print filecount, 'files processed!'
