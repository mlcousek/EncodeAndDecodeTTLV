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

### 🧪 **Round-Trip Test Suite** (`test_roundtrip.py`)
- Comprehensive validation across 159 test files (structured, JSON, CSV formats)
- Configurable output verbosity and summary display options
- 100% round-trip accuracy validation for all supported formats
- Automated regression testing for encoder/decoder compatibility

## Installation

Install the required PyKMIP library:
```bash
pip install -r requirements.txt
```

**Note:** The project includes a comprehensive test suite in the `test_cases/` directory with 159 test files (53 each in structured text, JSON, and CSV formats) covering various KMIP request/response scenarios for validation and testing.

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

The project includes a comprehensive round-trip test suite (`test_roundtrip.py`) that validates encoding and decoding functionality across all supported formats with 159 test files (53 each for structured text, JSON, and CSV formats):

#### **Basic Usage**
```bash
# Test all formats (default)
python test_roundtrip.py

# Test specific format
python test_roundtrip.py --format structured
python test_roundtrip.py --format json
python test_roundtrip.py --format csv
```

#### **Command Line Options**

```bash
python test_roundtrip.py [-h] [--format {structured,json,csv,all}] 
                        [--show-results] [--all-files-summary {failed,off,all}]
```

**Options:**
- `--format {structured,json,csv,all}`: Test format selection (default: all)
- `--show-results`: Show detailed results for all tests (default: hide successful tests, show only failures)
- `--all-files-summary {failed,off,all}`: Control summary display at the end
  - `failed` (default): Show only failed files in summary
  - `off`: Hide the summary section completely
  - `all`: Show all files (passed and failed) in summary

#### **Features:**
- 🎯 Automated testing of all test cases in the `test_cases/` directory
- 🔄 Round-trip validation (encode → decode → compare) for three formats:
  - **Structured Text**: Original format ↔ TTLV ↔ Structured format
  - **JSON**: JSON ↔ TTLV ↔ Structured ↔ JSON
  - **CSV**: CSV ↔ TTLV ↔ Structured ↔ CSV
- 📊 Detailed success/failure statistics with configurable verbosity
- 🔍 Smart error reporting (failures always shown, successes optional)

#### **Example Usage and Output:**

**Quiet mode (default):**
```bash
python test_roundtrip.py --format structured
```
```
🧪 TTLV Round-Trip Validation Script
==================================================
🔤 Testing Structured Text Files
--------------------------------------------------
� Found 53 structured text files to test
📊 Structured Text Summary: ✅ 53 passed, ❌ 0 failed
...
📊 OVERALL SUMMARY: ✅ 53 passed, ❌ 0 failed
==================================================
📋 ALL FILES SUMMARY:
==================================================
✅ No failed files to display
🎉 All 53 tests passed successfully!
```

**Verbose mode:**
```bash
python test_roundtrip.py --format structured --show-results --all-files-summary all
```
```
============================================================
Testing Structured: activate_object_request.txt
============================================================
1. Loading original structured text...
   ✅ Loaded 234 characters
2. Encoding to TTLV binary...
   ✅ Encoded to 152 bytes
3. Decoding back to structured text...
   ✅ Decoded to 234 characters
4. Comparing original and decoded...
   ✅ SUCCESS: PERFECT MATCH - Round-trip successful!
...
==================================================
� ALL FILES SUMMARY:
==================================================
✅ PASS 📄 activate_object_request.txt
✅ PASS 📄 activate_object_response.txt
✅ PASS 📄 create_key_pair_request.txt
...
```

### **Test File Formats and Organization**

The test suite includes 159 test files organized in three formats:

**Directory Structure:**
```
test_cases/
├── structured/     # 53 structured text files (.txt)
├── json/          # 53 JSON files (.json)  
└── csv/           # 53 CSV files (.csv)
```

**Format Details:**
- **Structured Text**: Uses the same format as decoder output
  - TEXT_STRING values: `bytearray(b'...')`
  - BYTE_STRING values: plain hex strings
  - Hierarchical indentation for STRUCTURE elements
  - Consistent enum names (e.g., `CREATE`, `DISCOVER_VERSIONS`)

- **JSON Format**: Array of objects with `tag`, `type`, and `value` properties
- **CSV Format**: Comma-separated values with columns for tag, type, and value

All test files contain identical KMIP request/response data in different representations, enabling comprehensive round-trip validation across all supported input formats.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## Dependencies

- Python 3.6+
- PyKMIP library
- Standard Python libraries (struct, binascii, argparse, etc.)
