# Client and Server Implementation for Socket Based Email Service
### Specification and Protocol Outline

CSC 412: Networking
Berea College, Spring 2017

Team Members: Christopher Hunt, Hunter Wiseman and Vincent Tembo

## Files and Modules

### Client_email.py
The client_email.py file holds all the client functions and operates solely as a test client without many extra functionalities for user interaction. The client does however match the implementation  of the server, which is a connection based implementation where a handshake must occur with the exchange of user information before a session can be initiated. This two phase system is implemented on the server and mimicked on the client side structurally. 

Modules Used: socket, sys, hashlib

### Server_email.py
The server_email.py file holds all the server functions and classes necessary to start a server socket, listen for a connection, test the initial connection handshake information received from the client, and launch and handle the session class and subsequent commands from the client. 

Modules Used: socket, sys, pickle, time, random, thred, hashlib

## Interface and Operation Overview
Once the server file (server_email.py) has been ran, it will continue to run until manually closed. Users can connect, run sessions, send commands, and log off multiple times while the server is running. To start the client the client_email.py file needs to be ran. The client will only close if incorrect  username and password information is provided. Once a session has been launched the client is prompted for a command. The full list of commands and command prompts can be accessed by entering the help command. The full list of commands is included below.

### Comands and Prompts
Get command list - help
Send email - email
Delete message - delmsg
Dump all messages - dump
Get emails from specific sender - getmsg
Get number of messages in inbox - count
Logoff session - logoff 

Depending on the command sent, the user is further prompted for the command specific information needed to execute that particular command.  For example, if the send email command is entered, the user is prompted for a recipient name, a email subject, and an email message. Once the command information has been collected, a checksum value is generated and appended to the end of the command string, the whole package is encoded using UTF-8, the package is sent to the server, and the client waits for a response from the server. 
The server receives the package, decodes it,  and splits off the checksum from the end of the string at the pound (#) symbol. This is obviously a problem because the user can not use a pound symbol for any input data being sent, however it serves as a functional way of dividing the message content form the checksum. The server then generates a checksum from the message content, using the same hashlib method as the client, and check it’s own checksum of the message with the sent checksum that the client generated before sending the message. If the checksums do not match on the server side, thus indicated bitloss or some other issue in transmission, the server responds with KO and the client automatically retries up to 3 times to resend the data until transmission is successful and the checksums match. If there are any further errors in the actual data supplied by the user, such as an incorrect recipient name for the send email command, or a non-existent subject for the delete message command, then the server will reply to the client, denoting the particular error. There is no functionality for an automatic try and resend for these types of errors because they originate from the user input, and thus the user must correct the error by re-entering new information. With this type of error the client will print the error message, indicating the specific error encountered by the server, then prompt the user for a new command. 

## Classes, Class Variables, and Methods

### Client Classes
Socket_client Class

Class Variables:
Self.ip -- stores ip information for the server 
Self.port -- stores port information for the server 
Self.sock -- stores the socket created from the socket module
Self.server_address -- stores the sever address information (ip, port)
Self.logged_on -- stores a default value for the logged on status

Class Methods:
Connect -- send initial handshake information and listen for response
Handshake sent in the form “username:password”
If valid un and pw received, response received is in the form “Session Started:xxx” where “xxx” is the unique id generated and sent from the server and the session handle function is called.
If invalid error message received and socket is closed.
Check_sum -- creates a checksum value to send to the server
Takes the message and encrypts it using SHA1
Runs Hexdigest to make it more manageable to send to the server
Session -- handles the session commands and responses
Generates command message in the form “ID:cmd:Command Specific information”
If email the command information is “email:subject:message”
When response received from server print response and close socket.
A try counter is set in place so that a resend can happen up to three times.

### Server Classes
Socket_server class

Class Variables:
Self.accounts -- empty dictionary to be populated from pickle file
Self.usernames -- dictionary holding all usernames and passwords
Self.ip -- server ip address passed in at initialization
Self.port -- server port number passed in at initialization
Self.server_address -- tuple created from ip and port 
self.sock.bind initialization of the socket 

Class Methods:
Create_accounts -- populates the accounts dictionary  from pickle file
Connect -- creates initial handshake connection on client request
Try if data received and split data by the colon “:” marker.
Check if username data is accurate
If it is then generate random number for session ID, return it to the client, and call the manage_session class, passing through the session_id and the username.
If incorrect then respond appropriately to client. 
At end of function close connection and return.
Manage_session -- manage session class instance for sessions with client
Create session class instance and pass username, id, and all usernames
Populate accounts dictionary
Loop through listening for connection from client and handling commands while session class variable logged_on is set to true. 
Listen for client connections
Create socket connection on connect
Handle session command and call appropriate session class function.
Check for valid session command and valid session ID
Respond to client with action completed

Session class

Class Variables:
Self.name --
Self.accounts -- empty dictionary to be populated by accounts dictionary, structure: key = username, value = list of lists where the structure is similar to [[emailcontents][emailcontents][emailcontents].
Self.logged_on -- boolean value keeping status of session status, initialized to True
self. ID -- class variable to hold the session ID 
Self.un-- variable to hold the username for the session

Class Methods:
populate_accounts -- populate accounts dictionary from pickle file
Handle_msg -- check for cmd section of session connection request from client and call appropriate session class method (e.g. if “email” then call emailcmd function).
If not correct command given in message then respond to client with error message. 
Update_accounts -- dump updated dictionary account information into the pickle file.
Emailmcd -- append email contents to the accounts list of lists value in the key-value pair, where key = self.un.
Getmsgcmd -- get messages from a specified user from the accounts dictionary
countcmd  --get the number of emails the user has.
Dumpcmd -- dump all emails in user's account dictionary value. 
Main Function
Initialize socket_server class instance with port and ip passed throgh
Call create_accounts function in class
Loop through listening for connections then calling the connect function in while loop.

