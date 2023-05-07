#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> // 파일 관리 함수 헤더
#include <arpa/inet.h>
#include <sys/socket.h> // 소켓프로그래밍 함수선언


#define TCP_PORT 5900

int main(int argc, char **argv)
{
    int csock; // 클라이언트 소켓 파일디스크립터 변수 선언
    struct sockaddr_in servaddr; // sockaddr_in 구조체 변수 선언
    char mesg[BUFSIZ];
    
    if (argc < 2)
    {
        printf("Usage: %s IP_ADRESS\n", argv[0]);
        return -1;
    }

    // 클라이언트 소켓 TCP/IP 프로토콜 생성
    if ((csock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket()");
        return -1;
    }

    // serv_sock에 bind로 주소 넣기 위한 밑작업
    memset(&servaddr, 0, sizeof(servaddr)); //구조체 배열 초기화
    servaddr.sin_family = AF_INET;

    //문자열을 네트워크 주소로 변경
    inet_pton(AF_INET, argv[1], &(servaddr.sin_addr.s_addr));
    servaddr.sin_port = htons(TCP_PORT);

    // 지정한 주소로 접속
    if (connect(csock, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("connect()");
        return -1;
    }
    while (1)
    {
        fgets(mesg, BUFSIZ, stdin);
        if (send(csock, mesg, BUFSIZ, MSG_DONTWAIT) <= 0)
        {
            perror("send()");
            return -1;
        }
        memset(mesg, 0, BUFSIZ);
        if (recv(csock, mesg, BUFSIZ, 0) <= 0)
        {
            perror("recv()");
            return -1;
        }
        printf("Received data : %s", mesg);
    }
    close(csock);
    return 0;
}