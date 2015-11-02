'''
Sam Lee (hsl2113) - 11/6/14
W4119 - Programming Assignment 2 - Reliable file transfer
sender.py - sender program
'''
import sys, socket, struct, math, datetime

# Maximum Segment Size
MSS = 576
def main(argv):
	if len(sys.argv) != 7:
		print 'usage: python sender.py <filename> <remote_ip> <remote_port> <ack_port_num> <log_filename> <window_size_default is 1>'
		sys.exit()		
	try:
		remote_port = int(sys.argv[3])
		ack_port = int(sys.argv[4])
		window_size = int(sys.argv[6])
	except ValueError:
		print '<remote_port>, <ack_port_num, and <window_size> must be ints'
		sys.exit()

	#print 'port number : %d' % remote_port
	#print 'ack port: % d' % ack_port
	#print 'window_size: %d' % window_size
	
	# get the hostname
	try:
		remote_ip = socket.gethostbyname(sys.argv[2])
	except socket.gaierror:
		print '\n hostname could not be resolved'
		sys.exit()

	# try to open file to send
	chunk = {}
	try:
		with open(sys.argv[1], 'rb') as file_to_send:
			i = 0
			chunk[i] = file_to_send.read(MSS-20)
			while chunk[i] != '':
				i += 1
				chunk[i] = file_to_send.read(MSS-20)
	except IOError:
		print 'unable to open file: %s' % argv[1]
		sys.exit()

	# open logFile
	if (sys.argv[5] == 'stdout'):
		logFile = sys.stdout
	else:
		try:
			logFile = open(sys.argv[5], 'wb')
		except IOError:
			print 'unable to open logFile to write: %s' %arg[5]

	# create the log column headers
	logHeader = 'Timestamp, Source Port, Destination Port, Seq #, ACK #, Flags, Estimated RTT in seconds\n'
	logFile.write(logHeader)

	# make sender UDP socket
	try:
		sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except:
		print 'failed to create sender socket'

	# make ack TCP socket
	HOST = ''
	ack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		ack_socket.bind((HOST,ack_port))
	except socket.error, msg:
		print '\nBind failed for ack_port. Error Code: ' +str(msg[0]) + ' Message: '+msg[1]
		sys.exit()

	# Assemble packets and send!
	j = 0
	totalBytes = 0
	retransmit = 0
	segmentsSent = 0
	estimatedRTT = 0.0
	timeSent = 0
	timeReceived = 0
	timeOut = 1
	devRTT = 0
	# start with packet 0 and go until the total number of chunks i
	while (j < i):
		packet = make_packet(ack_port, remote_port, j, 0 , 0, chunk[j])
		sender_socket.sendto(packet, (remote_ip, remote_port))
		timeSent = float(datetime.datetime.now().strftime('%S.%f')[:-2])
		segmentsSent += 1
		head, tmp = unpack_packet(packet)
		write_log(logFile, head, estimatedRTT)
		totalBytes += len(chunk[j])
		
		# wait for ack or timeout
		answer = wait_for_ack(ack_socket,timeOut, logFile, estimatedRTT)
		# calculate RTT stats
		timeReceived = float(datetime.datetime.now().strftime('%S.%f')[:-2])
		estimatedRTT = (0.875*estimatedRTT) + 0.125*(timeReceived-timeSent)
		devRTT = (.75*devRTT) + (.25*abs((timeReceived-timeSent) - estimatedRTT))
		timeOut = estimatedRTT + (4 * devRTT)
		#If expect ack number continue to the next packet else, retransmit
		if answer == j:
			j += 1
			continue
		else:
			j = j
			retransmit += 1 
		#if ack, send next chunk

		
	# out of the loop, send fin packet
	packet = make_packet(ack_port, remote_port, j, 0, 2, '')
	sender_socket.sendto(packet,(remote_ip, remote_port))
	segmentsSent += 1
	head, tmp = unpack_packet(packet)
	write_log(logFile, head, estimatedRTT)
	# close logFile
	if logFile != sys.stdout:
		logFile.close()
	# close the ack_socket
	ack_socket.close()
	print 'Delivery completed successfully'
	print 'Total Bytes Sent = %d' % totalBytes
	print 'Segments Sent = %d' % segmentsSent
	print 'Segments Retransmitted = %d' % retransmit

# Function to write the log
def write_log(logfile, header, ertt):
	entry = datetime.datetime.now().strftime('%H:%M:%S:%f')[:-2]
	entry +=', ' + str(header['sport'])
	entry +=', ' + str(header['dport'])
	entry +=', ' + str(header['seqNumber'])
	entry +=', ' + str(header['ackNumber'])
	if (header['flags'] == 1):
		entry +=', ackFlag set'
	elif (header['flags'] == 2):
		entry +=', finFlag set'
	else:
		entry +=', noFlags set'
	entry +=', ERTT %f\n' % ertt 
	logfile.write(entry)

# Function to wait for ack or timeout
def wait_for_ack(sock, timeout, logFile, rtt):
	try:
		sock.settimeout(timeout)
		sock.listen(10)
		conn,addr = sock.accept()
		answer = conn.recv(1024)
		header, data = unpack_packet(answer)
		write_log(logFile, header, rtt)
		#print 'got ackNumber #%d' % header['ackNumber']
		return header['ackNumber']
	except:
		timedout = ''
		#print 'no ack, timedout!'
		return timedout

# Function the unpack the packet and put the header in a dict
def unpack_packet(packet):
	head = packet[0:20]
	header = {}
	header['sport'], header['dport'], header['seqNumber'], header['ackNumber'],header['data_offset'],header['flags'],header['window'],header['checksum'],header['urgent'] = struct.unpack('!HHLLBBHHH',head)	
	payload = packet[20:len(packet)]
	payload_size = len(payload)
	fmt = '%ds' % payload_size
	buf, = struct.unpack(fmt,payload)
	return header, buf 

# Function to make the packet, all the magic
def make_packet(aport, rport, seqNumber, ackNumber, flag, data):
	# tcp headers
	source_port = aport
	destination_port = rport
	seq_number = seqNumber
	ack_number = ackNumber
	data_offset = 5
	# set the flag bits accordingly
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


# Function to figure out the checksum 2 bits at a time and the ones complement of the sum
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

