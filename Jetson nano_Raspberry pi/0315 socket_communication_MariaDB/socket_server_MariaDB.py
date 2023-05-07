import socket
import pymysql


# 서버의 주소와 포트 
HOST = '127.0.0.1'
PORT = 5000     

# 소켓 객체를 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

# accept 함수에서 대기하다가 클라이언트가 접속하면 새로운 소켓을 리턴 
client_socket, addr = server_socket.accept()

# 접속한 클라이언트의 주소입니다.
print('연결 성공')

db = pymysql.connect(host="localhost", user="root", password="0000", charset="utf8")
cursor = db.cursor()
if pymysql.connect:
        print('connect ok')

quantity_1 = 0
while True:

        # 클라이언트가 보낸 메시지를 수신하기 위해 대기합니다. 
        data = client_socket.recv(1024)

        if not data:
            break

        # 수신받은 문자열을 출력합니다.
        print('받은 메세지 : ', data.decode())
        cursor.execute('USE mysql;')
        if data.decode()=='1':
             cursor.execute('INSERT INTO fish_detection (classification,quantity) VALUES ("Pterophyllum",TRUE)')
        elif data.decode()=='2':
             cursor.execute('INSERT INTO fish_detection (classification,quantity) VALUES ("Arapaima gigas","1")')
        elif data.decode()=='3':
             cursor.execute('INSERT INTO fish_detection (classification,quantity) VALUES ("ikan-mas","1")')
        else:
             cursor.execute('INSERT INTO fish_detection (classification,quantity) VALUES ("trash","1")')
             
        db.commit()
       
# 소켓을 닫습니다.
db.close()
client_socket.close()
server_socket.close()
