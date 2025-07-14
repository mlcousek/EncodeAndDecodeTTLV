# CSV Test Cases

This directory contains TTLV test cases in CSV (Comma-Separated Values) format. These files are automatically generated from the structured text test cases using the `helpers/convert_to_csv.py` script.

## Format

Each CSV file contains one row per TTLV element with three columns:
- **TAG**: The KMIP tag name (e.g., `PROTOCOL_VERSION_MAJOR`, `OPERATION`)
- **TYPE**: The TTLV data type (e.g., `INTEGER`, `TEXT_STRING`, `ENUMERATION`)
- **VALUE**: The element value (e.g., `1`, `TestAttribute`, `CREATE`)

### Example:
```csv
PROTOCOL_VERSION_MAJOR,INTEGER,1
PROTOCOL_VERSION_MINOR,INTEGER,1
BATCH_COUNT,INTEGER,1
OPERATION,ENUMERATION,DISCOVER_VERSIONS
```

## Data Types Included

The CSV files include all KMIP data types except `STRUCTURE` elements:
- **INTEGER**: 32-bit signed integers
- **LONG_INTEGER**: 64-bit signed integers
- **ENUMERATION**: Enum values (names or numbers)
- **BOOLEAN**: Boolean values (true/false)
- **TEXT_STRING**: UTF-8 text strings
- **BYTE_STRING**: Binary data as hex strings
- **DATE_TIME**: Unix timestamps

Note: `STRUCTURE` elements are excluded from CSV format since CSV is inherently flat and cannot represent hierarchical structures.

## Usage

### With TTLV Encoder
```bash
python encode_ttlv.py --text test_cases/csv/example_file.csv --decode
```

### Round-Trip Testing
The CSV files are included in the comprehensive round-trip test suite:
```bash
python test_roundtrip.py --format csv
python test_roundtrip.py --format all
```

### Generate CSV Files
To regenerate all CSV files from structured text:
```bash
python helpers/convert_to_csv.py
```

## File Count
This directory contains **53 CSV test files** corresponding to all structured text test cases, with a total of **475 data rows** across all files.

## Notes
- CSV files do not include headers by design (to match the expected CSV text format)
- Text values containing commas may be quoted in CSV output (e.g., `"VMware, Inc."`)
- All files are UTF-8 encoded
- Round-trip testing achieves **100% success rate** for CSV format
