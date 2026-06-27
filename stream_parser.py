#!/usr/bin/env python3
import os
import sys
import struct
import binascii

PIPE_PATH = "/tmp/nodeA_to_attacker"

HEADER_FORMAT = '<IBBBxH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  

REMAINDER_SIZE = 262


def execute_two_phase_parser():
    print("[*] Initializing Phase 2 / Week 3 Parsing Engine (C-Compatible)...")
    
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)
        print(f"[+] Created target communication channel endpoint: {PIPE_PATH}")

    print(f"[*] Listening on {PIPE_PATH}...")
    print("[*] Awaiting node connection (process will block until data writes occur)...")
    
    fd = os.open(PIPE_PATH, os.O_RDONLY)
    print("[+] Link established! Reading binary stream sequentially.\n")

    try:
        while True:
            raw_header = os.read(fd, HEADER_SIZE)
            
            if not raw_header:
                print("[*] Stream terminated by transmitter node. Awaiting reconnect...")
                os.close(fd)
                fd = os.open(PIPE_PATH, os.O_RDONLY)
                continue

            if len(raw_header) < HEADER_SIZE:
                print("[-] Warning: Received partial header chunk. Dropping out-of-sync bytes.")
                continue

            magic, src_id, dest_id, packet_type, payload_len = struct.unpack(HEADER_FORMAT, raw_header)
            
            print("┌" + "─"*60)
            print(f"│ [PHASE 1 SUCCESS] Extracted Header Block Telemetry")
            print(f"│  ├── Magic Signature   : {hex(magic).upper()}")
            print(f"│  ├── Source Node ID    : {src_id}")
            print(f"│  ├── Destination ID    : {dest_id}")
            print(f"│  ├── Packet Type Tag   : {packet_type}")
            print(f"│  └── Dynamic Payload   : {payload_len} bytes calculated")
            print("├" + "─"*60)

            raw_phase2_block = os.read(fd, REMAINDER_SIZE)
            
            if len(raw_phase2_block) < REMAINDER_SIZE:
                print("[-] Warning: Remainder stream truncation detected. Dropping frame.")
                print("└" + "─"*60 + "\n")
                continue
            
            raw_payload_array = raw_phase2_block[:256]
            raw_payload_body = raw_payload_array[:payload_len]
            
            packet_checksum, sequence_counter = struct.unpack('<HI', raw_phase2_block[256:262])
            
            local_arithmetic_checksum = sum(raw_payload_body) & 0xFFFF
            local_crc32 = binascii.crc32(raw_payload_body)
            decoded_message = raw_payload_body.decode('utf-8', errors='ignore')

            print(f"│ [PHASE 2 SUCCESS] Extracted Remainder Data Blocks")
            print(f"│  ├── String Body       : \"{decoded_message}\"")
            print(f"│  ├── Stream Checksum   : {packet_checksum} (Local Calc: {local_arithmetic_checksum})")
            print(f"│  ├── Local CRC32 Tag   : {hex(local_crc32).upper()}")
            print(f"│  └── Sequence Index    : {sequence_counter}")
            print("└" + "─"*60 + "\n")

    except KeyboardInterrupt:
        print("\n[*] Parsing engine closed manually by engineer interrupt.")
    finally:
        os.close(fd)
        print("[*] Channel resource handle closed successfully.")


if __name__ == "__main__":
    execute_two_phase_parser()
