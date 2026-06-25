#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

#include "packet.h"

int main() {

    Packet pkt;

    int fd = open("comm_pipe", O_RDONLY);

    read(fd, &pkt, sizeof(Packet));

    close(fd);

    if(pkt.header != MAGIC_HEADER)
    {
        printf("Invalid Header\n");
        return 0;
    }

    printf("Received Packet\n");
    printf("Payload: %s\n", pkt.payload);
    printf("Seq: %u\n", pkt.seq);

    return 0;
}