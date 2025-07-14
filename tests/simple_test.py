#!/usr/bin/env python

"""
Simple test to verify TTLV encoder fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encode_ttlv import EncodeTTLV, encode_ttlv_structure
from decode_ttlv import DecodeTTLV

def test_simple_enum():
    """Test encoding with integer enum values"""
    print("Testing simple enum encoding...")
    
    try:
        encoder = EncodeTTLV()
        
        # Test with integer enum value (this was causing the error)
        encoder.encode_ttlv('OPERATION', 'ENUMERATION', 1)  # Integer value
        
        hex_result = encoder.get_hex_string()
        print(f"Success! Encoded enum with integer value.")
        print(f"Hex: {hex_result}")
        
        # Test decoding
        decoder = DecodeTTLV(encoder.get_buffer())
        print("Decoding result:")
        decoder.decode()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_simple_structure():
    """Test a simple structure"""
    print("\nTesting simple structure...")
    
    try:
        # Simple structure with integer enums
        structure = [
            {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 1},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]}
        ]
        
        encoder = encode_ttlv_structure(structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Success! Encoded structure.")
        print(f"Hex length: {len(hex_result)} characters")
        
        # Test decoding
        decoder = DecodeTTLV(encoder.get_buffer())
        print("Decoding result:")
        decoder.decode()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("Simple TTLV Encoder Test")
    print("=" * 30)
    
    test1_passed = test_simple_enum()
    test2_passed = test_simple_structure()
    
    print("\n" + "=" * 30)
    if test1_passed and test2_passed:
        print("All tests PASSED! The fixes work correctly.")
    else:
        print("Some tests FAILED. Check the errors above.")
