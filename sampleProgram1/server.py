'''
Sam Lee (hsl2113) - 10/2/14
W4119 - Programming Assignment 1 - Chat Server
server.py - server file
'''
import sys, socket, signal, datetime, thread, select

#LAST_HOUR is defined in unit minutes
LAST_HOUR = 60
#TIME_OUT is definited in unit minutes
TIME_OUT = 30
#BLOCK_TIME is definited in unit seconds
BLOCK_TIME = 60

one_hour = datetime.timedelta(minutes=LAST_HOUR)
thirty_min = datetime.timedelta(minutes=TIME_OUT)
one_min = datetime.timedelta(seconds=BLOCK_TIME)

def main(argv):
	if len(sys.argv) != 2:
		print 'usage: python server.py <port number>'
		sys.exit()
	try:
		port = int(sys.argv[1])
	except ValueError:
		print '<port number> must be an int'
		sys.exit()
		
	#print "Got the port number! : %d" % port
	#print "trying to read_password_file"
	
	loginPasswords = read_password_file("user_pass.txt")

	#print "Sending port number to createSocket"
	serverSocket = create_socket(port)

	#serverSocket.setblocking(False)
	serverSocket.listen(10)
	print "Server listening on port %d.... Press Ctrl - C to quit" % port

	# Main server loop
	# 1. Listen and accept connections from clients
	# 2. Check the password for the user using check_password function
	# 3. If successful launch a new thread with the handle_client function
	# 4. If authentication is not successful then close the connection
	# 5. Error handling, ctrl - c
	while True:
		try:
			conn, addr = serverSocket.accept()
			print 'Connected to ' + addr[0] + ':' + str(addr[1])
			try:
				user, loginPasswords = check_password(conn,loginPasswords) 
				if user not in loginPasswords or loginPasswords[user][6] == 'BLOCKED':
					print addr[0] + ':' + str(addr[1]) + ' disconnected\n'
				elif user in loginPasswords and loginPasswords[user][6] == '':
					thread.start_new_thread(handle_clients,(user, loginPasswords))
				else:
					conn.close()
					print addr[0] + ':' + str(addr[1]) + ' disconnected\n'
			except socket.error:
				print '\n Ctrl - c User quit'
		except KeyboardInterrupt:
			print '\nCtrl - C detected, server shutting down...'
			serverSocket.close()
			sys.exit()

# open the file to read the username and passwords and store them in the main
# dicitionary file used to store everything
def read_password_file(filename):
	passwords = {}
	try:
		with open(filename) as f:
			for line in f:
				line = line.rstrip()
				divline = line.split(' ')
				user = divline[0]
				userAtrribs = [divline[1],'',"offline",'','','','']
				passwords[user] = userAtrribs
		#print passwords
	except IOError:
		print '\n Could not open user_pass.txt'
		sys.exit()
	return passwords

# create the server socket
def create_socket(port):
	HOST = ''
	PORT = port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#print 'Socket created'
	try:
		s.bind((HOST, PORT))
	except socket.error, msg:
		print '\nBind failed. Error Code : ' + str(msg[0]) + ' Message: ' + msg[1]
		sys.exit()
	#print 'Socket successfully bound'
	return s

# Function to authenticate the user
# 1. ask for username and password a max of 3 times
# 2. First check to make sure that the username is valid if it is check password
# 3. Next check to make sure the username is not already online
# 4. Next check is to make sure the username is not "BLOCKED" and it has been less than 60 seconds
# 5. If everything is ok, Welcome the user to the chat server and return the user and the passwordList dict

def check_password(conn, loginPasswords):
	passwordList = loginPasswords
	for i in range(3):
		conn.send('Username: ')
		user = conn.recv(1024)
		user = user.rstrip()
		conn.send('Password: ')
		password = conn.recv(1024)
		password = password.rstrip()
		if user not in passwordList:
			conn.send('No such user')
		elif passwordList[user][0] != password:
			conn.send('Bad Password')
		elif passwordList[user][2] == 'online':
			conn.send(user + ' already connected')
		elif passwordList[user][6] == 'BLOCKED' and datetime.datetime.now() - passwordList[user][5] < one_min:
			conn.send(user +' is BLOCKED')
		elif passwordList[user][6] == 'BLOCKED' and datetime.datetime.now() - passwordList[user][5] >= one_min:
			passwordList[user][6] = ''
			conn.send('Welcoe to Simple Chat Server! \n')
			passwordList[user][1] = conn
			passwordList[user][2] = 'online'
			passwordList[user][3] = datetime.datetime.now()
			return user, passwordList
		else:
			conn.send('Welcome to Simple Chat Server! \n')
			passwordList[user][1] = conn
			passwordList[user][2] = 'online'
			passwordList[user][3] = datetime.datetime.now()
			return user, passwordList
		if i < 2:
			conn.send('\nPlease try again! \n')
		else:
			if user not in passwordList:
				conn.close()
			else:
				passwordList[user][5] = datetime.datetime.now()
				passwordList[user][6] = 'BLOCKED'
				conn.close()
			return user, passwordList

# main fuction to handle the clients
# 1. Run the loop while the user has not timed out yet
# 2. Separate the input commands using the blank space as a separator
# 3. Check each command and apply the proper handling for each command
# 4. If user does not enter anything, send the available commands
# 5. If a user enters an unrecognized command notify the user
def handle_clients(user, loginPasswords):
	passwordList = loginPasswords
	client_user = user
	commands = ''
	divcommands = ['']
	passwordList[client_user][4] = datetime.datetime.now()
	try:	
		while datetime.datetime.now() - passwordList[client_user][4] <  thirty_min:
			passwordList[client_user][1].send("Command: ")
			commands = passwordList[client_user][1].recv(1024)
			commands = commands.rstrip()
			divcommands = commands.split(' ')
			if divcommands[0] == 'logout':
				passwordList[client_user][2] = 'offline'
				passwordList[client_user][1].close()
				print "%s logged out" % client_user
				thread.exit()
			elif divcommands[0] == '':
				passwordList[client_user][1].send('Available commands are: \n')
				passwordList[client_user][1].send('whoelse, wholasthr, broadcast <message>, message <user> <message>, and logout\n')
			elif divcommands[0] == 'whoelse':
				passwordList[client_user][4] = datetime.datetime.now()
				for u in passwordList:
					if u != client_user and passwordList[u][2] == 'online':
						passwordList[client_user][1].send(u + '\n')
			elif divcommands[0] == 'wholasthr':
				passwordList[client_user][4] = datetime.datetime.now()
				for u in passwordList:
					if passwordList[u][4] != '':
						if u != client_user and datetime.datetime.now() - passwordList[u][4] < one_hour:
							passwordList[client_user][1].send(u + '\n')
			elif divcommands[0] == 'broadcast':
				passwordList[client_user][4] = datetime.datetime.now()
				for u in passwordList:
					if u != client_user and passwordList[u][2] == 'online':
						passwordList[u][1].send('\n' + client_user +': ')
						for i in range(1,len(divcommands)):
							passwordList[u][1].send(divcommands[i]+' ')
						passwordList[u][1].send('\n')
			elif divcommands[0] == 'message':
				passwordList[client_user][4] = datetime.datetime.now()
				try:
					if passwordList[divcommands[1]][2]=='online':
						passwordList[divcommands[1]][1].send('\n' + client_user +': ')
						for i in range(2,len(divcommands)):
							passwordList[divcommands[1]][1].send(divcommands[i]+' ')
					else:
						passwordList[client_user][1].send('User does not exist or not online \n')
				except KeyError:
					passwordList[client_user][1].send('\nUser does not exist or not online \n')
			else:
				passwordList[client_user][4] = datetime.datetime.now()
				passwordList[client_user][1].send("Command not recognized\n")
	except socket.error:	
		print '\nClient pressed Ctrl -C'
		passwordList[client_user][2] = 'offline'
		print "%s logged out" % client_user
		thread.exit()
	# User Timed OUT 
	passwordList[client_user][2] = 'offline'
	passwordList[client_user][1].send('Timed out!')
	passwordList[client_user][1].close()
	print "%s logged out" % client_user
	thread.exit()


if __name__ == "__main__":
	main(sys.argv)
