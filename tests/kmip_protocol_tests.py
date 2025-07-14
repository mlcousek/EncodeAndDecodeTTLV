#!/usr/bin/env python

"""
KMIP Protocol Test Suite for TTLV Encoder
This script creates and tests complex KMIP protocol structures like:
- Discover Versions
- Create Key
- Get Key
- Get Attributes
- Add Attribute
- Activate Key
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encode_ttlv import EncodeTTLV, encode_ttlv_structure
from decode_ttlv import DecodeTTLV
import binascii
import time

def create_protocol_version(major=1, minor=1):
    """Helper to create protocol version structure"""
    return [
        {'tag': 'PROTOCOL_VERSION_MAJOR', 'type': 'INTEGER', 'value': major},
        {'tag': 'PROTOCOL_VERSION_MINOR', 'type': 'INTEGER', 'value': minor}
    ]

def create_credential_structure():
    """Helper to create authentication credential structure"""
    return [
        {'tag': 'CREDENTIAL_TYPE', 'type': 'ENUMERATION', 'value': 1},  # USERNAME_AND_PASSWORD
        {'tag': 'CREDENTIAL_VALUE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'USERNAME', 'type': 'TEXT_STRING', 'value': 'vSphere'},
            {'tag': 'PASSWORD', 'type': 'TEXT_STRING', 'value': 'password'}
        ]}
    ]

def create_attribute(name, value, value_type='TEXT_STRING'):
    """Helper to create an attribute structure"""
    return [
        {'tag': 'ATTRIBUTE_NAME', 'type': 'TEXT_STRING', 'value': name},
        {'tag': 'ATTRIBUTE_VALUE', 'type': value_type, 'value': value}
    ]

def test_discover_versions_request():
    """Test 1: Discover Versions Request"""
    print("=== Test 1: Discover Versions Request ===")
    
    # Create the structure as shown in your example
    request_structure = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 1},  # DISCOVER_VERSIONS
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': []}  # Empty payload
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(request_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Request encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        print(f"Hex (first 100 chars): {hex_result[:100]}...")
        
        # Test decoding
        print("\nDecoding result:")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_discover_versions_with_batch_id():
    """Test 2: Discover Versions Request with Batch ID"""
    print("=== Test 2: Discover Versions Request with Batch ID ===")
    
    request_structure = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 1},  # DISCOVER_VERSIONS
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4301000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': []}
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(request_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Request with Batch ID encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        
        # Test decoding
        print("\nDecoding result:")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_create_key_request():
    """Test 3: Create Symmetric Key Request"""
    print("=== Test 3: Create Symmetric Key Request ===")
    
    request_structure = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'AUTHENTICATION', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'CREDENTIAL', 'type': 'STRUCTURE', 'value': create_credential_structure()}
                ]},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 1},  # CREATE
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4301000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'OBJECT_TYPE', 'type': 'ENUMERATION', 'value': 2},  # SYMMETRIC_KEY
                    {'tag': 'TEMPLATE_ATTRIBUTE', 'type': 'STRUCTURE', 'value': [
                        {'tag': 'ATTRIBUTE', 'type': 'STRUCTURE', 'value': create_attribute('Cryptographic Algorithm', 3, 'ENUMERATION')},  # AES
                        {'tag': 'ATTRIBUTE', 'type': 'STRUCTURE', 'value': create_attribute('Cryptographic Usage Mask', 12, 'INTEGER')},
                        {'tag': 'ATTRIBUTE', 'type': 'STRUCTURE', 'value': create_attribute('Cryptographic Length', 256, 'INTEGER')}
                    ]}
                ]}
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(request_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Create Key Request encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        
        # Test decoding
        print("\nDecoding result:")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_get_request():
    """Test 4: Get Key Request"""
    print("=== Test 4: Get Key Request ===")
    
    request_structure = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'AUTHENTICATION', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'CREDENTIAL', 'type': 'STRUCTURE', 'value': create_credential_structure()}
                ]},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 10},  # GET
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4301000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'UNIQUE_IDENTIFIER', 'type': 'TEXT_STRING', 'value': '01000000-7356-8565-621e-08ddba133224'}
                ]}
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(request_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Get Request encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        
        # Test decoding
        print("\nDecoding result:")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_get_attributes_request():
    """Test 5: Get Attributes Request"""
    print("=== Test 5: Get Attributes Request ===")
    
    request_structure = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 8},  # GET_ATTRIBUTES
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4301000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'UNIQUE_IDENTIFIER', 'type': 'TEXT_STRING', 'value': '01000000-7356-8565-621e-08ddba133224'},
                    {'tag': 'ATTRIBUTE_NAME', 'type': 'TEXT_STRING', 'value': 'State'}
                ]}
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(request_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Get Attributes Request encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        
        # Test decoding
        print("\nDecoding result:")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_activate_request():
    """Test 6: Activate Key Request"""
    print("=== Test 6: Activate Key Request ===")
    
    request_structure = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'AUTHENTICATION', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'CREDENTIAL', 'type': 'STRUCTURE', 'value': create_credential_structure()}
                ]},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 12},  # ACTIVATE
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4301000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'UNIQUE_IDENTIFIER', 'type': 'TEXT_STRING', 'value': '01000000-7356-8565-621e-08ddba133224'}
                ]}
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(request_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Activate Request encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        
        # Test decoding
        print("\nDecoding result:")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_add_attribute_request():
    """Test 7: Add Attribute Request (Multiple Batch Items)"""
    print("=== Test 7: Add Attribute Request (Multiple Batch Items) ===")
    
    request_structure = [
        {'tag': 'REQUEST_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'REQUEST_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 3}
            ]},
            # First batch item
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 3},  # ADD_ATTRIBUTE
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4301000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'UNIQUE_IDENTIFIER', 'type': 'TEXT_STRING', 'value': '01000000-7356-8565-621e-08ddba133224'},
                    {'tag': 'ATTRIBUTE', 'type': 'STRUCTURE', 'value': create_attribute('x-Product_Version', '8.0.1 build-21560480')}
                ]}
            ]},
            # Second batch item
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 3},  # ADD_ATTRIBUTE
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4302000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'UNIQUE_IDENTIFIER', 'type': 'TEXT_STRING', 'value': '01000000-7356-8565-621e-08ddba133224'},
                    {'tag': 'ATTRIBUTE', 'type': 'STRUCTURE', 'value': create_attribute('x-Vendor', 'VMware, Inc.')}
                ]}
            ]},
            # Third batch item
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 3},  # ADD_ATTRIBUTE
                {'tag': 'UNIQUE_BATCH_ITEM_ID', 'type': 'BYTE_STRING', 'value': '514c4b4303000000'},
                {'tag': 'REQUEST_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'UNIQUE_IDENTIFIER', 'type': 'TEXT_STRING', 'value': '01000000-7356-8565-621e-08ddba133224'},
                    {'tag': 'ATTRIBUTE', 'type': 'STRUCTURE', 'value': create_attribute('x-Product', 'VMware vSphere')}
                ]}
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(request_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Add Attribute Request (3 batches) encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        
        # Test decoding (might be long, so limit output)
        print("\nDecoding result (showing structure):")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def test_response_structure():
    """Test 8: Response Structure"""
    print("=== Test 8: Simple Response Structure ===")
    
    # Create a simple response structure
    response_structure = [
        {'tag': 'RESPONSE_MESSAGE', 'type': 'STRUCTURE', 'value': [
            {'tag': 'RESPONSE_HEADER', 'type': 'STRUCTURE', 'value': [
                {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)},
                {'tag': 'TIME_STAMP', 'type': 'DATE_TIME', 'value': int(time.time())},
                {'tag': 'BATCH_COUNT', 'type': 'INTEGER', 'value': 1}
            ]},
            {'tag': 'BATCH_ITEM', 'type': 'STRUCTURE', 'value': [
                {'tag': 'OPERATION', 'type': 'ENUMERATION', 'value': 1},  # DISCOVER_VERSIONS
                {'tag': 'RESULT_STATUS', 'type': 'ENUMERATION', 'value': 0},  # SUCCESS
                {'tag': 'RESPONSE_PAYLOAD', 'type': 'STRUCTURE', 'value': [
                    {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(2, 1)},
                    {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 2)},
                    {'tag': 'PROTOCOL_VERSION', 'type': 'STRUCTURE', 'value': create_protocol_version(1, 1)}
                ]}
            ]}
        ]}
    ]
    
    try:
        encoder = encode_ttlv_structure(response_structure)
        hex_result = encoder.get_hex_string()
        
        print(f"Response Structure encoded successfully!")
        print(f"Hex length: {len(hex_result)} characters")
        print(f"Binary length: {len(encoder.get_buffer())} bytes")
        
        # Test decoding
        print("\nDecoding result:")
        decoder = DecodeTTLV(encoder.get_buffer())
        decoder.decode()
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def run_all_tests():
    """Run all KMIP protocol tests"""
    print("KMIP Protocol Test Suite for TTLV Encoder")
    print("=" * 60)
    print()
    
    tests = [
        test_discover_versions_request,
        test_discover_versions_with_batch_id,
        test_create_key_request,
        test_get_request,
        test_get_attributes_request,
        test_activate_request,
        test_add_attribute_request,
        test_response_structure
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print("[PASSED]\n")
            
        except Exception as e:
            failed += 1
            print(f"[FAILED]: {e}\n")
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1].lower()
        if test_name == 'discover':
            test_discover_versions_request()
        elif test_name == 'discover_batch':
            test_discover_versions_with_batch_id()
        elif test_name == 'create':
            test_create_key_request()
        elif test_name == 'get':
            test_get_request()
        elif test_name == 'getattr':
            test_get_attributes_request()
        elif test_name == 'activate':
            test_activate_request()
        elif test_name == 'addattr':
            test_add_attribute_request()
        elif test_name == 'response':
            test_response_structure()
        else:
            print("Available tests: discover, discover_batch, create, get, getattr, activate, addattr, response")
    else:
        # Run all tests
        run_all_tests()
