# TTLV Encoder and Decoder

This utility provides both encoding and decoding capabilities for TTLV (Tag-Type-Length-Value) byte buffers as used in the [KMIP protocol](https://docs.oasis-open.org/kmip/kmip-spec/v2.1/csd01/kmip-spec-v2.1-csd01.html). The scripts require the [PyKMIP library](https://github.com/OpenKMIP/PyKMIP) for enum definitions and tag mappings.

## Features

### 🔍 **TTLV Decoder** (`decode_ttlv.py`)
- Decode TTLV byte buffers into human-readable format
- Support for all KMIP data types (INTEGER, TEXT_STRING, ENUMERATION, STRUCTURE, etc.)
- Hierarchical structure display with proper indentation
- Automatic enum name resolution using PyKMIP definitions

### 🔧 **TTLV Encoder** (`encode_ttlv.py`)
- Encode data into TTLV format from multiple input sources
- Support for JSON, CSV text files, and **structured text format**
- Interactive mode for building TTLV structures
- Comprehensive data type support with proper padding
- Built-in validation and error handling
- **NEW**: Structured text format with indentation support

## Installation

Install the required PyKMIP library:
```bash
pip install -r requirements.txt
```

## Usage

### Decoder Usage

Decode hex-encoded TTLV data:
```bash
python decode_ttlv.py <hex_data>
```

**Example:**
```bash
python decode_ttlv.py 42000a070000000d54657374417474726962757465000000
```

**Output:**
```
ATTRIBUTE_NAME:TEXT_STRING(13):bytearray(b'TestAttribute')
```

### Encoder Usage

#### 1. **Structured Text Format** (Recommended)
Use indented text format that matches decoder output:

```bash
python encode_ttlv.py --structured input.txt [--output output.hex] [--decode]
```

**Example structured text file:**
```
REQUEST_MESSAGE:STRUCTURE(96):stru1
 REQUEST_HEADER:STRUCTURE(56):stru2
  PROTOCOL_VERSION:STRUCTURE(32):stru3
   PROTOCOL_VERSION_MAJOR:INTEGER(4):1
   PROTOCOL_VERSION_MINOR:INTEGER(4):1
  BATCH_COUNT:INTEGER(4):1
 BATCH_ITEM:STRUCTURE(24):stru2
  OPERATION:ENUMERATION(4):DISCOVER_VERSIONS
  REQUEST_PAYLOAD:STRUCTURE(0):stru3
```

**Command:**
```bash
python encode_ttlv.py --structured example_discover_versions.txt --decode
```

#### 2. **JSON Format**
```bash
python encode_ttlv.py --json input.json [--output output.hex]
```

**JSON Example:**
```json
[
  {"tag": "ATTRIBUTE_NAME", "type": "TEXT_STRING", "value": "MyAttribute"},
  {"tag": "ATTRIBUTE_VALUE", "type": "INTEGER", "value": 42},
  {"tag": "OPERATION", "type": "ENUMERATION", "value": "CREATE"}
]
```

#### 3. **CSV Text Format**
```bash
python encode_ttlv.py --text input.txt [--output output.hex]
```

**CSV Example:**
```
ATTRIBUTE_NAME,TEXT_STRING,MyAttribute
ATTRIBUTE_VALUE,INTEGER,42
OPERATION,ENUMERATION,CREATE
```

#### 4. **Interactive Mode**
```bash
python encode_ttlv.py --interactive
```

#### 5. **Test Mode**
```bash
python encode_ttlv.py test
```

## Supported Data Types

| Type | Description | Example |
|------|-------------|---------|
| `INTEGER` | 32-bit signed integer | `42` |
| `LONG_INTEGER` | 64-bit signed integer | `1234567890` |
| `ENUMERATION` | Enum values (supports names) | `CREATE`, `1` |
| `BOOLEAN` | Boolean values | `true`, `false` |
| `TEXT_STRING` | UTF-8 text | `"Hello World"` |
| `BYTE_STRING` | Binary data (hex) | `"48656c6c6f"` |
| `STRUCTURE` | Nested TTLV elements | Contains child elements |
| `DATE_TIME` | Timestamp | Unix timestamp |

## Enum Support

The encoder supports both numeric values and enum names for KMIP operations:

- `CREATE` → 1
- `REGISTER` → 3
- `GET` → 10
- `DISCOVER_VERSIONS` → 30
- `ACTIVATE` → 18
- And many more...

## Examples

### Complete Workflow Example

1. **Create a structured text file** (`my_request.txt`):
```
REQUEST_MESSAGE:STRUCTURE(200):stru1
 REQUEST_HEADER:STRUCTURE(100):stru2
  PROTOCOL_VERSION:STRUCTURE(32):stru3
   PROTOCOL_VERSION_MAJOR:INTEGER(4):1
   PROTOCOL_VERSION_MINOR:INTEGER(4):1
  BATCH_COUNT:INTEGER(4):1
 BATCH_ITEM:STRUCTURE(80):stru2
  OPERATION:ENUMERATION(4):CREATE
  REQUEST_PAYLOAD:STRUCTURE(60):stru3
   OBJECT_TYPE:ENUMERATION(4):2
   TEMPLATE_ATTRIBUTE:STRUCTURE(40):stru4
    ATTRIBUTE:STRUCTURE(30):stru5
     ATTRIBUTE_NAME:TEXT_STRING(20):Cryptographic Length
     ATTRIBUTE_VALUE:INTEGER(4):256
```

2. **Encode to hex:**
```bash
python encode_ttlv.py --structured my_request.txt --output encoded.hex
```

3. **Verify by decoding:**
```bash
python decode_ttlv.py $(cat encoded.hex)
```

### Programming Interface

```python
from encode_ttlv import encode_from_structured_text, EncodeTTLV
from decode_ttlv import DecodeTTLV

# Method 1: From structured text
structured_text = """ATTRIBUTE_NAME:TEXT_STRING(13):TestAttribute"""
encoder = encode_from_structured_text(structured_text)
hex_output = encoder.get_hex_string()

# Method 2: Programmatic encoding
encoder = EncodeTTLV()
encoder.encode_ttlv('ATTRIBUTE_NAME', 'TEXT_STRING', 'TestAttribute')
hex_output = encoder.get_hex_string()

# Decode
decoder = DecodeTTLV(encoder.get_buffer())
decoder.decode()
```

## File Structure

```
EncodeAndDecodeTTLV/
├── encode_ttlv.py              # Main encoder script
├── decode_ttlv.py              # Main decoder script
├── requirements.txt            # Python dependencies
├── tests/                      # Test files
│   ├── test_encoder.py         # Comprehensive tests
│   ├── quick_start.py          # Quick start examples
│   ├── simple_test.py          # Basic validation
│   └── run_tests.py           # Test runner
├── example_discover_versions.txt # Example structured file
├── example_create_key.txt      # Complex example
└── README.md                   # This file
```

## Advanced Features

- **Automatic enum resolution** from PyKMIP library
- **Proper TTLV padding** according to KMIP specification  
- **Nested structure support** with unlimited depth
- **Round-trip encoding/decoding** verification
- **Error handling** with detailed error messages
- **Multiple output formats** (hex, binary)
- **Command-line integration** for automation

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Dependencies

- Python 3.6+
- PyKMIP library
- Standard Python libraries (struct, binascii, argparse, etc.)
