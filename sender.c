#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#include "packet.h"

int main() {

    Packet pkt;

    pkt.header = MAGIC_HEADER;
    pkt.type = 1;
    pkt.seq = 1;

    strcpy((char*)pkt.payload, "HELLO FROM NODE A");
    pkt.length = strlen((char*)pkt.payload);

    int fd = open("comm_pipe", O_WRONLY);

    write(fd, &pkt, sizeof(Packet));

    close(fd);

    printf("Packet Sent\n");

    return 0;
}