#!/usr/bin/env python3
"""
TTLV Round-Trip Test Script

This script tests encoding and decoding for all test cases in both structured text and JSON formats.

For structured text files:
1. Loads the original structured text
2. Encodes it to TTLV binary format
3. Decodes the binary back to structured text
4. Compares the original with the decoded result

For JSON files:
1. Loads the original JSON
2. Encodes it to TTLV binary format
3. Decodes the binary back to structured text
4. Converts the structured text back to JSON
5. Compares the original JSON with the converted JSON

For CSV files:
1. Loads the original CSV
2. Encodes it to TTLV binary format
3. Decodes the binary back to structured text
4. Converts the structured text back to CSV
5. Compares the original CSV with the converted CSV

Usage:
    python test_roundtrip.py [--format structured|json|csv|all] [--show-results]
"""

import os
import sys
import traceback
import json
import argparse
from pathlib import Path

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'helpers'))

try:
    from encode_ttlv import load_from_structured_text_file, encode_from_structured_text, load_from_json_file, encode_ttlv_structure, load_from_text_file
    from decode_ttlv import DecodeTTLV
    from helpers.convert_structured_to_json import convert_structured_to_json
    from helpers.convert_structured_to_csv import convert_structured_to_csv
    import subprocess
    import io
    import csv
    from contextlib import redirect_stdout
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure encode_ttlv.py, decode_ttlv.py, and helpers/convert_structured_to_json.py are available")
    sys.exit(1)

def decode_ttlv_binary(binary_data):
    """Decode TTLV binary data to structured text using the DecodeTTLV class."""
    try:
        # Create a string buffer to capture the printed output
        output_buffer = io.StringIO()
        
        # Create decoder instance
        decoder = DecodeTTLV(binary_data)
        
        # Capture the decode output
        with redirect_stdout(output_buffer):
            decoder.decode()
        
        # Get the captured output
        decoded_text = output_buffer.getvalue()
        return decoded_text
        
    except Exception as e:
        raise Exception(f"Failed to decode TTLV binary: {e}")

def normalize_text(text):
    """Normalize text for comparison by removing extra whitespace and ensuring consistent line endings."""
    lines = []
    for line in text.strip().split('\n'):
        # Strip trailing whitespace but preserve leading spaces for indentation
        normalized_line = line.rstrip()
        if normalized_line:  # Skip empty lines
            lines.append(normalized_line)
    return '\n'.join(lines)

def compare_structures(original, decoded):
    """Compare two structured text representations and return differences."""
    orig_normalized = normalize_text(original)
    decoded_normalized = normalize_text(decoded)
    
    if orig_normalized == decoded_normalized:
        return True, []
    
    # Find differences line by line
    orig_lines = orig_normalized.split('\n')
    decoded_lines = decoded_normalized.split('\n')
    
    differences = []
    max_lines = max(len(orig_lines), len(decoded_lines))
    
    for i in range(max_lines):
        orig_line = orig_lines[i] if i < len(orig_lines) else "<MISSING>"
        decoded_line = decoded_lines[i] if i < len(decoded_lines) else "<MISSING>"
        
        if orig_line != decoded_line:
            differences.append(f"Line {i+1}:")
            differences.append(f"  Original: {orig_line}")
            differences.append(f"  Decoded:  {decoded_line}")
    
    return False, differences

def compare_json_structures(original_json, converted_json):
    """Compare two JSON structures and return differences."""
    if original_json == converted_json:
        return True, []
    
    # Find differences
    differences = []
    
    def compare_recursive(obj1, obj2, path=""):
        if type(obj1) != type(obj2):
            differences.append(f"{path}: Type mismatch - {type(obj1).__name__} vs {type(obj2).__name__}")
            return
        
        if isinstance(obj1, dict):
            for key in set(obj1.keys()) | set(obj2.keys()):
                if key not in obj1:
                    differences.append(f"{path}.{key}: Missing in original")
                elif key not in obj2:
                    differences.append(f"{path}.{key}: Missing in converted")
                else:
                    compare_recursive(obj1[key], obj2[key], f"{path}.{key}")
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                differences.append(f"{path}: List length mismatch - {len(obj1)} vs {len(obj2)}")
                return
            for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                compare_recursive(item1, item2, f"{path}[{i}]")
        else:
            if obj1 != obj2:
                differences.append(f"{path}: Value mismatch - '{obj1}' vs '{obj2}'")
    
    compare_recursive(original_json, converted_json)
    return False, differences

def compare_csv_structures(original_csv_rows, converted_csv_rows):
    """Compare two CSV row structures and return differences."""
    if original_csv_rows == converted_csv_rows:
        return True, []
    
    # Find differences
    differences = []
    
    if len(original_csv_rows) != len(converted_csv_rows):
        differences.append(f"Row count mismatch - original: {len(original_csv_rows)}, converted: {len(converted_csv_rows)}")
        return False, differences
    
    def normalize_csv_value(value):
        """Normalize CSV value by removing quotes if present and stripping whitespace."""
        value = str(value).strip()
        # Remove quotes if the value is quoted
        if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        return value
    
    for i, (orig_row, conv_row) in enumerate(zip(original_csv_rows, converted_csv_rows)):
        if len(orig_row) != len(conv_row):
            differences.append(f"Row {i}: Column count mismatch - original: {len(orig_row)}, converted: {len(conv_row)}")
            continue
            
        for j, (orig_cell, conv_cell) in enumerate(zip(orig_row, conv_row)):
            # Normalize both values to handle CSV quoting differences
            orig_normalized = normalize_csv_value(orig_cell)
            conv_normalized = normalize_csv_value(conv_cell)
            
            if orig_normalized != conv_normalized:
                differences.append(f"Row {i}, Col {j}: '{orig_cell}' vs '{conv_cell}'")
    
    # Return success if no differences found
    if len(differences) == 0:
        return True, []
    else:
        return False, differences

def test_structured_file(file_path, show_results=True):
    """Test encoding and decoding for a single structured text file."""
    if isinstance(file_path, str):
        file_name = os.path.basename(file_path)
    else:
        file_name = file_path.name
    
    if show_results:
        print(f"\n{'='*60}")
        print(f"Testing Structured: {file_name}")
        print(f"{'='*60}")
    
    try:
        # Step 1: Load original structured text
        if show_results:
            print("1. Loading original structured text...")
        with open(file_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        if not original_text.strip():
            if show_results:
                print("   ❌ ERROR: File is empty, skipping")
            return False, "Empty file"
        
        if show_results:
            print(f"   ✅ Loaded {len(original_text)} characters")
        
        # Step 2: Parse and encode to TTLV binary
        if show_results:
            print("2. Encoding to TTLV binary...")
        try:
            structured_data = load_from_structured_text_file(str(file_path))
            encoder = encode_from_structured_text(original_text)
            ttlv_binary = encoder.get_buffer()  # Get the actual binary data
            if show_results:
                print(f"   ✅ Encoded to {len(ttlv_binary)} bytes")
        except Exception as e:
            if show_results:
                print(f"   ❌ Encoding failed: {e}")
            return False, f"Encoding error: {e}"
        
        # Step 3: Decode back to structured text
        if show_results:
            print("3. Decoding back to structured text...")
        try:
            decoded_text = decode_ttlv_binary(ttlv_binary)
            if show_results:
                print(f"   ✅ Decoded to {len(decoded_text)} characters")
        except Exception as e:
            if show_results:
                print(f"   ❌ Decoding failed: {e}")
            return False, f"Decoding error: {e}"
        
        # Step 4: Compare original and decoded
        if show_results:
            print("4. Comparing original and decoded...")
        matches, differences = compare_structures(original_text, decoded_text)
        
        if matches:
            if show_results:
                print("   ✅ SUCCESS: PERFECT MATCH - Round-trip successful!")
            return True, "Success"
        else:
            # Always show failures, even when hiding results
            if not show_results:
                print(f"\n{'='*60}")
                print(f"❌ FAILED: Structured: {file_name}")
                print(f"{'='*60}")
            print("   ⚠️  DIFFERENCES FOUND:")
            for diff in differences[:10]:  # Show first 10 differences
                print(f"      {diff}")
            if len(differences) > 10:
                print(f"      ... and {len(differences) - 10} more differences")
            return False, f"Comparison failed: {len(differences)} differences"
            
    except Exception as e:
        # Always show errors, even when hiding results
        if not show_results:
            print(f"\n{'='*60}")
            print(f"❌ ERROR: Structured: {file_name}")
            print(f"{'='*60}")
        print(f"   ❌ ERROR: Unexpected error: {e}")
        print(f"   Stack trace: {traceback.format_exc()}")
        return False, f"Unexpected error: {e}"

def test_json_file(file_path, show_results=True):
    """Test encoding and decoding for a single JSON file."""
    if isinstance(file_path, str):
        file_name = os.path.basename(file_path)
    else:
        file_name = file_path.name
    
    if show_results:
        print(f"\n{'='*60}")
        print(f"Testing JSON: {file_name}")
        print(f"{'='*60}")
    
    try:
        # Step 1: Load original JSON
        if show_results:
            print("1. Loading original JSON...")
        with open(file_path, 'r', encoding='utf-8') as f:
            original_json = json.load(f)
        
        if not original_json:
            if show_results:
                print("   ❌ ERROR: File is empty, skipping")
            return False, "Empty file"
        
        if show_results:
            print(f"   ✅ Loaded {len(json.dumps(original_json))} characters")
        
        # Step 2: Encode to TTLV binary
        if show_results:
            print("2. Encoding JSON to TTLV binary...")
        try:
            # Encode using the same approach as the main script
            encoder = encode_ttlv_structure(original_json)
            ttlv_binary = encoder.get_buffer()
            if show_results:
                print(f"   ✅ Encoded to {len(ttlv_binary)} bytes")
        except Exception as e:
            if show_results:
                print(f"   ❌ Encoding failed: {e}")
            return False, f"Encoding error: {e}"
        
        # Step 3: Decode back to structured text
        if show_results:
            print("3. Decoding back to structured text...")
        try:
            decoded_text = decode_ttlv_binary(ttlv_binary)
            if show_results:
                print(f"   ✅ Decoded to {len(decoded_text)} characters")
        except Exception as e:
            if show_results:
                print(f"   ❌ Decoding failed: {e}")
            return False, f"Decoding error: {e}"
        
        # Step 4: Convert structured text back to JSON
        if show_results:
            print("4. Converting structured text back to JSON...")
        try:
            converted_json = convert_structured_to_json(decoded_text)
            if show_results:
                print(f"   ✅ Converted back to JSON")
        except Exception as e:
            if show_results:
                print(f"   ❌ Conversion failed: {e}")
            return False, f"Conversion error: {e}"
        
        # Step 5: Compare original JSON with converted JSON
        if show_results:
            print("5. Comparing original and converted JSON...")
        matches, differences = compare_json_structures(original_json, converted_json)
        
        if matches:
            if show_results:
                print("   ✅ SUCCESS: PERFECT MATCH - Round-trip successful!")
            return True, "Success"
        else:
            # Always show failures, even when hiding results
            if not show_results:
                print(f"\n{'='*60}")
                print(f"❌ FAILED: JSON: {file_name}")
                print(f"{'='*60}")
            print("   ⚠️  DIFFERENCES FOUND:")
            for diff in differences[:10]:  # Show first 10 differences
                print(f"      {diff}")
            if len(differences) > 10:
                print(f"      ... and {len(differences) - 10} more differences")
            return False, f"Comparison failed: {len(differences)} differences"
            
    except Exception as e:
        # Always show errors, even when hiding results
        if not show_results:
            print(f"\n{'='*60}")
            print(f"❌ ERROR: JSON: {file_name}")
            print(f"{'='*60}")
        print(f"   ❌ ERROR: Unexpected error: {e}")
        print(f"   Stack trace: {traceback.format_exc()}")
        return False, f"Unexpected error: {e}"

def test_csv_file(file_path, show_results=True):
    """Test encoding and decoding for a single CSV file."""
    if isinstance(file_path, str):
        file_name = os.path.basename(file_path)
    else:
        file_name = file_path.name
    
    if show_results:
        print(f"\n{'='*60}")
        print(f"Testing CSV: {file_name}")
        print(f"{'='*60}")
    
    try:
        # Step 1: Load original CSV
        if show_results:
            print("1. Loading original CSV...")
        original_csv_rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            original_csv_rows = list(csv_reader)
        
        if not original_csv_rows or len(original_csv_rows) == 0:  # Empty file
            if show_results:
                print("   ❌ ERROR: File is empty, skipping")
            return False, "Empty file"
        
        if show_results:
            print(f"   ✅ Loaded {len(original_csv_rows)} rows")
        
        # Step 2: Encode to TTLV binary using CSV format
        if show_results:
            print("2. Encoding CSV to TTLV binary...")
        try:
            # Use the same approach as the main script for CSV files
            elements = load_from_text_file(str(file_path))
            encoder = encode_ttlv_structure(elements)
            ttlv_binary = encoder.get_buffer()
            if show_results:
                print(f"   ✅ Encoded to {len(ttlv_binary)} bytes")
        except Exception as e:
            if show_results:
                print(f"   ❌ Encoding failed: {e}")
            return False, f"Encoding error: {e}"
        
        # Step 3: Decode back to structured text
        if show_results:
            print("3. Decoding back to structured text...")
        try:
            decoded_text = decode_ttlv_binary(ttlv_binary)
            if show_results:
                print(f"   ✅ Decoded to {len(decoded_text)} characters")
        except Exception as e:
            if show_results:
                print(f"   ❌ Decoding failed: {e}")
            return False, f"Decoding error: {e}"
        
        # Step 4: Convert structured text back to CSV
        if show_results:
            print("4. Converting structured text back to CSV...")
        try:
            converted_csv_rows = convert_structured_to_csv(decoded_text)
            # Don't add header row since original doesn't have one
            if show_results:
                print(f"   ✅ Converted back to CSV ({len(converted_csv_rows)} rows)")
        except Exception as e:
            if show_results:
                print(f"   ❌ Conversion failed: {e}")
            return False, f"Conversion error: {e}"
        
        # Step 5: Compare original CSV with converted CSV
        if show_results:
            print("5. Comparing original and converted CSV...")
        matches, differences = compare_csv_structures(original_csv_rows, converted_csv_rows)
        
        if matches:
            if show_results:
                print("   ✅ SUCCESS: PERFECT MATCH - Round-trip successful!")
            return True, "Success"
        else:
            # Always show failures, even when hiding results
            if not show_results:
                print(f"\n{'='*60}")
                print(f"❌ FAILED: CSV: {file_name}")
                print(f"{'='*60}")
            print("   ⚠️  DIFFERENCES FOUND:")
            for diff in differences[:10]:  # Show first 10 differences
                print(f"      {diff}")
            if len(differences) > 10:
                print(f"      ... and {len(differences) - 10} more differences")
            return False, f"Comparison failed: {len(differences)} differences"
            
    except Exception as e:
        # Always show errors, even when hiding results
        if not show_results:
            print(f"\n{'='*60}")
            print(f"❌ ERROR: CSV: {file_name}")
            print(f"{'='*60}")
        print(f"   ❌ ERROR: Unexpected error: {e}")
        print(f"   Stack trace: {traceback.format_exc()}")
        return False, f"Unexpected error: {e}"

def main():
    """Main function to test files in both structured and JSON formats."""
    parser = argparse.ArgumentParser(description='TTLV Round-Trip Validation Script')
    parser.add_argument('--format', choices=['structured', 'json', 'csv', 'all'], default='all',
                        help='Test format: structured text, JSON, CSV, or all (default: all)')
    parser.add_argument('--show-results', action='store_true',
                        help='Show detailed results for all tests (default: hide successful tests)')
    parser.add_argument('--all-files-summary', choices=['failed', 'off', 'all'], default='failed',
                        help='Control ALL FILES SUMMARY display: failed=show only failed files (default), off=show nothing, all=show all files')
    args = parser.parse_args()
    
    print("🧪 TTLV Round-Trip Validation Script")
    print("=" * 50)
    
    # Show results only if explicitly requested
    show_results = args.show_results
    
    total_passed = 0
    total_failed = 0
    all_results = []
    
    # Test structured text files
    if args.format in ['structured', 'all']:
        print("\n🔤 Testing Structured Text Files")
        print("-" * 50)
        
        structured_dir = Path("test_cases/structured")
        if not structured_dir.exists():
            print(f"❌ ERROR: Directory {structured_dir} not found!")
        else:
            txt_files = list(structured_dir.glob("*.txt"))
            if not txt_files:
                print(f"❌ ERROR: No .txt files found in {structured_dir}")
            else:
                print(f"📁 Found {len(txt_files)} structured text files to test")
                
                passed = 0
                failed = 0
                
                for file_path in sorted(txt_files):
                    success, message = test_structured_file(file_path, show_results)
                    all_results.append((f"📄 {file_path.name}", success, message))
                    
                    if success:
                        passed += 1
                        total_passed += 1
                    else:
                        failed += 1
                        total_failed += 1
                
                print(f"\n📊 Structured Text Summary: ✅ {passed} passed, ❌ {failed} failed")
    
    # Test JSON files
    if args.format in ['json', 'all']:
        print("\n🔧 Testing JSON Files")
        print("-" * 50)
        
        json_dir = Path("test_cases/json")
        if not json_dir.exists():
            print(f"❌ ERROR: Directory {json_dir} not found!")
        else:
            json_files = list(json_dir.glob("*.json"))
            if not json_files:
                print(f"❌ ERROR: No .json files found in {json_dir}")
            else:
                print(f"📁 Found {len(json_files)} JSON files to test")
                
                passed = 0
                failed = 0
                
                for file_path in sorted(json_files):
                    success, message = test_json_file(file_path, show_results)
                    all_results.append((f"🔧 {file_path.name}", success, message))
                    
                    if success:
                        passed += 1
                        total_passed += 1
                    else:
                        failed += 1
                        total_failed += 1
                
                print(f"\n📊 JSON Summary: ✅ {passed} passed, ❌ {failed} failed")
    
    # Test CSV files
    if args.format in ['csv', 'all']:
        print("\n📊 Testing CSV Files")
        print("-" * 50)
        
        csv_dir = Path("test_cases/csv")
        if not csv_dir.exists():
            print(f"❌ ERROR: Directory {csv_dir} not found!")
        else:
            csv_files = list(csv_dir.glob("*.csv"))
            if not csv_files:
                print(f"❌ ERROR: No .csv files found in {csv_dir}")
            else:
                print(f"📁 Found {len(csv_files)} CSV files to test")
                
                passed = 0
                failed = 0
                
                for file_path in sorted(csv_files):
                    success, message = test_csv_file(file_path, show_results)
                    all_results.append((f"📊 {file_path.name}", success, message))
                    
                    if success:
                        passed += 1
                        total_passed += 1
                    else:
                        failed += 1
                        total_failed += 1
                
                print(f"\n📊 CSV Summary: ✅ {passed} passed, ❌ {failed} failed")
    
    # Print overall summary
    print(f"\n{'='*80}")
    print("📊 OVERALL SUMMARY")
    print(f"{'='*80}")
    print(f"📈 Total files tested: {total_passed + total_failed}")
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    if total_passed + total_failed > 0:
        print(f"📊 Success rate: {(total_passed/(total_passed + total_failed)*100):.1f}%")
    
    if total_failed > 0:
        print(f"\n{'='*50}")
        print("💥 FAILED FILES:")
        print(f"{'='*50}")
        for filename, success, message in all_results:
            if not success:
                print(f"❌ {filename}: {message}")
    
    # Display ALL FILES SUMMARY based on the --all-files-summary flag
    if args.all_files_summary != 'off':
        
        if args.all_files_summary == 'failed':
            # Show only failed files
            print(f"\n{'='*50}")
            print("📋 FAILED FILES SUMMARY:")
            print(f"{'='*50}")
            failed_files = [result for result in all_results if not result[1]]
            if failed_files:
                for filename, success, message in failed_files:
                    print(f"❌ FAIL {filename}")
            else:
                print("✅ No failed files to display")
        elif args.all_files_summary == 'all':
            print(f"\n{'='*50}")
            print("📋 ALL FILES SUMMARY:")
            print(f"{'='*50}")
            # Show all files
            for filename, success, message in all_results:
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{status} {filename}")
    
    # Exit with error code if any tests failed
    if total_failed > 0:
        print(f"\n⚠️  {total_failed} test(s) failed. Check the output above for details.")
        sys.exit(1)
    else:
        print(f"\n🎉 All {total_passed} tests passed successfully!")

if __name__ == "__main__":
    main()
