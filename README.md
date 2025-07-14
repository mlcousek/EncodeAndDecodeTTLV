# TTLV Encoder and Decoder

This utility provides both encoding and decoding capabilities for TTLV (Tag-Type-Length-Value) byte buffers as used in the [KMIP protocol](https://docs.oasis-open.org/kmip/kmip-spec/v2.1/csd01/kmip-spec-v2.1-csd01.html). The scripts require the [PyKMIP library](https://github.com/OpenKMIP/PyKMIP) for enum definitions and tag mappings.

## Features

### 🔍 **TTLV Decoder** (`decode_ttlv.py`)
- Decode TTLV byte buffers into human-readable format
- Support for all KMIP data types (INTEGER, TEXT_STRING, ENUMERATION, STRUCTURE, etc.)
- Hierarchical structure display with proper indentation
- Automatic enum name resolution using PyKMIP definitions
- **Output Conventions:**
  - TEXT_STRING values displayed as `bytearray(b'...')`
  - BYTE_STRING values displayed as plain hex strings

### 🔧 **TTLV Encoder** (`encode_ttlv.py`)
- Encode data into TTLV format from multiple input sources
- Support for JSON, CSV text files, and structured text format
- Interactive mode for building TTLV structures
- Comprehensive data type support with proper padding
- Structured text format with indentation support

## Installation

Install the required PyKMIP library:
```bash
pip install -r requirements.txt
```

**Note:** The project includes a comprehensive test suite in the `test_cases/` directory with 53 example KMIP request/response files for validation and testing. Additional usage examples are available in the `examples/` directory.

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

**Note:** The structured text format is designed for round-trip compatibility - output from the decoder can be directly used as input to the encoder.

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

## Supported Data Types

| Type | Description | Example |
|------|-------------|---------|
| `INTEGER` | 32-bit signed integer | `42` |
| `LONG_INTEGER` | 64-bit signed integer | `1234567890` |
| `ENUMERATION` | Enum values (supports names) | `CREATE`, `1` |
| `BOOLEAN` | Boolean values | `true`, `false` |
| `TEXT_STRING` | UTF-8 text (decoded as `bytearray(b'...')`) | `bytearray(b'Hello World')` |
| `BYTE_STRING` | Binary data (decoded as hex) | `48656c6c6f` |
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
     ATTRIBUTE_NAME:TEXT_STRING(20):bytearray(b'Cryptographic Length')
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

## Testing and Validation

### 🧪 **Round-Trip Testing**

The project includes a comprehensive round-trip test suite that validates encoding and decoding functionality across all example KMIP request/response files:

```bash
python test_roundtrip.py
```

**Features:**
- 🎯 Automated testing of all test cases in the `test_cases/` directory
- 🔄 Round-trip validation (encode → decode → compare)
- 🎨 Colorful emoji-enhanced output for easy status tracking
- 📊 Detailed success/failure statistics
- ⚡ Parallel processing for faster test execution

**Example output:**
```
🧪 Round-trip testing for TTLV encoder/decoder
🔍 Found 56 test files

✅ example_discover_versions_request.txt - Round-trip successful
✅ example_create_request.txt - Round-trip successful
✅ example_get_object_request.txt - Round-trip successful
...

📊 Round-trip Test Summary:
✅ Successful: 56/56 (100.0%)
❌ Failed: 0/56 (0.0%)
🎉 All tests passed!
```

### **Test File Format**

Test files use the structured text format that matches decoder output:
- TEXT_STRING values are represented as `bytearray(b'...')`
- BYTE_STRING values are represented as plain hex strings
- Proper hierarchical indentation for STRUCTURE elements
- Consistent enum name usage (e.g., `CREATE`, `DISCOVER_VERSIONS`)

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Dependencies

- Python 3.6+
- PyKMIP library
- Standard Python libraries (struct, binascii, argparse, etc.)
