# Examples Directory

This directory contains example files demonstrating different input formats supported by the TTLV encoder.

## Files

### 1. `discover_versions_request.txt`
A basic KMIP Discover Versions request using structured text format.
- Shows nested STRUCTURE elements
- Demonstrates proper indentation
- Uses ENUMERATION for operation type

**Usage:**
```bash
python encode_ttlv.py --structured examples/discover_versions_request.txt --decode
```

### 2. `simple_attributes.txt`
A simple example showing attribute encoding with TEXT_STRING values.
- Demonstrates TEXT_STRING format using `bytearray(b'...')`
- Shows basic attribute name/value pairs
- Good for learning the structured text format

**Usage:**
```bash
python encode_ttlv.py --structured examples/simple_attributes.txt --decode
```

### 3. `simple_attributes.json`
A JSON format example showing various KMIP data types.
- Demonstrates JSON input format
- Shows different data types (TEXT_STRING, INTEGER, ENUMERATION, BOOLEAN)
- Alternative to structured text format

**Usage:**
```bash
python encode_ttlv.py --json examples/simple_attributes.json --decode
```

## Format Notes

- **Structured Text Format (.txt)**: Recommended format that matches decoder output
- **JSON Format (.json)**: Alternative format for programmatic generation
- **Round-Trip Compatible**: All examples can be encoded and decoded back to identical format

## Testing Examples

You can test all examples using the round-trip test:
```bash
python test_roundtrip.py
```

The main test suite in `test_cases/` contains 53+ comprehensive examples covering all KMIP operations.
