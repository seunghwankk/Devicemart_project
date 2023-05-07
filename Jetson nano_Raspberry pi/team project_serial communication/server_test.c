#include <stdio.h>
#include <string.h>
#include <unistd.h> // ���� ���� �Լ� ���
#include <arpa/inet.h>
#include <sys/socket.h> // �������α׷��� �Լ�����


#define TCP_PORT 5900
#define IP "10.10.141.67"

int main(int argc, char** argv)
{
    int ssock; // ���� ���� ���ϵ�ũ���� ���� ����
    socklen_t clen;
    int n;
    struct sockaddr_in servaddr, cliaddr; // sockaddr_in ����ü ���� ����
    char mesg[BUFSIZ];

    // ���� ���� TCP/IP �������� ����
    if ((ssock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
    {
        perror("socket()");
        return -1;
    }

    // �ּ� ����ü�� �ּ�����
    memset(&servaddr, 0, sizeof(servaddr)); //����ü �迭 �ʱ�ȭ
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(IP);
    servaddr.sin_port = htons(TCP_PORT);

    //bind �Լ��� ����Ͽ� ���������� �ּҼ���
    if (bind(ssock, (struct sockaddr*)&servaddr, sizeof(servaddr)) < 0)
    {
        perror("bind()");
        return -1;
    }

    //���ÿ� �����ϴ� Ŭ���̾�Ʈ�� ó���� ���� ���ť ����
    if (listen(ssock, 8 < 0))
    {
        perror("listen()");
        return -1;
    }

    clen = sizeof(cliaddr);
    do
    {
        //Ŭ���̾�Ʈ�� �����ϸ� ������ ����ϰ� Ŭ���̾�Ʈ ���� ����
        int n, csock = accept(ssock, (struct server_sock*)&cliaddr, &clen);

        //��Ʈ��ũ �ּҸ� ���ڿ��� ����
        inet_ntop(AF_INET, &cliaddr.sin_addr, mesg, BUFSIZ);
        printf("Client is conneted :%s\n", mesg);

        if ((n = read(csock, mesg, BUFSIZ)) <= 0)
            perror("read()");

        printf("Received data : %s", mesg);

        //Ŭ���̾�Ʈ�� buf ���ִ� ���ڿ� ����
        if (write(csock, mesg, n) <= 0)
            perror("write()");

        close(csock);
    } while (strncmp(mesg, "q", 1));
    close(ssock);

    return 0;

 }

