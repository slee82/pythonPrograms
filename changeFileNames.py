#!/usr/bin/python

import os, sys
import shutil

if len(sys.argv) != 2  :
	print 'usage: names.py formNumber'
	sys.exit()

formNumber = sys.argv[1]
cur = os.getcwd()
new = ''
top = cur + '/form_' + str(formNumber) +'/'
new = top +'fixed' + '/'
print new
os.mkdir(new)
fileLocation = top + 'files/'
os.chdir(fileLocation)

# remove spaces from file names
for badfiles in os.listdir("."):
	f = badfiles.split()
	output = ''
	output = output.join(f)
	os.rename(badfiles,output)

# rename the files appropriately
for filename in os.listdir('.'):
	singles = filename.split('-')
	if len(singles) == 3:
		output = singles[2]
		dst =  new  + output
		src = fileLocation + filename
		shutil.copyfile(src, dst)
	elif len(singles) > 3:
		output = ''
		output = output.join(singles[2:])
		dst = new + output
		src = fileLocation + filename
		shutil.copyfile(src, dst)
	elif len(singles) > 1:
		output = ''
		output = output.join(singles[1:])
		dst = new + output
		src = fileLocation + filename
		shutil.copyfile(src, dst)
	else:
		output = ''
		output = output.join(singles[0:])
		dst = new + output
		src = fileLocation + filename
		shutil.copyfile(src,dst)

# remove the tmp file extension
os.chdir(new)
for f in os.listdir('.'):
	fixed = f.split('.')
	if (fixed[len(fixed) - 1] == 'tmp'):
		output = ''.join(fixed[:len(fixed) - 2])
		ext = fixed[len(fixed)-2]
		output = output + '.' + ext  
		os.rename(f,output)

		
print "done"

