from __future__ import print_function

from kmip.core import enums

import binascii
import struct
import time


class EncodeTTLV(object):
    def __init__(self):
        self.buffer = bytearray()
        self.attribute_name = "".encode("utf-8")
        
    def get_buffer(self):
        """Return the encoded TTLV buffer"""
        return self.buffer
    
    def get_hex_string(self):
        """Return the encoded TTLV buffer as a hex string"""
        return binascii.hexlify(self.buffer).decode('utf-8')
    
    def encode_ttlv(self, tag, type_name, value):
        """Encode a single TTLV element"""
        # Encode the tag (3 bytes: 0x42 + 2-byte tag value)
        tag_bytes = self._encode_tag(tag)
        
        # Encode the type (1 byte)
        type_byte = self._encode_type(type_name)
        
        # Encode the value and get its size
        value_bytes, size = self._encode_value(type_name, value, tag)
        
        # Encode the size (4 bytes)
        size_bytes = struct.pack(">I", size)
        
        # Combine all parts
        self.buffer.extend(tag_bytes)
        self.buffer.extend(type_byte)
        self.buffer.extend(size_bytes)
        self.buffer.extend(value_bytes)
        
        return len(tag_bytes) + len(type_byte) + len(size_bytes) + len(value_bytes)
    
    def _encode_tag(self, tag):
        """Encode tag as 3 bytes: 0x42 + 2-byte tag value"""
        tag_value = self._get_enum_value('Tags', tag)
        # Extract the 2-byte tag value from the 3-byte combined value
        tag_lower = tag_value & 0xFFFF
        return struct.pack(">Bh", 0x42, tag_lower)
    
    def _encode_type(self, type_name):
        """Encode type as 1 byte"""
        type_value = self._get_enum_value('Types', type_name)
        return struct.pack(">B", type_value)
    
    def _encode_value(self, type_name, value, tag):
        """Encode value based on type and return (value_bytes, actual_size)"""
        if type_name == 'STRUCTURE':
            return self._encode_type_struct(value)
        elif type_name == 'INTEGER':
            return self._encode_type_int4(value)
        elif type_name == 'LONG_INTEGER':
            return self._encode_type_long(value)
        elif type_name == 'BIG_INTEGER':
            return self._encode_type_bigint(value)
        elif type_name == 'ENUMERATION':
            return self._encode_type_enum(value, tag)
        elif type_name == 'BOOLEAN':
            return self._encode_type_bool(value)
        elif type_name == 'TEXT_STRING':
            return self._encode_type_text(value, tag)
        elif type_name == 'BYTE_STRING':
            return self._encode_type_bytes(value)
        elif type_name == 'DATE_TIME':
            return self._encode_type_date(value)
        elif type_name == 'INTERVAL':
            return self._encode_type_inter(value)
        elif type_name == 'DATE_TIME_EXTENDED':
            return self._encode_type_exdate(value)
        else:
            raise Exception("Unsupported type: {0}".format(type_name))
    
    def _encode_type_struct(self, value):
        """Encode structure - value should be a list of TTLV elements"""
        if isinstance(value, (list, tuple)):
            # If value is a list of TTLV elements, encode them
            struct_buffer = bytearray()
            for element in value:
                if isinstance(element, dict) and 'tag' in element and 'type' in element and 'value' in element:
                    encoder = EncodeTTLV()
                    encoder.encode_ttlv(element['tag'], element['type'], element['value'])
                    struct_buffer.extend(encoder.get_buffer())
            return struct_buffer, len(struct_buffer)
        elif isinstance(value, bytes):
            # If value is already encoded bytes
            return value, len(value)
        else:
            # Empty structure
            return b'', 0
    
    def _encode_type_int4(self, value):
        """Encode 32-bit integer with 4-byte padding"""
        data = struct.pack(">i", int(value))
        padded_data = data + b'\x00' * 4  # 4 bytes padding
        return padded_data, 4  # actual size is 4, not 8
    
    def _encode_type_long(self, value):
        """Encode 64-bit long integer"""
        data = struct.pack(">q", int(value))
        return data, 8
    
    def _encode_type_bigint(self, value):
        """Encode big integer (placeholder implementation)"""
        # For now, treat as 64-bit long
        data = struct.pack(">q", int(value))
        return data, 8
    
    def _encode_type_enum(self, value, tag):
        """Encode enumeration with 4-byte padding"""
        # If value is already an integer, use it directly
        if isinstance(value, int):
            enum_value = value
        elif tag == "ATTRIBUTE_VALUE":
            enum_value = self._get_enum_value_attr(tag, value)
        else:
            enum_value = self._get_enum_value(tag, value)
        data = struct.pack(">I", enum_value)
        padded_data = data + b'\x00' * 4  # 4 bytes padding
        return padded_data, 4  # actual size is 4, not 8
    
    def _encode_type_bool(self, value):
        """Encode boolean as 8-byte value"""
        bool_value = 1 if value else 0
        data = struct.pack(">Q", bool_value)
        return data, 8
    
    def _encode_type_text(self, value, tag):
        """Encode text string with padding to 8-byte boundary"""
        if isinstance(value, str):
            text_bytes = value.encode('utf-8')
        else:
            text_bytes = bytes(value)
        
        if tag == "ATTRIBUTE_NAME":
            self.attribute_name = text_bytes
            
        actual_size = len(text_bytes)
        padding = (8 - actual_size % 8) % 8
        padded_data = text_bytes + b'\x00' * padding
        return padded_data, actual_size
    
    def _encode_type_bytes(self, value):
        """Encode byte string with padding to 8-byte boundary"""
        if isinstance(value, str):
            # Assume hex string
            byte_data = binascii.unhexlify(value)
        else:
            byte_data = bytes(value)
            
        actual_size = len(byte_data)
        padding = (8 - actual_size % 8) % 8
        padded_data = byte_data + b'\x00' * padding
        return padded_data, actual_size
    
    def _encode_type_date(self, value):
        """Encode date/time as 8-byte timestamp"""
        if isinstance(value, (int, float)):
            timestamp = int(value)
        elif isinstance(value, str):
            # Parse time string to timestamp
            timestamp = int(time.mktime(time.strptime(value)))
        else:
            timestamp = int(time.time())
            
        data = struct.pack(">Q", timestamp)
        return data, 8
    
    def _encode_type_inter(self, value):
        """Encode interval as 32-bit integer with 4-byte padding"""
        data = struct.pack(">i", int(value))
        padded_data = data + b'\x00' * 4  # 4 bytes padding
        return padded_data, 4  # actual size is 4, not 8
    
    def _encode_type_exdate(self, value):
        """Encode extended date/time as 8-byte timestamp"""
        return self._encode_type_date(value)
    
    def _get_enum_value(self, enum_name, name):
        """Get enum value by name"""
        # If name is already an integer, return it directly
        if isinstance(name, int):
            return name
        
        # Special handling for common enum values
        if enum_name == 'ATTRIBUTE_VALUE':
            # Common attribute value enums
            common_mappings = {
                'AES': 3,
                'DES': 1,
                'TRIPLE_DES': 2,
                'RSA': 4,
                'DSA': 5,
                'SYMMETRIC_KEY': 2,
                'PUBLIC_KEY': 3,
                'PRIVATE_KEY': 4,
                'CERTIFICATE': 6,
                'USERNAME_AND_PASSWORD': 1,
                'DEVICE_SPECIFIC': 2
            }
            if name in common_mappings:
                return common_mappings[name]
        
        # Special mappings for other common enums
        if enum_name == 'CREDENTIAL_TYPE':
            credential_mappings = {
                'USERNAME_AND_PASSWORD': 1,
                'DEVICE_SPECIFIC': 2
            }
            if name in credential_mappings:
                return credential_mappings[name]
        
        if enum_name == 'OBJECT_TYPE':
            object_mappings = {
                'CERTIFICATE': 1,
                'SYMMETRIC_KEY': 2,
                'PUBLIC_KEY': 3,
                'PRIVATE_KEY': 4,
                'SPLIT_KEY': 5,
                'TEMPLATE': 6,
                'SECRET_DATA': 7,
                'OPAQUE_DATA': 8
            }
            if name in object_mappings:
                return object_mappings[name]
        
        if enum_name == 'OBJECT_GROUP':
            group_mappings = {
                'DEFAULT': 0,
                'NONE': 0
            }
            if name in group_mappings:
                return group_mappings[name]
            
        type_name = ''.join(x.capitalize() or '_' for x in enum_name.split('_'))
        
        try:
            enum_class = getattr(enums, type_name)
            
            # Try to get the enum value by name
            if hasattr(enum_class, str(name)):
                enum_val = getattr(enum_class, str(name))
                if hasattr(enum_val, 'value'):
                    return enum_val.value
            
            # If not found by name, search through all enum values
            for attr_name in dir(enum_class):
                enum_val = getattr(enum_class, attr_name)
                if hasattr(enum_val, 'name') and enum_val.name == str(name):
                    return enum_val.value
                    
        except AttributeError:
            # If enum class doesn't exist, try some fallbacks
            pass
                
        raise ValueError("Enum value '{0}' not found in {1}".format(name, enum_name))
    
    def _get_enum_value_attr(self, tag, name):
        """Get attribute enum value by name using stored attribute name"""
        # If name is already an integer, return it directly
        if isinstance(name, int):
            return name
        
        # Special handling for common KMIP state values
        state_mappings = {
            'PRE_ACTIVE': 1,
            'ACTIVE': 2,
            'DEACTIVATED': 3,
            'COMPROMISED': 4,
            'DESTROYED': 5,
            'DESTROYED_COMPROMISED': 6
        }
        
        if str(name) in state_mappings:
            return state_mappings[str(name)]
        
        # Debug: check if attribute_name is set
        if not hasattr(self, 'attribute_name') or not self.attribute_name:
            # Fallback: try to get enum value directly from tag
            return self._get_enum_value(tag, name)
            
        try:
            type_name = self.attribute_name.decode('utf-8').replace(' ', '')
            
            # Debug: check if type_name is empty
            if not type_name:
                return self._get_enum_value(tag, name)
                
            # Try common enum classes for attribute values
            enum_classes_to_try = [type_name, 'State', 'CryptographicUsageMask', 'CryptographicAlgorithm']
            
            for enum_class_name in enum_classes_to_try:
                try:
                    enum_class = getattr(enums, enum_class_name)
                    
                    # Try to get the enum value by name
                    if hasattr(enum_class, str(name)):
                        enum_val = getattr(enum_class, str(name))
                        if hasattr(enum_val, 'value'):
                            return enum_val.value
                    
                    # If not found by name, search through all enum values
                    for attr_name in dir(enum_class):
                        enum_val = getattr(enum_class, attr_name)
                        if hasattr(enum_val, 'name') and enum_val.name == str(name):
                            return enum_val.value
                except AttributeError:
                    continue  # Try next enum class
                    
            raise ValueError("Enum value '{0}' not found in attribute enums".format(name))
            
        except (AttributeError, UnicodeDecodeError) as e:
            # Fallback to regular enum lookup if attribute-based lookup fails
            return self._get_enum_value(tag, name)


def encode_ttlv_structure(elements):
    """
    Helper function to encode a list of TTLV elements
    
    Args:
        elements: List of dictionaries with 'tag', 'type', and 'value' keys
    
    Returns:
        EncodeTTLV object with encoded buffer
    """
    encoder = EncodeTTLV()
    
    for element in elements:
        if not isinstance(element, dict):
            raise ValueError("Each element must be a dictionary with 'tag', 'type', and 'value' keys")
        
        if 'tag' not in element or 'type' not in element or 'value' not in element:
            raise ValueError("Each element must have 'tag', 'type', and 'value' keys")
        
        encoder.encode_ttlv(element['tag'], element['type'], element['value'])
    
    return encoder


def load_from_json_file(filename):
    """Load TTLV structure from JSON file"""
    import json
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON file {filename}: {e}")
        return None

def load_from_text_file(filename):
    """Load TTLV structure from text file (simple format)"""
    elements = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Expected format: TAG,TYPE,VALUE
                parts = line.split(',', 2)
                if len(parts) != 3:
                    print(f"Warning: Invalid line {line_num}: {line}")
                    continue
                
                tag, type_name, value = parts
                tag = tag.strip()
                type_name = type_name.strip()
                value = value.strip()
                
                # Convert value based on type
                if type_name == 'INTEGER':
                    value = int(value)
                elif type_name == 'BOOLEAN':
                    value = value.lower() in ('true', '1', 'yes')
                elif type_name == 'ENUMERATION':
                    try:
                        value = int(value)
                    except ValueError:
                        pass  # Keep as string
                
                elements.append({
                    'tag': tag,
                    'type': type_name,
                    'value': value
                })
        
        return elements
    except Exception as e:
        print(f"Error loading text file {filename}: {e}")
        return None

def save_output(encoder, output_file=None, format='hex'):
    """Save encoder output to file or print to console"""
    
    if output_file:
        # When writing to file, always write binary data
        try:
            with open(output_file, 'wb') as f:
                f.write(encoder.get_buffer())
            print(f"Binary output saved to: {output_file}")
        except Exception as e:
            print(f"Error saving to {output_file}: {e}")
    else:
        # When printing to console, respect the format parameter
        if format.lower() == 'binary':
            print("Binary output (hex representation):")
            print(binascii.hexlify(encoder.get_buffer()).decode('utf-8'))
        else:
            print("Hex output:")
            print(encoder.get_hex_string())

def show_usage():
    """Show usage information"""
    print("TTLV Encoder - Usage:")
    print("=" * 50)
    print()
    print("1. Test mode:")
    print("   python encode_ttlv.py test")
    print()
    print("2. From JSON file:")
    print("   python encode_ttlv.py --json input.json [--output output.bin] [--format hex|binary]")
    print()
    print("3. From text file (CSV format):")
    print("   python encode_ttlv.py --text input.txt [--output output.bin] [--format hex|binary]")
    print()
    print("4. From structured text file (with indentation):")
    print("   python encode_ttlv.py --structured input.txt [--output output.bin] [--format hex|binary]")
    print()
    print("5. Interactive mode:")
    print("   python encode_ttlv.py --interactive")
    print()
    print("Note: Files are always saved in binary format. --format only affects console output.")
    print()
    print("Text file format (CSV - one element per line):")
    print("TAG,TYPE,VALUE")
    print("Example:")
    print("ATTRIBUTE_NAME,TEXT_STRING,MyAttribute")
    print("ATTRIBUTE_VALUE,INTEGER,42")
    print("OPERATION,ENUMERATION,CREATE")
    print()
    print("Structured text file format (with indentation):")
    print("REQUEST_MESSAGE:STRUCTURE(96):stru1")
    print(" REQUEST_HEADER:STRUCTURE(56):stru2")
    print("  PROTOCOL_VERSION:STRUCTURE(32):stru3")
    print("   PROTOCOL_VERSION_MAJOR:INTEGER(4):1")
    print("   PROTOCOL_VERSION_MINOR:INTEGER(4):1")
    print("  BATCH_COUNT:INTEGER(4):1")
    print(" BATCH_ITEM:STRUCTURE(24):stru2")
    print("  OPERATION:ENUMERATION(4):DISCOVER_VERSIONS")
    print("  REQUEST_PAYLOAD:STRUCTURE(0):stru3")
    print()
    print("JSON file format:")
    print('[')
    print('  {"tag": "ATTRIBUTE_NAME", "type": "TEXT_STRING", "value": "MyAttribute"},')
    print('  {"tag": "ATTRIBUTE_VALUE", "type": "INTEGER", "value": 42}')
    print(']')

def parse_structured_text(text_content):
    """
    Parse structured TTLV text format with indentation
    
    Example format:
    REQUEST_MESSAGE:STRUCTURE(96):stru1
     REQUEST_HEADER:STRUCTURE(56):stru2
      PROTOCOL_VERSION:STRUCTURE(32):stru3
       PROTOCOL_VERSION_MAJOR:INTEGER(4):1
       PROTOCOL_VERSION_MINOR:INTEGER(4):1
      BATCH_COUNT:INTEGER(4):1
     BATCH_ITEM:STRUCTURE(24):stru2
      OPERATION:ENUMERATION(4):DISCOVER_VERSIONS
      REQUEST_PAYLOAD:STRUCTURE(0):stru3
    
    Returns: List of elements in hierarchical structure
    """
    lines = text_content.strip().split('\n')
    elements = []
    stack = []  # Stack to track nested structures
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        # Count leading spaces to determine indentation level
        indent_level = len(line) - len(line.lstrip())
        line_content = line.strip()
        
        # Parse the line format: TAG:TYPE(length):value
        try:
            # Split by the first colon to get tag and rest
            if ':' not in line_content:
                continue
                
            tag_part, rest = line_content.split(':', 1)
            tag = tag_part.strip()
            
            # Extract type and length
            if '(' not in rest or ')' not in rest:
                continue
                
            type_part, value_part = rest.split(')', 1)
            type_with_length = type_part + ')'
            
            # Parse type and length
            type_name = type_with_length.split('(')[0].strip()
            length_str = type_with_length.split('(')[1].rstrip(')')
            
            # Parse value (after the colon following the type)
            if ':' in value_part:
                value = value_part.split(':', 1)[1].strip()
            else:
                value = value_part.strip()
            
            # Convert value based on type
            if type_name == 'INTEGER':
                try:
                    value = int(value)
                except ValueError:
                    value = 0
            elif type_name == 'BOOLEAN':
                value = value.lower() in ('true', '1', 'yes')
            elif type_name == 'ENUMERATION':
                # Try to convert to integer, keep as string if it fails
                try:
                    value = int(value)
                except ValueError:
                    # Could be enum name like DISCOVER_VERSIONS
                    # For OPERATION tag, map common enum names using PyKMIP values
                    if tag == 'OPERATION':
                        enum_mapping = {
                            'CREATE': 1,
                            'CREATE_KEY_PAIR': 2,
                            'REGISTER': 3,
                            'REKEY': 4,
                            'DERIVE_KEY': 5,
                            'CERTIFY': 6,
                            'RECERTIFY': 7,
                            'LOCATE': 8,
                            'CHECK': 9,
                            'GET': 10,
                            'GET_ATTRIBUTES': 11,
                            'GET_ATTRIBUTE_LIST': 12,
                            'ADD_ATTRIBUTE': 13,
                            'MODIFY_ATTRIBUTE': 14,
                            'DELETE_ATTRIBUTE': 15,
                            'OBTAIN_LEASE': 16,
                            'GET_USAGE_ALLOCATION': 17,
                            'ACTIVATE': 18,
                            'REVOKE': 19,
                            'DESTROY': 20,
                            'ARCHIVE': 21,
                            'RECOVER': 22,
                            'VALIDATE': 23,
                            'QUERY': 24,
                            'CANCEL': 25,
                            'POLL': 26,
                            'NOTIFY': 27,
                            'PUT': 28,
                            'REKEY_KEY_PAIR': 29,
                            'DISCOVER_VERSIONS': 30,
                            'ENCRYPT': 31,
                            'DECRYPT': 32,
                            'SIGN': 33,
                            'SIGNATURE_VERIFY': 34,
                            'MAC': 35,
                            'MAC_VERIFY': 36,
                            'RNG_RETRIEVE': 37,
                            'RNG_SEED': 38,
                            'HASH': 39,
                            'CREATE_SPLIT_KEY': 40,
                            'JOIN_SPLIT_KEY': 41,
                            'IMPORT': 42,
                            'EXPORT': 43,
                            'LOG': 44,
                            'LOGIN': 45,
                            'LOGOUT': 46,
                            'DELEGATED_LOGIN': 47,
                            'ADJUST_ATTRIBUTE': 48,
                            'SET_ATTRIBUTE': 49,
                            'SET_ENDPOINT_ROLE': 50,
                            'PKCS_11': 51,
                            'INTEROP': 52,
                            'REPROVISION': 53
                        }
                        if value in enum_mapping:
                            value = enum_mapping[value]
                    pass
            elif type_name == 'STRUCTURE':
                # For structures, we'll handle the value differently
                # Value might be like "stru1" or could be empty
                if value.startswith('stru'):
                    value = None  # We'll build this from child elements
            elif type_name == 'BYTE_STRING':
                # Handle byte strings (might be hex format)
                if value.startswith('b\'') and value.endswith('\''):
                    # Python byte string format: b'514c4b4301000000'
                    hex_value = value[2:-1]  # Remove b' and '
                    value = bytes.fromhex(hex_value)
                elif len(value) % 2 == 0 and all(c in '0123456789abcdefABCDEF' for c in value):
                    # Plain hex string
                    value = bytes.fromhex(value)
            elif type_name == 'TEXT_STRING':
                # Handle text strings that might be in bytearray format
                if value.startswith('bytearray(b\'') and value.endswith('\')'):
                    # Extract the string from bytearray(b'text')
                    text_value = value[12:-2]  # Remove bytearray(b' and ')
                    value = text_value
                elif value.startswith('b\'') and value.endswith('\''):
                    # Python byte string format: b'text'
                    value = value[2:-1]  # Remove b' and '
            
            # Adjust stack based on indentation
            while len(stack) > indent_level // 1:  # Assuming 1 space per level
                stack.pop()
            
            element = {
                'tag': tag,
                'type': type_name,
                'value': value,
                'indent_level': indent_level,
                'children': []
            }
            
            # Add to parent structure if we're nested
            if stack:
                parent = stack[-1]
                parent['children'].append(element)
            else:
                elements.append(element)
            
            # If this is a structure, add it to the stack for potential children
            if type_name == 'STRUCTURE':
                stack.append(element)
                
        except Exception as e:
            print(f"Warning: Could not parse line {line_num}: {line.strip()} - {e}")
            continue
    
    return elements

def convert_structured_to_flat(structured_elements):
    """
    Convert hierarchical structured elements to flat list for encoding
    """
    flat_elements = []
    
    def process_element(element):
        if element['type'] == 'STRUCTURE':
            # For structures, we need to encode children first, then the structure
            child_elements = []
            for child in element.get('children', []):
                child_result = process_element(child)
                if isinstance(child_result, list):
                    child_elements.extend(child_result)
                else:
                    child_elements.append(child_result)
            
            # Create the structure element
            struct_element = {
                'tag': element['tag'],
                'type': 'STRUCTURE',
                'value': child_elements  # Structure value is its children
            }
            return struct_element
        else:
            # For non-structure elements, return as-is
            return {
                'tag': element['tag'],
                'type': element['type'],
                'value': element['value']
            }
    
    for element in structured_elements:
        result = process_element(element)
        flat_elements.append(result)
    
    return flat_elements

def load_from_structured_text_file(filename):
    """Load TTLV structure from structured text file format"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        structured_elements = parse_structured_text(content)
        flat_elements = convert_structured_to_flat(structured_elements)
        return flat_elements
    except Exception as e:
        print(f"Error loading structured text file {filename}: {e}")
        return None

def encode_from_structured_text(text_content):
    """
    Encode TTLV from structured text format
    
    Args:
        text_content: String containing the structured TTLV format
        
    Returns:
        EncodeTTLV object with encoded data
    """
    structured_elements = parse_structured_text(text_content)
    flat_elements = convert_structured_to_flat(structured_elements)
    
    return encode_ttlv_structure(flat_elements)


if __name__ == '__main__':
    import sys
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='TTLV Encoder')
    parser.add_argument('--json', help='Input JSON file')
    parser.add_argument('--text', help='Input text file (simple CSV format)')
    parser.add_argument('--structured', help='Input structured text file (with indentation)')
    parser.add_argument('--output', help='Output file (optional)')
    parser.add_argument('--format', choices=['hex', 'binary'], default='hex', help='Console output format (files always saved as binary)')
    parser.add_argument('--decode', action='store_true', help='Also decode and show the result')
    
    # Parse arguments
    if len(sys.argv) == 1:
        show_usage()
        sys.exit(0)
    
    args = parser.parse_args()
    
    # Load data based on input method
    elements = None
    
    if args.json:
        print(f"Loading from JSON file: {args.json}")
        elements = load_from_json_file(args.json)
    elif args.text:
        print(f"Loading from text file: {args.text}")
        elements = load_from_text_file(args.text)
    elif args.structured:
        print(f"Loading from structured text file: {args.structured}")
        elements = load_from_structured_text_file(args.structured)
    else:
        show_usage()
        sys.exit(1)
    
    if not elements:
        print("No valid elements loaded or created.")
        sys.exit(1)
    
    # Encode the elements
    try:
        print(f"Encoding {len(elements)} elements...")
        encoder = encode_ttlv_structure(elements)
        
        print(f"Successfully encoded {len(elements)} elements")
        print(f"Total size: {len(encoder.get_buffer())} bytes")
        
        # Save or display output
        save_output(encoder, args.output, args.format)
        
        # Optionally decode and show
        if args.decode:
            try:
                from decode_ttlv import DecodeTTLV
                print("\nDecoded verification:")
                print("-" * 30)
                decoder = DecodeTTLV(encoder.get_buffer())
                decoder.decode()
            except ImportError:
                print("Decoder not available for verification")
        
    except Exception as e:
        print(f"Error encoding elements: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
