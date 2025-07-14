#!/usr/bin/env python3
"""
Convert structured text TTLV files to JSON format
"""

import os
import sys
import json
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
        # For structures, the value is just a structure identifier
        return {
            "tag": tag,
            "type": data_type,
            "indent": indent_level,
            "value": []  # Will be populated with child elements
        }
    elif data_type == "TEXT_STRING":
        # Remove bytearray(b'...') wrapper if present
        if value.startswith("bytearray(b'") and value.endswith("')"):
            actual_value = value[12:-2]  # Remove bytearray(b' and ')
        else:
            actual_value = value
        return {
            "tag": tag,
            "type": data_type,
            "indent": indent_level,
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
            "indent": indent_level,
            "value": actual_value
        }
    elif data_type == "INTEGER" or data_type == "LONG_INTEGER":
        return {
            "tag": tag,
            "type": data_type,
            "indent": indent_level,
            "value": int(value)
        }
    elif data_type == "ENUMERATION":
        # Try to convert to int if it's numeric, otherwise keep as string
        try:
            enum_value = int(value)
        except ValueError:
            enum_value = value
        return {
            "tag": tag,
            "type": data_type,
            "indent": indent_level,
            "value": enum_value
        }
    elif data_type == "BOOLEAN":
        bool_value = value.lower() in ('true', '1', 'yes')
        return {
            "tag": tag,
            "type": data_type,
            "indent": indent_level,
            "value": bool_value
        }
    elif data_type == "DATE_TIME":
        # Handle both Unix timestamps and date strings
        try:
            # Try to parse as Unix timestamp first
            timestamp_value = int(value)
        except ValueError:
            # If it's a date string, keep it as string for now
            timestamp_value = value
        return {
            "tag": tag,
            "type": data_type,
            "indent": indent_level,
            "value": timestamp_value
        }
    
    return None

def build_json_structure(parsed_lines):
    """Convert parsed lines to nested JSON structure."""
    if not parsed_lines:
        return []
    
    # Start with the root element (always has indent 0)
    if len(parsed_lines) == 1:
        element = parsed_lines[0]
        if element["type"] == "STRUCTURE":
            return [{
                "tag": element["tag"],
                "type": element["type"],
                "value": []
            }]
        else:
            return [{
                "tag": element["tag"],
                "type": element["type"],
                "value": element["value"]
            }]
    
    # For multiple elements, process them as siblings at the same level
    result = []
    i = 0
    
    while i < len(parsed_lines):
        current = parsed_lines[i]
        
        if current["type"] == "STRUCTURE":
            # Find children (next level of indentation)
            children_start = i + 1
            children_end = children_start
            target_indent = current["indent"] + 1
            
            # Find all elements that belong to this structure
            while children_end < len(parsed_lines) and parsed_lines[children_end]["indent"] >= target_indent:
                children_end += 1
            
            # Extract children lines
            children_lines = []
            j = children_start
            while j < children_end:
                if parsed_lines[j]["indent"] == target_indent:
                    # This is a direct child, find its end
                    child_start = j
                    child_end = j + 1
                    while child_end < children_end and parsed_lines[child_end]["indent"] > target_indent:
                        child_end += 1
                    
                    # Add this child and its descendants
                    child_lines = parsed_lines[child_start:child_end]
                    if len(child_lines) == 1:
                        # Simple element
                        child = child_lines[0]
                        children_lines.append({
                            "tag": child["tag"],
                            "type": child["type"],
                            "value": child["value"]
                        })
                    else:
                        # Structure with children - recursively process
                        child_structure = build_json_structure(child_lines)
                        children_lines.extend(child_structure)
                    
                    j = child_end
                else:
                    j += 1
            
            result.append({
                "tag": current["tag"],
                "type": current["type"],
                "value": children_lines
            })
            
            i = children_end
        else:
            # Simple element
            result.append({
                "tag": current["tag"],
                "type": current["type"],
                "value": current["value"]
            })
            i += 1
    
    return result

def convert_structured_to_json(structured_text):
    """Convert structured text to JSON format."""
    lines = structured_text.strip().split('\n')
    parsed_lines = []
    
    for line in lines:
        parsed = parse_structured_line(line)
        if parsed:
            parsed_lines.append(parsed)
    
    return build_json_structure(parsed_lines)

def convert_file(input_path, output_path):
    """Convert a single structured text file to JSON."""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            structured_text = f.read()
        
        json_data = convert_structured_to_json(structured_text)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {e}")
        return False

def main():
    """Convert all structured text files to JSON."""
    structured_dir = Path("test_cases/structured")
    json_dir = Path("test_cases/json")
    
    if not structured_dir.exists():
        print(f"Error: {structured_dir} not found!")
        return
    
    # Create JSON directory if it doesn't exist
    json_dir.mkdir(exist_ok=True)
    
    # Find all .txt files
    txt_files = list(structured_dir.glob("*.txt"))
    
    print(f"Converting {len(txt_files)} structured text files to JSON...")
    
    success_count = 0
    for txt_file in txt_files:
        json_file = json_dir / (txt_file.stem + ".json")
        print(f"Converting {txt_file.name} -> {json_file.name}")
        
        if convert_file(txt_file, json_file):
            success_count += 1
        else:
            print(f"Failed to convert {txt_file.name}")
    
    print(f"\nCompleted: {success_count}/{len(txt_files)} files converted successfully")

if __name__ == "__main__":
    main()
