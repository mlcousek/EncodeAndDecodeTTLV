#!/usr/bin/env python

"""
Quick Start Guide for TTLV Encoder
This shows you exactly how to use the encoder step by step
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encode_ttlv import EncodeTTLV, encode_ttlv_structure
from decode_ttlv import DecodeTTLV

def example_1_simple_text():
    """Example 1: Encode a simple text string"""
    print("=== Example 1: Simple Text String ===")
    
    encoder = EncodeTTLV()
    encoder.encode_ttlv('ATTRIBUTE_NAME', 'TEXT_STRING', 'MyTestKey')
    
    hex_result = encoder.get_hex_string()
    print(f"Input: 'MyTestKey'")
    print(f"Output hex: {hex_result}")
    
    # Decode to verify
    decoder = DecodeTTLV(encoder.get_buffer())
    print("Decoded back:")
    decoder.decode()
    print()

def example_2_integer():
    """Example 2: Encode an integer"""
    print("=== Example 2: Integer ===")
    
    encoder = EncodeTTLV()
    encoder.encode_ttlv('CRYPTOGRAPHIC_LENGTH', 'INTEGER', 256)
    
    hex_result = encoder.get_hex_string()
    print(f"Input: 256")
    print(f"Output hex: {hex_result}")
    
    # Decode to verify
    decoder = DecodeTTLV(encoder.get_buffer())
    print("Decoded back:")
    decoder.decode()
    print()

def example_3_enum():
    """Example 3: Encode an enumeration"""
    print("=== Example 3: Enumeration ===")
    
    encoder = EncodeTTLV()
    encoder.encode_ttlv('OPERATION', 'ENUMERATION', 1)  # 1 = DISCOVER_VERSIONS
    
    hex_result = encoder.get_hex_string()
    print(f"Input: 1 (DISCOVER_VERSIONS)")
    print(f"Output hex: {hex_result}")
    
    # Decode to verify
    decoder = DecodeTTLV(encoder.get_buffer())
    print("Decoded back:")
    decoder.decode()
    print()

def example_4_multiple_elements():
    """Example 4: Multiple elements in one encoder"""
    print("=== Example 4: Multiple Elements ===")
    
    encoder = EncodeTTLV()
    encoder.encode_ttlv('ATTRIBUTE_NAME', 'TEXT_STRING', 'TestKey')
    encoder.encode_ttlv('ATTRIBUTE_VALUE', 'INTEGER', 42)
    encoder.encode_ttlv('OPERATION', 'ENUMERATION', 1)
    
    hex_result = encoder.get_hex_string()
    print(f"Input: Three elements")
    print(f"Output hex: {hex_result}")
    
    # Decode to verify
    decoder = DecodeTTLV(encoder.get_buffer())
    print("Decoded back:")
    decoder.decode()
    print()

def example_5_structure_method():
    """Example 5: Using the structure method (recommended)"""
    print("=== Example 5: Structure Method (Recommended) ===")
    
    # Define your data structure
    elements = [
        {'tag': 'ATTRIBUTE_NAME', 'type': 'TEXT_STRING', 'value': 'StructureTest'},
        {'tag': 'CRYPTOGRAPHIC_LENGTH', 'type': 'INTEGER', 'value': 128},
        {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 10}  # GET operation
    ]
    
    # Encode all at once
    encoder = encode_ttlv_structure(elements)
    hex_result = encoder.get_hex_string()
    
    print(f"Input: List of 3 elements")
    print(f"Output hex: {hex_result}")
    
    # Decode to verify
    decoder = DecodeTTLV(encoder.get_buffer())
    print("Decoded back:")
    decoder.decode()
    print()

def example_6_nested_structure():
    """Example 6: Nested structure (like KMIP messages)"""
    print("=== Example 6: Nested Structure ===")
    
    # Create a simple nested structure
    request = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 1}  # DISCOVER_VERSIONS
            ]}
        ]}
    ]
    
    encoder = encode_ttlv_structure(request)
    hex_result = encoder.get_hex_string()
    
    print(f"Input: Nested structure")
    print(f"Output hex: {hex_result}")
    
    # Decode to verify
    decoder = DecodeTTLV(encoder.get_buffer())
    print("Decoded back:")
    decoder.decode()
    print()

if __name__ == '__main__':
    print("TTLV Encoder Quick Start Guide")
    print("=" * 50)
    print()
    
    # Run all examples
    example_1_simple_text()
    example_2_integer()
    example_3_enum()
    example_4_multiple_elements()
    example_5_structure_method()
    example_6_nested_structure()
    
    print("=" * 50)
    print("All examples completed!")
    print()
    print("Next steps:")
    print("1. Replace the example data with your actual data")
    print("2. Use the hex output in your application")
    print("3. Test with the decoder to verify correctness")
