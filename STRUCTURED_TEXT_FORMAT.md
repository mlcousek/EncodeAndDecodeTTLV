# Structured Text Format Support

The TTLV Encoder now supports parsing structured text format with indentation, making it much easier to work with complex TTLV hierarchies.

## Format Description

The structured text format uses indentation to represent hierarchy and follows this pattern:
```
TAG:TYPE(length):value
```

Where:
- **TAG**: The TTLV tag name (e.g., `REQUEST_MESSAGE`, `OPERATION`)
- **TYPE**: The data type (e.g., `STRUCTURE`, `INTEGER`, `TEXT_STRING`, `ENUMERATION`)
- **length**: The length in bytes (for reference, calculated automatically)
- **value**: The actual value (for structures, this is typically `struX` where X is a number)

## Indentation Rules

- Use spaces for indentation (1 space per level recommended)
- Child elements must be indented more than their parent
- Sibling elements should have the same indentation level

## Example

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

## Supported Data Types

### Basic Types
- **INTEGER**: 32-bit integers (e.g., `BATCH_COUNT:INTEGER(4):1`)
- **TEXT_STRING**: Text strings (e.g., `ATTRIBUTE_NAME:TEXT_STRING(10):TestValue`)
- **BOOLEAN**: Boolean values (e.g., `ACTIVE:BOOLEAN(8):True`)
- **BYTE_STRING**: Binary data in hex format
- **DATE_TIME**: Timestamps

### Special Types
- **STRUCTURE**: Container for other elements
- **ENUMERATION**: Enumerated values (supports both numeric and named values)

### Enumeration Support

For `OPERATION` enumerations, you can use either numeric values or names:

**Numeric:**
```
OPERATION:ENUMERATION(4):30
```

**Named (recommended):**
```
OPERATION:ENUMERATION(4):DISCOVER_VERSIONS
```

Supported operation names include:
- CREATE, GET, LOCATE, REGISTER
- DISCOVER_VERSIONS, ACTIVATE, REVOKE
- ENCRYPT, DECRYPT, SIGN, etc.

## Usage

### Command Line
```bash
# From structured text file
python encode_ttlv.py --structured my_structure.txt --decode

# Save to file
python encode_ttlv.py --structured input.txt --output output.hex --format hex
```

### Python Code
```python
from encode_ttlv import encode_from_structured_text, load_from_structured_text_file

# From text string
structured_text = """REQUEST_MESSAGE:STRUCTURE(96):stru1
 REQUEST_HEADER:STRUCTURE(56):stru2
  BATCH_COUNT:INTEGER(4):1"""

encoder = encode_from_structured_text(structured_text)
hex_output = encoder.get_hex_string()

# From file
elements = load_from_structured_text_file('my_structure.txt')
encoder = encode_ttlv_structure(elements)
```

## Benefits

1. **Human Readable**: Easy to read and understand hierarchical structures
2. **Direct Copy-Paste**: Can copy decoder output and use it directly as input
3. **Enum Support**: Supports both numeric and named enumeration values
4. **Error Handling**: Graceful handling of parsing errors with helpful messages
5. **Validation**: Automatic type conversion and validation

## Example Files

See the included example files:
- `example_discover_versions.txt` - Simple DISCOVER_VERSIONS request
- `example_create_key.txt` - More complex CREATE request with authentication

This feature makes it much easier to work with complex KMIP protocol structures and debug TTLV encoding issues.
