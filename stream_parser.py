import os
import sys
import struct
import binascii  # Used to compute local integrity check tags

PIPE_PATH = "/tmp/nodeA_to_attacker"


HEADER_FORMAT = '<IBxH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  

REMAINDER_SIZE = 260


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
            # PHASE 1: READ AND UNPACK FIXED HEADER
            
            if not raw_header:
                print("[*] Stream terminated by transmitter node. Awaiting reconnect...")
                os.close(fd)
                fd = os.open(PIPE_PATH, os.O_RDONLY)
                continue

            magic, packet_type, payload_len = struct.unpack(HEADER_FORMAT, raw_header)
            
            print("┌" + "─"*50)
            print(f"│ [PHASE 1 SUCCESS] Extracted Header Block Telemetry")
            print(f"│  ├── Magic Signature : {hex(magic).upper()}")
            print(f"│  ├── Packet Type Tag : {packet_type}")
            print(f"│  └── Dynamic Payload : {payload_len} bytes calculated")
            print("├" + "─"*50)

            # PHASE 2: CALCULATED SEQUENTIAL READ (Fixed 260-Byte Structure Remainder)


            raw_phase2_block = os.open(fd, REMAINDER_SIZE) if 'os.read' else os.read(fd, REMAINDER_SIZE)
            
            raw_payload_array = raw_phase2_block[:256]
            
            raw_payload_body = raw_payload_array[:payload_len]
            
            # Unpack the final 4-byte sequence number sitting at the end of the structure block
            sequence_counter = struct.unpack('<I', raw_phase2_block[256:260])[0]
            
            crc_checksum = binascii.crc32(raw_payload_body)
            
            decoded_message = raw_payload_body.decode('utf-8', errors='ignore')

            print(f"│ [PHASE 2 SUCCESS] Extracted Remainder Data Blocks")
            print(f"│  ├── String Body     : \"{decoded_message}\"")
            print(f"│  ├── Integrity Code  : {hex(crc_checksum).upper()}")
            print(f"│  └── Sequence Index  : {sequence_counter}")
            print("└" + "─"*50 + "\n")

    except KeyboardInterrupt:
        print("\n[*] Parsing engine closed manually by engineer interrupt.")
    finally:
        os.close(fd)
        print("[*] Channel resource handle closed successfully.")


if __name__ == "__main__":
    execute_two_phase_parser()
