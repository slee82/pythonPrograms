Sam Lee - hsl2113 - Programming Assignment 2 
README 

----------------- Description -------------------------------
1. (a)My sender.py file handles the sending of the files. The MSS is set to 576, since the “TCP” header takes 20 bytes, it essentially breaks up the files into 556 byte chunks. The window size is hard coded and set to 1, I did not implement a variable window size. No matter what number you enter for the window size it will always be 1. Sender.py opens 2 files, the file to be transferred and the log file or stdout, if the file to be transferred is not found it exits with an IOException. Opens the TCP ACK socket and starts sending UDP sockets to the receiver. Read the file into ‘i’ chunks, and then send ‘j’ packets matching ‘i’. Calculate the RTT stats based on the sample RTTs collected. Lastly send the ‘fin’ packet so that the receiver knows no more packets are coming, and close all files and sockets.
    (b)My receiver.py file handles the receipt of all the files. Sets the sockets where it will be listening for the UDP. Get the IP address of the sender, and open the file to write the transferred file and also the log file or stdout. Enter the main receiving loop, and start receiving from the sender on the listening port. Get the packets, unpack them, if it’s the correct one we expect, send the ack, and log it. Otherwise, send the previous ack again. Once the packet with ‘fin’ flag set is received, close the files.

****** sender.py ********
# Main server loop
	# 1. Check the arguments, and open the files to log and to send
	# 2. Read the file and slice it up into the MSS-20 bytes
	# 3. Assemble the packet, tcp header + chunk, and send to receiver
	# 4. Wait for ACK or retransmit
	# 5. Calculate ERTT, devRTT, and TimeOut stats
	# 6. Send the packet with ‘fin’ flag set so that the receiver.py knows the transfer is over
	# 7. Print the final stats
write_log() - helper function to write the sender log, takes a file object, the packet header, and an estimated RTT
wait_for_ack() - function to wait for ack from receiver via TCP. Return the ACK number or timeout so that you can retransmit
unpack_packet() - split the packet header from the data, put the header into a dictionary
make_packet() - put all of the values of the header using the struct.pack function and the add the data to the packet
get_checksum() - get the checksum from the packet

****** receiver.py ******
# Main server loop
	# 1. Check the arguments, open the files to log and to write
	# 2. Wait for packets to come in, and start writing the file if the packet is in order.
	# 3. If the packet is out of order, send the previous ack
	# 4. Once the ‘fin’ packet is received close the log and received file
write_log() - same as the sender write_log() except without the RTT stat
check_checksum() - unpack the packet and do a checksum, if it matches the original checksum return True, False otherwise
send_ack() - send the ack packet to the sender
make_packet() - same as the one in the sender.py
get_checksum() - same as the checksum from sender.py


----------------- Development Environment --------------------
OS:  	MAC OS 10.10
python: 2.7.5
IDE:	Sublime Text 

----------------- How to Run Code ----------------------------
3. Instructions on how to run the files are included when you run the files, but for the server please run it by typing 

***** receiver.py ******
usage: python receiver.py <filename> <listening_port> <sender_ip> <sender_port> <log_filename>
***** sender.py ******
usage: python sender.py <filename> <remote_ip> <remote_port> <ack_port_num> <log_filename> <window_size_default is 1>

Sample run:
python sender.py test.JPG localhost 4199 5000 stdout 1
python receiver.py file_received 4199 localhost 5000 log


----------------- Additional Features ------------------------
4. I did not implement any additional functionalities
