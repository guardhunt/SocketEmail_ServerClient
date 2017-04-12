import socket
import sys
import pickle
import time
import random

class socket_server():
  def __init__(self, ip, port):
    self.usernames = {"huntc": "123", "peterm" : "123",  "jamest" : "123", "tuckerm" : "123", "lydiar" : "123", "masterl" : "123", "cassym" : "123"}
    self.accounts = {}
    self.ip = ip
    self.port = port	
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_address = (self.ip, self.port)
    self.sock.bind(self.server_address)
 
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
      data = connection.recv(1024)
      if data:
        print("Handshake Data Recieved: Func-connect()")
        data.decode('utf-8')
        data = data.split(":")

        #check if username and are correct exists
        if data[0] in self.usernames:
          if self.usernames[data[0]] == data[1]:
            session_id = random.randint(1000000000, 9999999999)
            print("Session ID Sent: " + str(session_id))
            connection.send(b"Session Started:" + str(session_id))
            self.manage_session(session_id, data[0])
          else:
            connection.send(b"Password incorrect: " + str(data[1]))
        else:
          connection.send(b"Username incorrect: " + str(data[0]))
          
    finally:
      pass
    connection.close()
    print("Connection Closed")
    return

  def manage_session(self, session_id, un):
    """
    Mannage incoming commands from client after handshake and confirm Session ID
    """
    session_handle = Session(session_id, un, self.usernames)
    session_handle.populate_accounts()
    while session_handle.logged_on == True:
      self.sock.listen(1)
      connection, self.server_address = self.sock.accept()
      try:
        data = connection.recv(1024)
        if data:
          print("Session CMD Recieved: Func-manage_session()")
          data.decode('utf-8')
          data = data.split(":")
          if str(data[0]) == str(session_handle.ID):
            print("ID Recieved Correct. Handling CMD Message")
            session_handle.handle_msg(data, connection)
          else:
            print("ID Recieved Inccorect. Reponding to Client")
            connection.send(b"ID does not match exiting session ID: " + str(data[0]))
      finally:
        pass
    print("Session handled and user logged off: listening for new connection")
    session_handle.update_accounts()
    return
   
class Session():
  def __init__(self, session_id, un, usernames):
    self.name = ""
    self.accounts = {}
    self.logged_on = True
    self.ID = session_id
    self.un = un
    self.usernames = usernames

  def populate_accounts(self):
    self.accounts = pickle.load(open("accounts.p", "rb"))

  def handle_msg(self, data, connection):
    print data
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
      connection.send(b"Command sent does not exist")

  def update_accounts(self):
    """
    Update Pickle accounts file
    Called from the function(s):
      -emailcmd()
    """
    pickle.dump(self.accounts, open("accounts.p", "wb"))

	
  def emailcmd(self, connection, data):
    """
    Handle command for emails to be sent and log emails sent
    Data in form of [user name, command, recipient username, subject, message]
    Called from the function(s):
      -connect()
    """
    if data[2] not in self.usernames:
      connection.send(b"Recipient Name Not Recognized: " + str(data[2]))
    else:
      #append email contnets to accounts dictionary value with key being the recipient
      #email values logged in form of [sender, subject, message, date/time]
      self.accounts[data[2]].append([self.un, data[3], data[4], time.strftime("%c")])
      self.update_accounts()
      connection.send(b"Email sent to " + data[2])

	  
  def getmsgcmd(self, connection, data):
    """
    Handle command for getting messages from specific users
    Data in form of [user name, command, requested sender username]
    Called form the functions(s):
      -connect()
    """
    response = ""
    if data[2] not in self.usernames:
      connection.send(b"Sender Name Not Recognized: " + str(data[2]))
    else:
      #step through all emails of requested username
      #if email sender name is equal to the requested sender
      for logedEmail in self.accounts[data[0]]:
        if logedEmail[0] == data[2]:
          #response sent in form of [subject, message, date/time]
          response += ("Subject: " + str(logedEmail[1]) + "\n" + "Message: " + str(logedEmail[2]) + "\n" + str(logedEmail[3])+ "\n \n")
      connection.send(b"Emails from " + str(data[2])+ ":\n" + response)
 
  def countcmd(self, connection, data):
    """
    Give number of total mesages recieved
    Data in the form of [username, command]
    Called from the function(s):
      -connect()
    """
    count = 0
    for email in self.accounts[self.un]:
      count += 1
    connection.send("Total emails recived: " + str(count))
      

  def delmsgcmd(self, connection, data):
    """
    Deleat message recieved form specific user with specific subject
    Data in the form of [username, command, sender username, subject]
    Called from the function(s):
      -connect()
    """
    counter = 0
    sent = False
    for email in self.accounts[self.un]:  # for all email in account
      if data[2] in email[0]:
        print data[2]
        if data[3] in email[1]:             # email sender is equal to sepcied sender in cmd msg and email subject is equal to specified subject
          self.accounts[self.un].pop(counter)
          connection.send("Message deleated. Subject: " + data[3])
          print("Email deleated: Subject: " + data[3])
          sent = True  
      counter += 1
    if sent == False:
      print("Email not found. Subject: " + data[3])
      connection.send("Message not deleated. Email not found.") 
    

  def dumpcmd(self, connection, data):
    """
    Give all messages recived
    Data in the form of [username, command]
    Called from the function(s):
      -connect()
    """

    emails = ""
    for email in self.accounts[self.un]:
      emails += ("Sender: " + str(email[0]) + "\n" + "Subject: " + str(email[1]) + "\n" + "Message: " + str(email[2]) + "\n" + str(email[3])+ "\n \n")
    connection.send(b"All emails recived:\n" + emails)
    
  def help_cmd(self, connection):
    """
    Takes in data of the form [ID, command]
    Returns the help functionality
    """
    commands = "\nCommands: \nGet help: help \nSend email: email \nSearch for emails from user: getmsg \nGet number of mesages in inbox: count \nDeleat mesage by sender and subject: delmsg \nSee full email inbox: dump \nLog off of server: logoff\n"
    connection.send(commands)
    
  def logoffcmd(self, connection):
    self.logged_on = False
    connection.send(b"Successfully Logged Off User: " + str(self.un))

def main():
  """
  Create server socket, bind ip and port, create sock_server instace, create accounts dictionary, then listen and connect on request.
  """
  sockip = ("localhost")
  sockport =(8883)
  sock_server = socket_server(sockip, sockport)
  sock_server.create_accounts()
  print("[Socket Server Started on Port " + str(sockport) + "]")
  while True:
    sock_server.sock.listen(1)
    sock_server.connect()
  
main()
