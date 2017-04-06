import socket
class socket_client():
  def __init__(self, ip, port):
    self.ip = ip
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_address = (self.ip, int(self.port))
	
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
    print("session started")
    msg = (":dump")
    self.sock.connect(self.server_address)
    message = str(ID) + msg
    message = bytes("{0}\0".format(message))  #code based off of code by Matt Jaddu
    self.sock.send(message)
    try:
      receaved = self.sock.recv(1024)
      print("Data Recieved:: " + str(receaved))
    except not receaved:
      self.sock.send(message)
      print("Data Not Received. Trying to resend command.")
    finally:
      print("Closing Socket- from session()")
      self.sock.close()

  #for testing getmsg command
  #msg = (b"huntc:getmsg:jamest")

  #for testing count command
  #msg = (b"huntc:count")

  #for testing dump command

def main():
  sockip = "localhost"
  sockport = 8888
  socketObj = socket_client(sockip, sockport)
  
  #for handshake and creating session
  print("Client Socket Opened. Handshake Sent.")
  msg = (b"huntc:123")
  session_ID = socketObj.connect(msg)
  
  #for using session
  sessionObj = socket_client(sockip, sockport)
  sessionObj.session(session_ID) 
  
main()

