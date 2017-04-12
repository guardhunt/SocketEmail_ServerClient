import socket
import sys

class socket_client():
  def __init__(self, ip, port):
    self.ip = ip
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_address = (self.ip, int(self.port))
    self.loggedon = False
	
  def connect(self, user):
    self.sock.connect(self.server_address)
    message = user
    self.sock.send(message)
    try:    
        recieved = self.sock.recv(1024)
        print (str(recieved))
    except not recieved:
        self.sock.send(message)
        print("No data recieved. Resending Handshake") 
    finally:
        pass
 
    recieved = recieved.split(":")
    if recieved[0] == "Session Started":
      ID = recieved[1]
      print("ID SPLIT: " + str(ID))
      return(ID)
    else:
      print("Error: Exiting and Closing Socket")
      self.sock.close()
      exit()
 
  def session(self, ID): 
    print("Session started")
    self.logged_on = True
    while self.logged_on == True:
      cmd = self.get_cmd()
      package = self.mng_cmd(cmd, ID)
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.connect(self.server_address)
      print(package)
      self.sock.send(package)
      try:
        receaved = self.sock.recv(1024)
        print("Data Recieved: " + str(receaved))
      except not receaved:
        self.sock.send(message)
        print("Data Not Received. Trying to resend command.")
      self.sock.close()
    return

  def get_cmd(self):
    cmd = raw_input("Enter cmd: ")
    cmd = str(cmd)
    return cmd

  def mng_cmd(self, cmd, ID):
    print("CMD " + str(cmd))
    if cmd == "email":
      package = self.email_cmd(ID)
    elif cmd == "getmsg":
      package = self.getmsg_cmd(ID)
    elif cmd == "count":
      package = self.count_cmd(ID)
    elif cmd == "delmsg":
      package = self.deleat_cmd(ID)
    elif cmd == "dump":
      package = self.dump_cmd(ID)
    elif cmd == "logoff":
      package = self.logoff_cmd(ID)
    elif cmd == "help":
      package = self.help_cmd(ID)
    elif cmd == "shutdown":
      print("Shutting down...")
      self.shutdown(ID)
    else:
      print("Command does not exist.")
      package = "ERROR"
      print("Else statement after command does not exist")
  
    if package == "ERROR":
      print("Inside if loop for package")
      new_cmd = self.get_cmd()
      package = self.mng_cmd(new_cmd, ID)
      return package
    else:
      print("Returning package from mng_cmd at end")
      print(package)
      return package

  def email_cmd(self, ID):
    recipient = raw_input("Enter email recipient: ")
    subject = raw_input("Enter email subject: ")
    msg  = raw_input("Enter email message: ")
    package = "{0}:{1}:{2}:{3}:{4}".format(ID, "email", recipient, subject, msg)
    return self.encode(package)
  
  def getmsg_cmd(self, ID):
    sender_un = raw_input("Enter email sender: ")
    package = "{0}:{1}:{2}".format(ID, "getmsg", sender_un)
    return self.encode(package)

  def count_cmd(self, ID):
    package = "{0}:{1}".format(ID, "count")
    return self.encode(package)
    
  def deleat_cmd(self,ID):
    sender_un = raw_input("Enter sender user name: ")
    subject = raw_input("Enter email subject: ")
    package = "{0}:{1}:{2}:{3}".format(ID, "delmsg", sender_un, subject)
    return self.encode(package)

  def dump_cmd(self, ID):
    package = "{0}:{1}".format(ID, "dump")
    return self.encode(package)
  
  def logoff_cmd(self, ID):
    package = "{0}:{1}".format(ID, "logoff")
    print("logoff function called")
    self.logged_on = False
    return self.encode(package)

  def encode(self, package):
    package = bytes("{0}".format(package))
    return package
  
  def help_cmd(self, ID):
    package = "{0}:{1}".format(ID, "help")
    return self.encode(package)
    
  def shutdown(self, ID):
    package = "{0}:{1}".format(ID, "logoff")
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect(self.server_address)
    print("Closing")
    self.sock.send(package)
    sys.exit()
    
def main():
  sockip = "localhost"
  sockport = 8883
  #for handshake and creating session
  try:
    while True:
      socketObj = socket_client(sockip, sockport)
      #socketObj.help_cmd()
      un = raw_input("Enter user name: ")
      pw = raw_input("Enter password: ")
      print("Client Socket Opened. Handshake Sent.")
      msg = bytes("{0}:{1}".format(un, pw))
      #msg = (b"huntc:123")
      session_ID = socketObj.connect(msg)
    
      #for using session
      sessionObj = socket_client(sockip, sockport)
      sessionObj.session(session_ID)
  except:
    print("\nSomething went wrong")
    socketObj.shutdown(session_ID)
  
main()

