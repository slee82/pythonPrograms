'''
Sam Lee (hsl2113) - 10/2/14
W4119 - Programming Assignment 1 - Chat Server
client.py - client file
'''
import sys, socket, select

def main(argv):
	if len(sys.argv) != 3:
		print 'usage: python client.py <server_IP_address> <server_port_number>'
		sys.exit()
	try:
		port,host = [int(sys.argv[2]), (sys.argv[1])] 
	except ValueError:
		print address
		print sys.argv[2]
		print '<server host> and <server_port_number> must be ints'
		sys.exit()
	#debug info	
	#print "Got the port number! : %d" % port
	#print "Got the host! : %s" % host
	# attempt to resolve the hostname
	try:
		address = socket.gethostbyname(host)
	except socket.gaierror:
		print "\nHostname could not be resolved"
		sys.exit()
	# create the client socket
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, msg:
		print '\nFailed to create client socket. Error code: ' + str(msg[0]) + ', Error message: ' +msg[1]
		sys.exit()

	#print "Client Socket created"

	# connect to chat server
	try:
		client_socket.connect((address, port))
		print '\nConnected to chat server on ' + address + ":" + str(port)
	except socket.error, msg:
		print '\nCould not connect to chat server. Error code: ' + str(msg[0]) + ', Error message: ' + msg[1]
		sys.exit()

	# Main loop using select to await input from stdin(User) or socket(Server)
	while True:
		try:
			socket_list = [sys.stdin, client_socket]
			read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

			for sock in read_sockets:
				if sock == client_socket:
					data = sock.recv(4096)
					if not data:
						print '\n Disconnected from chat server'
						sock.close()
						sys.exit()
					else:
						sys.stdout.write(data)
						prompt()
				else:
					msg = sys.stdin.readline()
					client_socket.send(msg)
					prompt()
		#client_socket.close()
		except KeyboardInterrupt:
			print '\nCtrl - C detected client exiting'
			sock.close()
			sys.exit()
# function to make sure there is nothing in stdin
def prompt():
	sys.stdout.write('')
	sys.stdout.flush()

if __name__ == "__main__":
	main(sys.argv)