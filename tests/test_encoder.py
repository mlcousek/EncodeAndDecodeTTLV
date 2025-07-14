#!/usr/bin/env python

"""
Test script for TTLV Encoder
This script demonstrates various ways to use the TTLV encoder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encode_ttlv import EncodeTTLV, encode_ttlv_structure
from decode_ttlv import DecodeTTLV
import binascii

def test_basic_encoding():
    """Test basic TTLV encoding"""
    print("=== Test 1: Basic Text String Encoding ===")
    
    encoder = EncodeTTLV()
    
    # Encode a simple text string
    encoder.encode_ttlv('ATTRIBUTE_NAME', 'TEXT_STRING', 'TestAttribute')
    
    # Get the results
    buffer = encoder.get_buffer()
    hex_string = encoder.get_hex_string()
    
    print(f"Original value: 'TestAttribute'")
    print(f"Encoded hex: {hex_string}")
    print(f"Buffer length: {len(buffer)} bytes")
    
    # Test with decoder
    print("\nDecoding back:")
    decoder = DecodeTTLV(buffer)
    decoder.decode()
    print()

def test_integer_encoding():
    """Test integer encoding"""
    print("=== Test 2: Integer Encoding ===")
    
    encoder = EncodeTTLV()
    
    # Encode an integer
    encoder.encode_ttlv('ATTRIBUTE_VALUE', 'INTEGER', 42)
    
    buffer = encoder.get_buffer()
    hex_string = encoder.get_hex_string()
    
    print(f"Original value: 42")
    print(f"Encoded hex: {hex_string}")
    print(f"Buffer length: {len(buffer)} bytes")
    
    # Test with decoder
    print("\nDecoding back:")
    decoder = DecodeTTLV(buffer)
    decoder.decode()
    print()

def test_multiple_elements():
    """Test encoding multiple elements"""
    print("=== Test 3: Multiple Elements ===") 
    
    # Method 1: Using individual calls
    encoder = EncodeTTLV()
    encoder.encode_ttlv('ATTRIBUTE_NAME', 'TEXT_STRING', 'MyAttribute')
    encoder.encode_ttlv('ATTRIBUTE_VALUE', 'INTEGER', 123)
    
    buffer = encoder.get_buffer()
    hex_string = encoder.get_hex_string()
    
    print("Method 1 - Individual calls:")
    print(f"Encoded hex: {hex_string}")
    print(f"Buffer length: {len(buffer)} bytes")
    
    print("\nDecoding back:")
    decoder = DecodeTTLV(buffer)
    decoder.decode()
    
    # Method 2: Using structure helper
    print("\nMethod 2 - Using structure helper:")
    elements = [
        {'tag': 'ATTRIBUTE_NAME', 'type': 'TEXT_STRING', 'value': 'AnotherAttribute'},
        {'tag': 'ATTRIBUTE_VALUE', 'type': 'INTEGER', 'value': 456}
    ]
    
    encoder2 = encode_ttlv_structure(elements)
    buffer2 = encoder2.get_buffer()
    hex_string2 = encoder2.get_hex_string()
    
    print(f"Encoded hex: {hex_string2}")
    print(f"Buffer length: {len(buffer2)} bytes")
    
    print("\nDecoding back:")
    decoder2 = DecodeTTLV(buffer2)
    decoder2.decode()
    print()

def test_different_types():
    """Test different data types"""
    print("=== Test 4: Different Data Types ===")
    
    encoder = EncodeTTLV()
    
    # Test different types
    test_cases = [
        ('ATTRIBUTE_NAME', 'TEXT_STRING', 'BooleanTest'),
        ('ATTRIBUTE_VALUE', 'BOOLEAN', True),
        ('UNIQUE_IDENTIFIER', 'TEXT_STRING', 'test-id-123'),
        ('CRYPTOGRAPHIC_LENGTH', 'INTEGER', 256),
    ]
    
    for tag, type_name, value in test_cases:
        try:
            encoder_single = EncodeTTLV()
            encoder_single.encode_ttlv(tag, type_name, value)
            hex_result = encoder_single.get_hex_string()
            
            print(f"Tag: {tag}, Type: {type_name}, Value: {value}")
            print(f"Hex: {hex_result}")
            
            # Decode to verify
            decoder = DecodeTTLV(encoder_single.get_buffer())
            print("Decoded:")
            decoder.decode()
            print("-" * 50)
            
        except Exception as e:
            print(f"Error encoding {tag}: {e}")
            print("-" * 50)

def test_hex_string_input():
    """Test encoding/decoding with hex string input (like your decoder example)"""
    print("=== Test 5: Hex String Round Trip ===")
    
    # Create some test data
    encoder = EncodeTTLV()
    encoder.encode_ttlv('ATTRIBUTE_NAME', 'TEXT_STRING', 'HexTest')
    encoder.encode_ttlv('ATTRIBUTE_VALUE', 'INTEGER', 999)
    
    # Get hex string
    hex_string = encoder.get_hex_string()
    print(f"Generated hex string: {hex_string}")
    
    # Convert hex string back to binary (like your decoder's main function)
    binary_data = bytearray()
    for i in range(0, len(hex_string), 2):
        byte_str = hex_string[i:i+2]
        binary_data.append(int(byte_str, 16))
    
    # Decode the reconstructed binary
    print("\nDecoding reconstructed binary:")
    decoder = DecodeTTLV(binary_data)
    decoder.decode()
    print()

def test_structured_text_format():
    """Test parsing and encoding from structured text format"""
    print("=== Test 6: Structured Text Format ===")
    
    # Test with the format you provided
    structured_text = """REQUEST_MESSAGE:STRUCTURE(96):stru1
 REQUEST_HEADER:STRUCTURE(56):stru2
  PROTOCOL_VERSION:STRUCTURE(32):stru3
   PROTOCOL_VERSION_MAJOR:INTEGER(4):1
   PROTOCOL_VERSION_MINOR:INTEGER(4):1
  BATCH_COUNT:INTEGER(4):1
 BATCH_ITEM:STRUCTURE(24):stru2
  OPERATION:ENUMERATION(4):DISCOVER_VERSIONS
  REQUEST_PAYLOAD:STRUCTURE(0):stru3"""
    
    print("Input structured text:")
    print(structured_text)
    print()
    
    try:
        # Import the new function
        from encode_ttlv import encode_from_structured_text
        
        # Encode from structured text
        encoder = encode_from_structured_text(structured_text)
        
        if encoder:
            hex_result = encoder.get_hex_string()
            buffer = encoder.get_buffer()
            
            print(f"Successfully encoded from structured text!")
            print(f"Hex output: {hex_result}")
            print(f"Buffer length: {len(buffer)} bytes")
            
            # Test decoding back
            print("\nDecoding back:")
            decoder = DecodeTTLV(buffer)
            decoder.decode()
            
            print("\n" + "="*60)
            print("✅ NEW FEATURE: Structured Text Format Support")
            print("="*60)
            print("You can now use structured text files with the encoder!")
            print()
            print("Usage examples:")
            print("1. Command line:")
            print("   python encode_ttlv.py --structured my_structure.txt --decode")
            print()
            print("2. In Python code:")
            print("   from encode_ttlv import encode_from_structured_text")
            print("   encoder = encode_from_structured_text(structured_text)")
            print("   hex_output = encoder.get_hex_string()")
            print()
            print("3. From file:")
            print("   from encode_ttlv import load_from_structured_text_file")
            print("   elements = load_from_structured_text_file('my_file.txt')")
            print("   encoder = encode_ttlv_structure(elements)")
            print("="*60)
        else:
            print("Failed to encode from structured text")
            
    except Exception as e:
        print(f"Error testing structured text format: {e}")
        import traceback
        traceback.print_exc()
    
    print()

if __name__ == '__main__':
    print("TTLV Encoder Test Suite")
    print("=" * 50)
    
    try:
        test_basic_encoding()
        test_integer_encoding()
        test_multiple_elements()
        test_different_types()
        test_hex_string_input()
        test_structured_text_format()
        
        print("All tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
