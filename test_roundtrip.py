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

Usage:
    python test_roundtrip.py [--format structured|json|both]
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
    from encode_ttlv import load_from_structured_text_file, encode_from_structured_text, load_from_json_file, encode_ttlv_structure
    from decode_ttlv import DecodeTTLV
    from helpers.convert_to_json import convert_structured_to_json
    import subprocess
    import io
    from contextlib import redirect_stdout
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure encode_ttlv.py, decode_ttlv.py, and helpers/convert_to_json.py are available")
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

def test_structured_file(file_path):
    """Test encoding and decoding for a single structured text file."""
    if isinstance(file_path, str):
        file_name = os.path.basename(file_path)
    else:
        file_name = file_path.name
    
    print(f"\n{'='*60}")
    print(f"Testing Structured: {file_name}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Load original structured text
        print("1. Loading original structured text...")
        with open(file_path, 'r', encoding='utf-8') as f:
            original_text = f.read()
        
        if not original_text.strip():
            print("   ❌ ERROR: File is empty, skipping")
            return False, "Empty file"
        
        print(f"   ✅ Loaded {len(original_text)} characters")
        
        # Step 2: Parse and encode to TTLV binary
        print("2. Encoding to TTLV binary...")
        try:
            structured_data = load_from_structured_text_file(str(file_path))
            encoder = encode_from_structured_text(original_text)
            ttlv_binary = encoder.get_buffer()  # Get the actual binary data
            print(f"   ✅ Encoded to {len(ttlv_binary)} bytes")
        except Exception as e:
            print(f"   ❌ Encoding failed: {e}")
            return False, f"Encoding error: {e}"
        
        # Step 3: Decode back to structured text
        print("3. Decoding back to structured text...")
        try:
            decoded_text = decode_ttlv_binary(ttlv_binary)
            print(f"   ✅ Decoded to {len(decoded_text)} characters")
        except Exception as e:
            print(f"   ❌ Decoding failed: {e}")
            return False, f"Decoding error: {e}"
        
        # Step 4: Compare original and decoded
        print("4. Comparing original and decoded...")
        matches, differences = compare_structures(original_text, decoded_text)
        
        if matches:
            print("   ✅ SUCCESS: PERFECT MATCH - Round-trip successful!")
            return True, "Success"
        else:
            print("   ⚠️  DIFFERENCES FOUND:")
            for diff in differences[:10]:  # Show first 10 differences
                print(f"      {diff}")
            if len(differences) > 10:
                print(f"      ... and {len(differences) - 10} more differences")
            return False, f"Comparison failed: {len(differences)} differences"
            
    except Exception as e:
        print(f"   ❌ ERROR: Unexpected error: {e}")
        print(f"   Stack trace: {traceback.format_exc()}")
        return False, f"Unexpected error: {e}"

def test_json_file(file_path):
    """Test encoding and decoding for a single JSON file."""
    if isinstance(file_path, str):
        file_name = os.path.basename(file_path)
    else:
        file_name = file_path.name
    
    print(f"\n{'='*60}")
    print(f"Testing JSON: {file_name}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Load original JSON
        print("1. Loading original JSON...")
        with open(file_path, 'r', encoding='utf-8') as f:
            original_json = json.load(f)
        
        if not original_json:
            print("   ❌ ERROR: File is empty, skipping")
            return False, "Empty file"
        
        print(f"   ✅ Loaded {len(json.dumps(original_json))} characters")
        
        # Step 2: Encode to TTLV binary
        print("2. Encoding JSON to TTLV binary...")
        try:
            # Encode using the same approach as the main script
            encoder = encode_ttlv_structure(original_json)
            ttlv_binary = encoder.get_buffer()
            print(f"   ✅ Encoded to {len(ttlv_binary)} bytes")
        except Exception as e:
            print(f"   ❌ Encoding failed: {e}")
            return False, f"Encoding error: {e}"
        
        # Step 3: Decode back to structured text
        print("3. Decoding back to structured text...")
        try:
            decoded_text = decode_ttlv_binary(ttlv_binary)
            print(f"   ✅ Decoded to {len(decoded_text)} characters")
        except Exception as e:
            print(f"   ❌ Decoding failed: {e}")
            return False, f"Decoding error: {e}"
        
        # Step 4: Convert structured text back to JSON
        print("4. Converting structured text back to JSON...")
        try:
            converted_json = convert_structured_to_json(decoded_text)
            print(f"   ✅ Converted back to JSON")
        except Exception as e:
            print(f"   ❌ Conversion failed: {e}")
            return False, f"Conversion error: {e}"
        
        # Step 5: Compare original JSON with converted JSON
        print("5. Comparing original and converted JSON...")
        matches, differences = compare_json_structures(original_json, converted_json)
        
        if matches:
            print("   ✅ SUCCESS: PERFECT MATCH - Round-trip successful!")
            return True, "Success"
        else:
            print("   ⚠️  DIFFERENCES FOUND:")
            for diff in differences[:10]:  # Show first 10 differences
                print(f"      {diff}")
            if len(differences) > 10:
                print(f"      ... and {len(differences) - 10} more differences")
            return False, f"Comparison failed: {len(differences)} differences"
            
    except Exception as e:
        print(f"   ❌ ERROR: Unexpected error: {e}")
        print(f"   Stack trace: {traceback.format_exc()}")
        return False, f"Unexpected error: {e}"

def main():
    """Main function to test files in both structured and JSON formats."""
    parser = argparse.ArgumentParser(description='TTLV Round-Trip Validation Script')
    parser.add_argument('--format', choices=['structured', 'json', 'both'], default='both',
                        help='Test format: structured text, JSON, or both (default: both)')
    args = parser.parse_args()
    
    print("🧪 TTLV Round-Trip Validation Script")
    print("=" * 50)
    
    total_passed = 0
    total_failed = 0
    all_results = []
    
    # Test structured text files
    if args.format in ['structured', 'both']:
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
                    success, message = test_structured_file(file_path)
                    all_results.append((f"📄 {file_path.name}", success, message))
                    
                    if success:
                        passed += 1
                        total_passed += 1
                    else:
                        failed += 1
                        total_failed += 1
                
                print(f"\n📊 Structured Text Summary: ✅ {passed} passed, ❌ {failed} failed")
    
    # Test JSON files
    if args.format in ['json', 'both']:
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
                    success, message = test_json_file(file_path)
                    all_results.append((f"🔧 {file_path.name}", success, message))
                    
                    if success:
                        passed += 1
                        total_passed += 1
                    else:
                        failed += 1
                        total_failed += 1
                
                print(f"\n📊 JSON Summary: ✅ {passed} passed, ❌ {failed} failed")
    
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
    
    print(f"\n{'='*50}")
    print("📋 ALL FILES SUMMARY:")
    print(f"{'='*50}")
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
