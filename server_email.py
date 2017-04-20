import socket
import sys
import pickle
import time
import random
from threading import Thread
import hashlib

class socket_server(): #class format for the server side of the socket
  def __init__(self, ip, port): #initilize with ip and port
    self.usernames = {"huntc": "123", "peterm" : "123",  "jamest" : "123", "tuckerm" : "123", "lydiar" : "123", "masterl" : "123", "cassym" : "123"} #list of usernames and passwords hashed together
    self.accounts = {} #empty list for the accounts that will be filled later by a pickle file
    self.ip = ip #takes in the ip argument and sets the ip for the connection
    self.port = port #takes in the port argument and sets the socket port connection
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #the socket object, standard library setup
    self.server_address = (self.ip, self.port) #creates the server address with IP and Port used from earlier
    self.sock.bind(self.server_address) #bind the socket using the server_address
 
  def create_accounts(self):
    """
    Create accoutns dictionary from pickle file
    Called from function(s):
      -main()
    """
    self.accounts = pickle.load(open("accounts.p", "rb")) 
      
  def connect(self):
    """
    Create connection on client request, test for data, split data recievd, test username, call appropriate command function.
    Called from functions(s):
      -main()
    """
    connection, self.server_address = self.sock.accept()
    
    try:
      data = connection.recv(1024) #buffer for the amount of bytes that can be recieved 
      if data:
        data.decode('utf-8') #decode using standard U.S. utf-8
        data = data.split(":") #split the data at every colon

        #check if username and are correct exists
        if data[0] in self.usernames: #takes first element of two and checks if it is in the list of usernames
          if self.usernames[data[0]] == data[1]: #if the list of usernames has a hash to a password that matches the one given in data. 
            session_id = random.randint(1000000000, 9999999999) #creates a random integer id between these two numbers to use as a session identifier
            print("Session ID Sent: " + str(session_id)) #print the identifier on the server side
            connection.send(b"OK:" + str(session_id)) #send the session id over the connection 
            self.manage_session(session_id, data[0]) #calls message session using the session id and the username from data to create a session class
          else: #if password doesn't match prints password incorrect on server side and sends a KO to the client
            connection.send(b"KO")
            print("Password sent incorrect")
        else: #if ussername doesn't exist prints username incorrect on server side and sends a KO to the client
          connection.send(b"KO")
          print("Username sent incorrect")
          
    finally:
      pass
    connection.close() #close socket connection
    print("Connection Closed")
    return

  def manage_session(self, session_id, un):
    """
    Mannage incoming commands from client after handshake and confirm Session ID
    """
    session_handle = Session(session_id, un, self.usernames) #creates a handle for a session class that uses the session identifier, the username, and the list of usernames
    session_handle.populate_accounts() #populate accounts from the pickle file
    while session_handle.logged_on == True:
      self.sock.listen(1) #listens for a single byte
      connection, self.server_address = self.sock.accept() #tries to accept the connection
      try:
        data = connection.recv(1024) #tries to recieve up to 1024 bytes from the client
        if data: #checks to see if there is data to recieve
          print("Session CMD Recieved: Func-manage_session()")
          data.decode('utf-8') #decodes using standard U.S. utf-8
          
          #testing messageddd and checksum data
          full_data = data.split("#") #splits off the checksum half of data
          if self.try_checksum(full_data) == False: #checks the checksum
            connection.send(b"KO") #sends KO to client side if try_checksum comes back with False
            print("Checksum ERROR!")
          else: #if try_checksum is equal to True
            #testing message data only
            data = full_data[0].split(":") #split the message using colons that isn't the checksum
            #check if the session ID is the same
            if str(data[0]) == str(session_handle.ID): #if the first element of data is the session ID handle the message using standard commands
              print("ID Recieved Correct. Handling CMD Message")
              session_handle.handle_msg(data, connection)
            else: #if ID is no included or inccorrect
              print("ID Recieved Inccorect. Reponding to Client")
              connection.send(b"KO")
              print("ID match error")
      finally:
        pass
    print("Session handled and user logged off: listening for new connection")
    session_handle.update_accounts() #updates the pickle file with the newly added messages etc
    return
  
  def check_sum(self, message): #Help from Wade Rutherford who used this method with MD5
    return hashlib.sha1(message).hexdigest()  #encrypts using SHA1 and hexdigests so that it easier to pass along
    
  def try_checksum(self, message): #takes the checksum sent from the client and tests it with the check_sum of the message send.
    sent_checksum = message[1]
    test_checksum = self.check_sum(message[0])
    if sent_checksum == test_checksum: #if both checksumns match then return true else false
      return True
    else:
      return False
  
class Session(): #creates a session class for the user using a session identifier
  def __init__(self, session_id, un, usernames): #creates a session using the session id, username, and the list of usernames
    self.name = "" 
    self.accounts = {} #empty to be filled with pickle file data
    self.logged_on = True #loggon on set to true
    self.ID = session_id
    self.un = un
    self.usernames = usernames

  def populate_accounts(self):
    self.accounts = pickle.load(open("accounts.p", "rb")) #populate the empty accounts with the data from the pickle file

  def handle_msg(self, data, connection): #list of commands the user can use to check messages or send them
    #for email functionality
    if "email" in data[1]:
      print ("email cmd recieved")
      self.emailcmd(connection, data)

    #for get message functionality
    elif "getmsg" in data[1]:
      print("Get msg. cmd recieved")
      self.getmsgcmd(connection, data)

    #for count functionality
    elif "count" in data[1]:
      print("count cmd recieved")
      self.countcmd(connection, data)

    #for deleat message functionality
    elif "delmsg" in data[1]:
      print("delmsg cmd recieved")
      self.delmsgcmd(connection, data)

    #for dump message functionality
    elif "dump" in data[1]:
      print("dump cmd recieved")
      self.dumpcmd(connection, data)
    
    elif "logoff" in data[1]:
      print("logoff cmd recieved")
      self.logoffcmd(connection)
      
    elif "help" in data[1]:
      self.help_cmd(connection)

    else:
      print("NA cmd recieved")
      connection.send(b"KO")

  def update_accounts(self):
    """
    -Sesion() function dumps all new account information before closing
    """
    pickle.dump(self.accounts, open("accounts.p", "wb")) #updates the pickle file with any new info recently added after logoff

	
  def emailcmd(self, connection, data):
    """
    -Session() function adds the sent email to specified user's account
    -Data in form of [ID, CMD, recipient username, subject, message]
    """
    if data[2] not in self.usernames:
      connection.send(b"Recipient Name Not Recognized: " + str(data[2]))
    else:
      #append email contnets to accounts dictionary value with key being the recipient
      #email values logged in form of [sender, subject, message, date/time]
      self.accounts[data[2]].append([self.un, data[3], data[4], time.strftime("%c")])
      self.update_accounts()
      connection.send(b"OK: Email Sent")

	  
  def getmsgcmd(self, connection, data):
    """
    -Session() function returns with all emails from specified sender
    -Data in form of [ID, CMD, requested sender username]
    """
    response = ""
    if data[2] not in self.usernames:
      connection.send(b"Sender Name Not Recognized: " + str(data[2]))
    else:
      for email in self.accounts[self.un]:
        if email[0] == data[2]:
          #response sent in form of [subject, message, date/time]
          response += ("Subject: " + str(email[1]) + "\n" + "Message: " + str(email[2]) + "\n" + str(email[3])+ "\n \n")
      connection.send(b"Emails From:" + str(data[2])+ ":\n" + response)
 
  def countcmd(self, connection, data):
    """
    -Session() function returns total number of user's emails
    """
    count = 0
    for email in self.accounts[self.un]:
      count += 1
    connection.send("Total emails recived: " + str(count))
      

  def delmsgcmd(self, connection, data):
    """
    -Session() function deleats message, with specified sender and subject
    -Data in the form [ID, CMD, sender username, subject]
    """
    counter = 0
    sent = False
    for email in self.accounts[self.un]:                           # for all emails in account
      if data[2] in email[0]:                                      # if specified username is in email username slot
        if data[3] in email[1]:                                    # if specifed subject is in email subject slot
          self.accounts[self.un].pop(counter)                      # pop email at index location of counter in list of eamils
          connection.send("Email deleated. Subject: " + data[3])
          print("Email deleated. Subject: " + data[3])
          sent = True  
      counter += 1
    if sent == False:
      print("Email not found. Subject: " + data[3])
      connection.send("KO. Email not found.") 
    

  def dumpcmd(self, connection, data):
    """
    -Session() function sends client all emails in thir own account
    """
    emails = ""
    for email in self.accounts[self.un]:
      emails += ("Sender: " + str(email[0]) + "\n" + "Subject: " + str(email[1]) + "\n" + "Message: " + str(email[2]) + "\n" + str(email[3])+ "\n \n")
    connection.send(b"All emails recived:\n" + emails)
    
  def help_cmd(self, connection):
    """
    -Session()  function returns all command prompts to client
    """
    commands = "\nCommands: \nGet help: help \nSend email: email \nSearch for emails from user: getmsg \nGet number of mesages in inbox: count \nDeleat mesage by sender and subject: delmsg \nSee full email inbox: dump \nLog off of server: logoff\n"
    connection.send(commands)
    
  def logoffcmd(self, connection):
    """
    -Session() function allows for session loop to exit and responds with OK
    """
    self.logged_on = False
    connection.send(b"OK")
    print("User Loged off")
    
def main():
  """
  -Create server socket for handshake
  -Create server class instace and populate accounts dictionary
  -Listen for connection and launch server on connect
  """
  sockip = ("localhost")
  sockport = (1503)
  sock_server = socket_server(sockip, sockport)
  sock_server.create_accounts()
  print("[Socket Server Started on Port " + str(sockport) + "]")
  #loop allows server to contune running for multible connections from client
  while True:
    sock_server.sock.listen(1)
    t = Thread(sock_server.connect())
    t.start()
    
main()
