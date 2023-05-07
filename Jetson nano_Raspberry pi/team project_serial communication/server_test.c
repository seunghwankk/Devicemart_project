#include <stdio.h>
#include <string.h>
#include <unistd.h> // 파일 관리 함수 헤더
#include <arpa/inet.h>
#include <sys/socket.h> // 소켓프로그래밍 함수선언


#define TCP_PORT 5900
#define IP "10.10.141.67"

int main(int argc, char** argv)
{
    int ssock; // 서버 소켓 파일디스크립터 변수 선언
    socklen_t clen;
    int n;
    struct sockaddr_in servaddr, cliaddr; // sockaddr_in 구조체 변수 선언
    char mesg[BUFSIZ];

    // 서버 소켓 TCP/IP 프로토콜 생성
    if ((ssock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket()");
        return -1;
    }

    // 주소 구조체에 주소지정
    memset(&servaddr, 0, sizeof(servaddr)); //구조체 배열 초기화
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(IP);
    servaddr.sin_port = htons(TCP_PORT);

    //bind 함수를 사용하여 서버소켓의 주소설정
    if (bind(ssock, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("bind()");
        return -1;
    }

    //동시에 접속하는 클라이언트의 처리를 위한 대기큐 설정
    if (listen(ssock, 8 < 0))
    {
        perror("listen()");
        return -1;
    }

    clen = sizeof(cliaddr);
    do
    {
        //클라이언트가 접속하면 접속을 허용하고 클라이언트 소켓 생성
        int n, csock = accept(ssock, (struct server_sock*)&cliaddr, &clen);

        //네트워크 주소를 문자열로 변경
        inet_ntop(AF_INET, &cliaddr.sin_addr, mesg, BUFSIZ);
        printf("Client is conneted :%s\n", mesg);

        if ((n = read(csock, mesg, BUFSIZ)) <= 0)
            perror("read()");

        printf("Received data : %s", mesg);

        //클라이언트로 buf 에있는 문자열 전송
        if (write(csock, mesg, n) <= 0)
            perror("write()");

        close(csock);
    } while (strncmp(mesg, "q", 1));
    close(ssock);

    return 0;

 }

