'''
Sam Lee (hsl2113) - 11/6/14
W4119 - Programming Assignment 2 - Reliable file transfer
receiver.py - receiver program
'''
import sys, socket, struct, datetime

def main(argv):
	if len(sys.argv) != 6:
		print 'usage: python receiver.py <filename> <listening_port> <sender_ip> <sender_port> <log_filename>'
		sys.exit()		
	try:
		listening_port = int(sys.argv[2])
		sender_port = int(sys.argv[4])
	except ValueError:
		print '<remote_port> and <sender_port> must be ints'
		sys.exit()

	#print 'listening port : %d' % listening_port
	#print 'sender port: % d' % sender_port

	# get the hostname
	try:
		sender_ip = socket.gethostbyname(sys.argv[3])
	except socket.gaierror:
		print '\n hostname could not be resolved'

	# open the listening socket
	try: 
		listening_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		listening_socket.bind(('',listening_port))
	except:
		print 'Failed to create socket or bind failed'
		sys.exit()
	# try to open file to write
	try:
		file_to_write = open(sys.argv[1],'wb')
	except IOError:
		print 'unable to open file to write: %s' % argv[1]
		sys.exit()

	# try to open the logFile
	if (sys.argv[5] == 'stdout'):
		logFile = sys.stdout
	else:
		try:
			logFile = open(sys.argv[5], 'wb')
		except IOError:
			print 'unable to open logFile to write: %s' %arg[5]
	# create tcp socket for acks
	#HOST = ''
	#send_ack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# create the log column headers
	logHeader = 'Timestamp, Source Port, Destination Port, Seq #, ACK #, Flags\n'
	logFile.write(logHeader)
	
	seqTracker = 0
	prevAck = 0
	
	# main listening loop, receive packets from sender and parse them
	while True:
		data, addr = listening_socket.recvfrom(1024)
		header, buf = unpack_packet(data)
		check = check_checksum(header, buf)
		#print 'expecting packet %d' % seqTracker
		write_log(logFile, header)
		# if checksum is ok, packet is valid and continue
		if (check == True):
			# check for 'fin' flag, if so end the loop and close the files
			if header['flags'] == 2:
				write_log(logFile, header)
				if logFile != sys.stdout:
					logFile.close()
				file_to_write.close()
				break
			# make sure it is the packet we're expecting
			if header['seqNumber'] == seqTracker:
				ack = header['seqNumber']
				#print 'set the ack to %d' % ack
				file_to_write.write(buf)
				#print 'wrote packet # %d' % ack
				# make the packet with the ack number
				packet = make_packet(listening_port,sender_port,0,ack,1,'')
				#print 'made ack packet'
				#print '***************'
				#print sender_ip, sender_port, packet
				send_ack(packet,sender_ip,sender_port)
				#print 'sent ack packet'
				ackheader, tmp = unpack_packet(packet)
				write_log(logFile, ackheader)
				prevAck = seqTracker
				seqTracker += 1
				# continue to next loop iteration and listen
				continue
			else:
				# send previous ack packet again because it's corrupted
				packet = make_packet(listening_port, sender_port,0,prevAck,1,'')
				send_ack(packet,sender_ip,sender_port)		
				
	print 'Delivery completed successfully'		
		
# Function the write the receiver log
def write_log(logfile, header):
	entry = datetime.datetime.now().strftime('%H:%M:%S:%f')[:-2]
	entry +=', ' + str(header['sport'])
	entry +=', ' + str(header['dport'])
	entry +=', ' + str(header['seqNumber'])
	entry +=', ' + str(header['ackNumber'])
	if (header['flags'] == 1):
		entry +=', ackFlag set\n'
	elif (header['flags'] == 2):
		entry +=', finFlag set\n'
	else:
		entry +=', noFlags set\n'
	logfile.write(entry)

# Function to make sure the checksum is valid
def check_checksum(header, data):
	check = header['checksum']
	# blank out the checksum
	header['checksum'] = 0
	newheader = struct.pack('!HHLLBBHHH',header['sport'], header['dport'], header['seqNumber'], header['ackNumber'],header['data_offset'],header['flags'],header['window'],header['checksum'],header['urgent'])	
	# assemble the packet and get the checksum again to compare
	newpacket = newheader + data
	newchecksum = get_checksum(newpacket)
	if (socket.htons(check) == newchecksum):
		return True
	else:
		return False

# Function the send the ACK packe to sender
def send_ack(packet, serverIP, serverPort):
	HOST = ''
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((serverIP,serverPort))
	#print 'sent ack packet'
	sock.send(packet)
	sock.close()

# Function the unpack the packet and the header into a dict
def unpack_packet(packet):
	head = packet[0:20]
	header = {}
	header['sport'], header['dport'], header['seqNumber'], header['ackNumber'],header['data_offset'],header['flags'],header['window'],header['checksum'],header['urgent'] = struct.unpack('!HHLLBBHHH',head)	
	payload = packet[20:len(packet)]
	payload_size = len(payload)
	fmt = '%ds' % payload_size
	buf, = struct.unpack(fmt,payload)
	return header, buf 

# Function to assemble the packet, all the magic!
def make_packet(aport, rport, seqNumber, ackNumber, flag, data):
	# tcp headers
	source_port = aport
	destination_port = rport
	seq_number = seqNumber
	ack_number = ackNumber
	data_offset = 5
	if flag == 1:
		flag_ack = 1
		flag_fin = 0
	elif flag == 2:
		flag_fin = 1
		flag_ack = 0
	else:
		flag_ack = 0
		flag_fin = 0
	window = socket.htons(1)
	checksum = 0
	urgent = 0
	# fix the offset and assemble the flags
	offset = (data_offset << 4) + 0
	flags = flag_ack + (flag_fin << 1)

	# make the first header without the correct checksum
	header = struct.pack('!HHLLBBHHH', source_port, destination_port, seq_number, ack_number, offset, flags, window, checksum, urgent)
	packet = header + data
	checksum = get_checksum(packet)
	# make the header again with the correct checksum + add the size of the payload
	header = struct.pack('!HHLLBBH',source_port, destination_port, seq_number, ack_number, offset, flags, window) + struct.pack('H',checksum)  + struct.pack('!H',urgent)
	# add the data to the packet
	packet = header + data
	return packet

# Function the calculate the checksum 2 bits at a time and then the ones complement of the sum
def get_checksum(pack):
	tot = 0
	rem = len(pack) % 2
	for i in range(0, len(pack) - rem, 2):
		tot += ord(pack[i]) + (ord(pack[i+1]) << 8)
	if rem:
		tot += ord(pack[i+1])
	while (tot >> 16):
		tot = (tot & 0xffff) + (tot >> 16)
	tot = ~tot & 0xffff
	return tot

if __name__ == "__main__":
	main(sys.argv)