#!/usr/bin/env python3
"""
Convert structured text TTLV files to CSV format
"""

import os
import sys
import csv
import re
from pathlib import Path

def parse_structured_line(line):
    """Parse a single line of structured text format."""
    # Remove leading whitespace to determine indentation level
    stripped = line.lstrip()
    if not stripped:
        return None
    
    indent_level = len(line) - len(stripped)
    
    # Parse the line format: TAG:TYPE(length):value
    match = re.match(r'^([A-Z_]+):(TEXT_STRING|BYTE_STRING|INTEGER|LONG_INTEGER|ENUMERATION|BOOLEAN|STRUCTURE|DATE_TIME)\((\d+)\):(.*)$', stripped)
    if not match:
        return None
    
    tag, data_type, length, value = match.groups()
    
    # Process the value based on type
    if data_type == "STRUCTURE":
        # For structures in CSV, we can skip them since CSV is flat
        # or represent them as empty values - but typically CSV doesn't include structures
        return None
    elif data_type == "TEXT_STRING":
        # Remove bytearray(b'...') wrapper if present and extract the actual string
        if value.startswith("bytearray(b'") and value.endswith("')"):
            actual_value = value[12:-2]  # Remove bytearray(b' and ')
        else:
            actual_value = value
        return {
            "tag": tag,
            "type": data_type,
            "value": actual_value
        }
    elif data_type == "BYTE_STRING":
        # Handle byte strings - remove b' prefix and ' suffix if present
        if value.startswith("b'") and value.endswith("'"):
            actual_value = value[2:-1]  # Remove b' and '
        else:
            actual_value = value
        return {
            "tag": tag,
            "type": data_type,
            "value": actual_value
        }
    elif data_type in ["INTEGER", "LONG_INTEGER"]:
        return {
            "tag": tag,
            "type": data_type,
            "value": int(value)
        }
    elif data_type == "ENUMERATION":
        # Keep enum values as they are (either numeric or string)
        try:
            enum_value = int(value)
        except ValueError:
            enum_value = value
        return {
            "tag": tag,
            "type": data_type,
            "value": enum_value
        }
    elif data_type == "BOOLEAN":
        bool_value = value.lower() in ('true', '1', 'yes')
        return {
            "tag": tag,
            "type": data_type,
            "value": bool_value
        }
    elif data_type == "DATE_TIME":
        # Handle both Unix timestamps and date strings
        try:
            # Try to parse as Unix timestamp first
            timestamp_value = int(value)
        except ValueError:
            # If it's a date string, keep it as string
            timestamp_value = value
        return {
            "tag": tag,
            "type": data_type,
            "value": timestamp_value
        }
    
    return None

def convert_structured_to_csv(structured_text):
    """Convert structured text to CSV format."""
    lines = structured_text.strip().split('\n')
    csv_rows = []
    
    for line in lines:
        parsed = parse_structured_line(line)
        if parsed:
            # CSV format: TAG,TYPE,VALUE
            csv_rows.append([parsed["tag"], parsed["type"], str(parsed["value"])])
    
    return csv_rows

def convert_file(input_path, output_path):
    """Convert a single structured text file to CSV."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            structured_text = f.read()
        
        csv_rows = convert_structured_to_csv(structured_text)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Don't write header row - CSV text format doesn't expect headers
            # writer.writerow(['TAG', 'TYPE', 'VALUE'])
            # Write data rows only
            writer.writerows(csv_rows)
        
        return True, len(csv_rows)
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False, 0

def main():
    """Convert all structured text files to CSV."""
    structured_dir = Path("test_cases/structured")
    csv_dir = Path("test_cases/csv")
    
    if not structured_dir.exists():
        print(f"Error: {structured_dir} not found!")
        return
    
    # Create CSV directory if it doesn't exist
    csv_dir.mkdir(exist_ok=True)
    
    # Find all .txt files
    txt_files = list(structured_dir.glob("*.txt"))
    
    print(f"Converting {len(txt_files)} structured text files to CSV...")
    
    success_count = 0
    total_rows = 0
    
    for txt_file in txt_files:
        csv_file = csv_dir / (txt_file.stem + ".csv")
        print(f"Converting {txt_file.name} -> {csv_file.name}")
        
        success, row_count = convert_file(txt_file, csv_file)
        if success:
            success_count += 1
            total_rows += row_count
            print(f"  ✅ {row_count} rows written")
        else:
            print(f"  ❌ Failed to convert {txt_file.name}")
    
    print(f"\nCompleted: {success_count}/{len(txt_files)} files converted successfully")
    print(f"Total CSV rows generated: {total_rows}")

if __name__ == "__main__":
    main()
