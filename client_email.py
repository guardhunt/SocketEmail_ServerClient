import socket
class socket_client():
  def __init__(self, ip, port):
    self.ip = ip
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.server_address = (self.ip, int(self.port))
	
  def connect(self, user):
    self.sock.connect(self.server_address)
    try:
        message = user
        self.sock.send(message)
        recieved = self.sock.recv(1024)
        print (str(recieved))
    finally:
        pass
        #print("in Finnally: Socket Closed")
        #self.sock.close()
        #self.session(receaved)
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
    msg = (":email:huntc:Email Subject: This is my message. It is a good message. I think I should get more creative sometime. The End. --masterl")
    self.sock.connect(self.server_address)
    try:
      message = str(ID) + msg
      message = bytes("{0}\0".format(message))  #code based off of code by Matt Jaddu
      self.sock.send(message)
      receaved = self.sock.recv(1024)
      print("Data Recieved from CMD send: " + str(receaved))
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
