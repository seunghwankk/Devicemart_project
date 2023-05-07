import socket
import MySQLdb


# 서버의 주소와 포트 
HOST = '127.0.0.1'     
PORT = 9999       

# 소켓 객체를 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

# accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓을 리턴 
client_socket, addr = server_socket.accept()

# 접속한 클라이언트의 주소입니다.
print('연결 성공')

db = MySQLdb.connect("localhost", "root", "0000", "fish_detection")
curs = db.cursor()

while True:

        # 클라이언트가 보낸 메시지를 수신하기 위해 대기합니다. 
        data = client_socket.recv(1024)

        if not data:
            break

        # 수신받은 문자열을 출력합니다.
        print('받은 메세지 : ', data.decode())
        if data=='1':
             classification = 'Pterophyllum'
             quantity = 1
        elif data=='2':
             classification = 'Arapaima gigas'
             quantity = 1
        elif data=='3':
             classification = 'ikan-mas'
             quantity = 1
        else:
             classification = 'trash'
             quantity = 1
        try:
            curs.execute("""INSERT INFO fish_detection (classification) VALUES (%c)""",(classification))
            curs.execute("""INSERT INFO fish_detection (quantity) VALUES (%d)""",(quantity))
            db.commit()
        except KeyboardInterrupt:
             break

    

# 소켓을 닫습니다.
client_socket.close()
server_socket.close()