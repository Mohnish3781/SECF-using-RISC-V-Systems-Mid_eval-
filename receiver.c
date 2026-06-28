include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

#include "packet.h"

int main() {

    Packet pkt;

    int fd = open("comm_pipe", O_RDONLY);

    read(fd, &pkt, sizeof(Packet));

    uint16_t checksum = 0;

    for(int i = 0; i < pkt.length; i++)
    {
        checksum += pkt.payload[i];
    }

    close(fd);

    if(pkt.header != MAGIC_HEADER)
    {
        printf("Invalid Header\n");
        return 0;
    }

    if(checksum != pkt.checksum)
    {
        printf("Checksum Error!\n");
        return 0;
    }

    printf("\n===== Packet Received =====\n");

    printf("Header      : 0x%X\n", pkt.header);
    printf("Source ID   : %d\n", pkt.srcID);
    printf("Destination : %d\n", pkt.destID);
    printf("Type        : %d\n", pkt.type);
    printf("Length      : %d\n", pkt.length);
    printf("Payload     : %s\n", pkt.payload);
    printf("Checksum    : %u\n", pkt.checksum);
    printf("Sequence    : %u\n", pkt.seq);
    
    return 0;
    }
