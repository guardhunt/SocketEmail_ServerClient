import socket
import sys
import hashlib

class socket_client():
  def __init__(self, ip, port):
    self.ip = ip
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_address = (self.ip, int(self.port))
    self.logged_on = False # Used for logging on and off (state variable)
    self.ID = 0 # Keeps track of session ID
	
  def connect(self, user):
    """
    Handles the handshake to the server
    Input: byte string of username:password
    """
    self.sock.connect(self.server_address)
    message = user
    self.sock.send(message)
    try:    
        recieved = self.sock.recv(1024)
    except not recieved:
        self.sock.send(message)
        print("No data recieved. Resending Handshake") 
    finally:
        pass
    
    #Following section either receives the session id from the server or 
    #closes connection if an error occured
    recieved = recieved.split(":")
    if recieved[0] == "OK":
      self.ID = recieved[1]
      return(self.ID)
    else:
      print("Error: Exiting and Closing Socket")
      self.sock.close()
      exit()
      
  def check_sum(self, message): #Help from Wade Rutherford who used this method with MD5
    return hashlib.sha1(message).hexdigest() #returns a string of double length, containing only hexadecimal digits
    
  def session(self, ID): 
    """
    The session class handles most of the session 
    """
    self.ID = ID
    print("Session started")
    self.logged_on = True #Switched on until user logs off
    while self.logged_on == True:
      cmd = self.get_cmd() 
      package = self.mng_cmd(cmd)
      # New connection has to be created each time the client attempts a new 
      # communcation with the server
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect(self.server_address)
      self.sock.send(package)
      
      receaved = self.sock.recv(1024)
      print receaved
      
      #try and resend package 3 times
      try_counter = 0
      while receaved == "KO":
        if try_counter < 4:
          self.sock.send(package)
          receaved = self.sock.recv(1024)
          receaved.decode("utf-8")
          try_counter += 1
        break
      
      self.sock.close()
    return

  def get_cmd(self):
    """
    Takes command from the user to be sent to the server
    Input: None
    Output: user input <type: string>
    """
    cmd = raw_input("Enter cmd: ")
    cmd = str(cmd)
    return cmd

  def mng_cmd(self, cmd):
    """
    Creates package to be sent to the server
    Input: command (e.g. delmsg)
    Output: package for server (e.g. "<ID>:'getmsg':<USERNAME>")
    """
    
    print("CMD " + str(cmd))
    if cmd == "email":
      package = self.email_cmd()
    elif cmd == "getmsg":
      package = self.getmsg_cmd()
    elif cmd == "count":
      package = self.count_cmd()
    elif cmd == "delmsg":
      package = self.deleat_cmd()
    elif cmd == "dump":
      package = self.dump_cmd()
    elif cmd == "logoff":
      package = self.logoff_cmd()
    elif cmd == "help":
      package = self.help_cmd()
    elif cmd == "shutdown":
      print("Shutting down...")
      self.shutdown(self.ID)
    else:
      print("Command does not exist.")
      package = "ERROR"
      
    if package == "ERROR":
      new_cmd = self.get_cmd()
      package = self.mng_cmd(new_cmd)
      return package
    else:
      return package

  def email_cmd(self):
    """
    Composes the email command
    Input: None
    Output: package for server (in the form: "<ID>:'email':<USERNAME>:<SUBJECT>:<MSG>")
    """
    recipient = raw_input("Enter email recipient: ")
    subject = raw_input("Enter email subject: ")
    msg  = raw_input("Enter email message: ")
    package = "{0}:{1}:{2}:{3}:{4}".format(self.ID, "email", recipient, subject, msg)
    return self.encode(package)
  
  def getmsg_cmd(self):
    """
    Composes the get message command
    Input: None
    Output: package for server (in the form: "<ID>:'getmsg':<USERNAME>")
    """
    sender_un = raw_input("Enter email sender: ")
    package = "{0}:{1}:{2}".format(self.ID, "getmsg", sender_un)
    return self.encode(package)

  def count_cmd(self):
    """
    Composes the command to count the number of emails in account
    Input: None
    Output: package for server (in the form: "<ID>:'count'")
    """
    package = "{0}:{1}".format(self.ID, "count")
    return self.encode(package)
    
  def deleat_cmd(self):
    """
    Composes the command to delete a message from an account
    Input: None
    Output: package for server (in the form: "<ID>:'delmsg':<USERNAME>:<SUBJECT>")
    """
    sender_un = raw_input("Enter sender user name: ")
    subject = raw_input("Enter email subject: ")
    package = "{0}:{1}:{2}:{3}".format(self.ID, "delmsg", sender_un, subject)
    return self.encode(package)

  def dump_cmd(self):
    """
    Composes the command to display all the  messages from an account
    Input: None
    Output: package for server (in the form: "<ID>:'dump'")
    """
    package = "{0}:{1}".format(self.ID, "dump")
    return self.encode(package)
  
  def logoff_cmd(self):
    """
    Composes the command to tell the server that it is logging off 
    Input: None
    Output: package for server (in the form: "<ID>:'logoff'")
    """
    package = "{0}:{1}".format(self.ID, "logoff")
    print("logoff function called")
    self.logged_on = False # Switching off to break out of session
    return self.encode(package)

  def encode(self, package):
    """
    Turns string commands into byte commands to be sent to server
    Input: Package to be sent to be server <type: string>
    Output: Package with checksum appended and then converted to byte string
    """
    checksum = self.check_sum(package)
    package = bytes("{0}#{1}".format(package, checksum))
    return package
  
  def help_cmd(self):
    """
    Called by user if they want to know what commands are available to them
    """
    package = "{0}:{1}".format(self.ID, "help")
    return self.encode(package)
    
  def shutdown(self):
    """
    Gracefully shuts down the client
    """
    package = "{0}:{1}".format(self.ID, "logoff")
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect(self.server_address)
    print("Closing")
    package = self.encode(package)
    self.sock.send(package)
    sys.exit()
    
def main():
  sockip = "localhost" 
  sockport = 1503
  #for handshake and creating session
  try:
    while True:
      socketObj = socket_client(sockip, sockport)
      un = raw_input("Enter user name: ")
      pw = raw_input("Enter password: ")
      print("Client Socket Opened. Handshake Sent.")
      msg = bytes("{0}:{1}".format(un, pw))
      ID = socketObj.connect(msg)
    
      #for using session
      sessionObj = socket_client(sockip, sockport)
      sessionObj.session(ID)
  except: # If anything goes wrong, the client catches the error and shuts down gracefully
    print("\nSomething went wrong")
    socketObj.shutdown()
  
main()

