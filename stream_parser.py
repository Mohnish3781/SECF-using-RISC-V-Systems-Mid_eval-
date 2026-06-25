import os
import sys
import struct
import binascii  # Used to compute local integrity check tags

# PATH NOTE: Your unchanged C code looks for a file named "comm_pipe" in its 
# local execution directory. Ensure this path points to the exact same pipe file.
# You can change this string to "comm_pipe" if running scripts in the same folder.
PIPE_PATH = "/tmp/nodeA_to_attacker"

# --- PROTOCOL STRUCT SPECIFICATIONS (SYNCED TO UNCHANGED C MEMORY MAP) ---
# Phase 1 Format: Little-Endian (<) | Magic (4B 'I') | Type (1B 'B') | 1-Byte Alignment Pad ('x') | Length (2B 'H')
HEADER_FORMAT = '<IBxH'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # Evaluates to exactly 8 bytes

# Total size of your C struct is 268 bytes. 
# The remaining block size after Phase 1 is exactly 268 - 8 = 260 bytes.
REMAINDER_SIZE = 260


def execute_two_phase_parser():
    print("[*] Initializing Phase 2 / Week 3 Parsing Engine (C-Compatible)...")
    
    # Structural Safety Check: Verify or instantiate the target POSIX FIFO
    if not os.path.exists(PIPE_PATH):
        os.mkfifo(PIPE_PATH)
        print(f"[+] Created target communication channel endpoint: {PIPE_PATH}")

    print(f"[*] Listening on {PIPE_PATH}...")
    print("[*] Awaiting node connection (process will block until data writes occur)...")
    
    # Low-level system open call returns an explicit integer file descriptor (fd)
    fd = os.open(PIPE_PATH, os.O_RDONLY)
    print("[+] Link established! Reading binary stream sequentially.\n")

    try:
        while True:
            # =================================================================
            # PHASE 1: READ AND UNPACK FIXED HEADER
            # =================================================================
            # Request exactly 8 bytes (accounted for alignment padding) out of the pipe
            raw_header = os.read(fd, HEADER_SIZE)
            
            # Catch end-of-stream descriptor when the sender process exits or disconnects
            if not raw_header:
                print("[*] Stream terminated by transmitter node. Awaiting reconnect...")
                os.close(fd)
                fd = os.open(PIPE_PATH, os.O_RDONLY)
                continue

            # Unpack raw binary data using explicit Little-Endian structural alignment
            magic, packet_type, payload_len = struct.unpack(HEADER_FORMAT, raw_header)
            
            print("┌" + "─"*50)
            print(f"│ [PHASE 1 SUCCESS] Extracted Header Block Telemetry")
            print(f"│  ├── Magic Signature : {hex(magic).upper()}")
            print(f"│  ├── Packet Type Tag : {packet_type}")
            print(f"│  └── Dynamic Payload : {payload_len} bytes calculated")
            print("├" + "─"*50)

            # =================================================================
            # PHASE 2: CALCULATED SEQUENTIAL READ (Fixed 260-Byte Structure Remainder)
            # =================================================================
            # To keep the pipe clean for subsequent transmissions, we must drain the 
            # remainder of the 268-byte fixed structure sent by write(fd, &pkt, sizeof(Packet))
            raw_phase2_block = os.open(fd, REMAINDER_SIZE) if 'os.read' else os.read(fd, REMAINDER_SIZE)
            
            # The first 256 bytes of Phase 2 belong to the payload array buffer
            raw_payload_array = raw_phase2_block[:256]
            
            # Slice out only the active cleartext message characters up to payload_len
            raw_payload_body = raw_payload_array[:payload_len]
            
            # Unpack the final 4-byte sequence number sitting at the end of the structure block
            sequence_counter = struct.unpack('<I', raw_phase2_block[256:260])[0]
            
            # Since your unchanged C structure does not contain a hardcoded CRC field,
            # we dynamically compute a real-time CRC-32 checksum in Python over the 
            # verified message string to supply your reporting telemetry interface.
            crc_checksum = binascii.crc32(raw_payload_body)
            
            # Convert raw payload back to cleartext text characters for interpretation
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