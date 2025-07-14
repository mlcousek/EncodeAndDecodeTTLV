# JSON Test Cases

This directory contains JSON format versions of all TTLV test cases. These files are automatically generated from the structured text files in the `../structured/` directory.

## File Format

Each JSON file represents a TTLV structure as an array of objects, where each object has:
- `tag`: The KMIP tag name (e.g., "REQUEST_MESSAGE", "ATTRIBUTE_NAME")
- `type`: The data type (e.g., "STRUCTURE", "TEXT_STRING", "INTEGER", "ENUMERATION")
- `value`: The actual value or nested array for STRUCTURE types

## Data Type Examples

```json
{
  "tag": "ATTRIBUTE_NAME",
  "type": "TEXT_STRING", 
  "value": "TestKey"
}

{
  "tag": "ATTRIBUTE_VALUE",
  "type": "INTEGER",
  "value": 256
}

{
  "tag": "OPERATION",
  "type": "ENUMERATION",
  "value": "CREATE"
}

{
  "tag": "REQUEST_HEADER",
  "type": "STRUCTURE",
  "value": [
    // ... nested elements
  ]
}
```

## Usage

These JSON files can be used with the encoder:

```bash
python encode_ttlv.py --json test_cases/json/discover_versions_simple_request.json --decode
```

## Generation

These files are automatically generated from the structured text format using:

```bash
python convert_to_json.py
```

The conversion script parses the indented structured text format and creates equivalent nested JSON structures.
