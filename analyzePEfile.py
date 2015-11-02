#!/usr/bin/python

# Sam Lee
# Program used to analyze the PE section of an executable file in Windows
# using the pefile.py python module


import sys, pefile, datetime, peutils

DBFile = 'UserDB.TXT'   # Name of Packer signature file
BinDump = 'ResourceDump.bin'  # Name of file to dump the 1st resource binary

# I assume pefile, peutils, and UserDB.TXT are in the same directory as this script


def main(argv):
	if len(sys.argv) != 2:
		print 'usage: ./hw1.py PEfile'
		sys.exit()
	try:
		pe = pefile.PE(sys.argv[1])
	except pefile.PEFormatError:
		print "Error: Could not open PEfile"
		sys.exit()

	try:
		sig_db = peutils.SignatureDatabase(DBFile)
	except IOError:
		print "Error: Could not open Signature Database"


	print '---------------------------------------------'
	
	try:
		if (pe.is_dll()):
			print "File type: DLL"
		elif (pe.is_driver()):
			print "File type: SYS"
		elif (pe.is_exe()):
			print "File type: EXE"
		else:
			print "ERROR: File type could not be determined"
	except IOError:
		print "ERROR: File type could not be determined"
		sys.exit()

	num_dlls = 0
	num_functions = 0
	for entry in pe.DIRECTORY_ENTRY_IMPORT:
		num_dlls += 1
		for imp in entry.imports:
			num_functions += 1
	print 'Total number of imported DLLS: %d' % num_dlls
	print 'Total number of imported functions: %d' % num_functions
	print '---------------------------------------------'

	st = datetime.datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp).strftime('%Y-%m-%d %H:%M:%S')
	print 'Compile Time: ' + st
	print '---------------------------------------------'


	ePoint = pe.OPTIONAL_HEADER.AddressOfEntryPoint
	sec = pe.get_section_by_rva(ePoint)

	if ( not('.text' in str(sec.Name)) or ('.code' in str(sec.Name)) or ('CODE' in str(sec.Name)) or ('INIT' in str(sec.Name))):
		print 'ALERT: Entry code is not in a section with name .text, .code, CODE, or INIT'
		print '---------------------------------------------'
	
	check = sig_db.match_all(pe, ep_only = True)
	print "Packer: " + str(check)	
	print '---------------------------------------------'
	
	packAlert = ''
	for section in pe.sections:
		s_entropy = section.get_entropy()
		if s_entropy > 7.4:
   			packAlert =  ' *** ALERT: section is probably packed or compressed ***'
   		print 'Section: ' + str(section.Name) +'\tEntropy =  ' + str(s_entropy) + packAlert
   		packAlert = ''
   	print '---------------------------------------------'

   	for section in pe.sections:
   		if(section.SizeOfRawData == 0):
   			print "ALERT: " + str(section.Name) + " has a raw size of 0"
   			print '---------------------------------------------'
	

   	if (not pe.verify_checksum()):
   		print "Checksums do not match"
		print '---------------------------------------------'


	for section in pe.sections:
		if('.rsrc' in section.Name):
			entry = pe.DIRECTORY_ENTRY_RESOURCE.entries[0].directory.entries[0]
			entSize = entry.directory.entries[0].data.struct.Size
			entOffSet = entry.directory.entries[0].data.struct.OffsetToData
			dump = pe.get_data(entOffSet,entSize)
			file_to_write = open(BinDump,'wb')
			file_to_write.write(dump)
			file_to_write.close
			print 'Dumped the first resource to file: resourceDump.bin'
			print '---------------------------------------------'

	print "ALL DONE"


	#print pe.parse_resources_directory(pe.get_section_by_rva())

	#for section in pe.sections:
	#	if('.rsrc' in section.Name):
	#		print section.get_data(section.PointerToRawData, section.SizeOfRawData
	

	#for section in pe.sections:
	#	if ('.rsrc' in section.Name):
	#		print section.dump()

if __name__ == "__main__":
	main(sys.argv)