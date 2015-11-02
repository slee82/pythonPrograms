Sam Lee - hsl2113 - Programming Assignment 1 
README 

----------------- Description -------------------------------
1. My server.py file includes the server code which handles all input from clients, parses it, and implements the commands as specified. The client.py file creates socket to connect to the server and basically just relays input and output from the user via stdin and the server via the socket.

****** Server ********
# Main server loop
	# 1. Listen and accept connections from clients
	# 2. Check the password for the user using check_password function
	# 3. If successful launch a new thread with the handle_client function
	# 4. If authentication is not successful then close the connection
	# 5. Error handling for ctrl - c
# read_password_file()
	# 1. Read the user_pass.txt file parse it and put it into a dictionary
# create_socet()
	# 1. Create the server socket and bind it
# check_password()
	# 1. ask for username and password a max of 3 times
	# 2. First check to make sure that the username is valid if it is check password
	# 3. Next check to make sure the username is not already online
	# 4. Next check is to make sure the username is not "BLOCKED" and it has been less than 60 seconds
	# 5. If everything is ok, Welcome the user to the chat server and return the user and the passwordList dict
# handle_clients()
	# 1. Run the loop while the user has not timed out yet
	# 2. Separate the input commands using the blank space as a separator
	# 3. Check each command and apply the proper handling for each command
	# 4. If user does not enter anything, send the available commands
	# 5. If a user enters an unrecognized command notify the user

----------------- Development Environment --------------------
OS:  	MAC OS 10.9.5
python: 2.7.5
IDE:	Sublime Text 

----------------- How to Run Code ----------------------------
3. Instructions on how to run the files are included when you run the files, but for the server please run it by typing 

***** Server ******
$python server.py <port number>
***** Client ******
 $python client.py <server host> <server port>


----------------- Additional Features ------------------------
4. I did not implement any additional functionalities
