#!/usr/bin/env python

"""
Test script for structured text format parsing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from encode_ttlv import encode_from_structured_text
from decode_ttlv import DecodeTTLV

def test_structured_format():
    """Test the new structured text format"""
    
    print("Testing Structured Text Format Parser")
    print("=" * 50)
    
    # Test 1: Simple structure
    print("\n=== Test 1: Simple DISCOVER_VERSIONS Request ===")
    
    structured_text1 = """REQUEST_MESSAGE:STRUCTURE(96):stru1
 REQUEST_HEADER:STRUCTURE(56):stru2
  PROTOCOL_VERSION:STRUCTURE(32):stru3
   PROTOCOL_VERSION_MAJOR:INTEGER(4):1
   PROTOCOL_VERSION_MINOR:INTEGER(4):1
  BATCH_COUNT:INTEGER(4):1
 BATCH_ITEM:STRUCTURE(24):stru2
  OPERATION:ENUMERATION(4):DISCOVER_VERSIONS
  REQUEST_PAYLOAD:STRUCTURE(0):stru3"""
    
    print("Input:")
    print(structured_text1)
    print()
    
    encoder1 = encode_from_structured_text(structured_text1)
    if encoder1:
        hex1 = encoder1.get_hex_string()
        print(f"Encoded hex: {hex1}")
        print(f"Length: {len(encoder1.get_buffer())} bytes")
        
        print("\nDecoded back:")
        decoder1 = DecodeTTLV(encoder1.get_buffer())
        decoder1.decode()
    
    # Test 2: More complex structure with different types
    print("\n=== Test 2: Complex Structure with Different Types ===")
    
    structured_text2 = """ATTRIBUTE:STRUCTURE(48):stru1
 ATTRIBUTE_NAME:TEXT_STRING(20):Cryptographic Length
 ATTRIBUTE_VALUE:INTEGER(4):256"""
    
    print("Input:")
    print(structured_text2)
    print()
    
    encoder2 = encode_from_structured_text(structured_text2)
    if encoder2:
        hex2 = encoder2.get_hex_string()
        print(f"Encoded hex: {hex2}")
        print(f"Length: {len(encoder2.get_buffer())} bytes")
        
        print("\nDecoded back:")
        decoder2 = DecodeTTLV(encoder2.get_buffer())
        decoder2.decode()
    
    # Test 3: Test enum value mapping
    print("\n=== Test 3: Test Different Operations ===")
    
    operations = ['CREATE', 'GET', 'DISCOVER_VERSIONS', 'ACTIVATE', 'REGISTER']
    
    for op in operations:
        structured_text = f"""OPERATION:ENUMERATION(4):{op}"""
        print(f"\nTesting: {op}")
        
        encoder = encode_from_structured_text(structured_text)
        if encoder:
            hex_result = encoder.get_hex_string()
            print(f"Hex: {hex_result}")
            
            decoder = DecodeTTLV(encoder.get_buffer())
            decoder.decode()

if __name__ == '__main__':
    test_structured_format()
