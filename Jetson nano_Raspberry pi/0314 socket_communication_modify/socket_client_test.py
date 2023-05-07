import socket

# 서버의 주소와 포트
HOST = '127.0.0.1'  
PORT = 9999  

# 소켓 객체를 생성합니다.   
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 지정한 HOST와 PORT를 사용하여 서버에 접속
client_socket.connect((HOST, PORT))

while True:
    value = input(' ') 
    if value =='quit':
      close_data = value
      break

    client_socket.send(value.encode())

client_socket.close()