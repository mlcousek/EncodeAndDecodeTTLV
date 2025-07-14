#!/usr/bin/env python3
"""
TTLV Round-Trip Test Script

This script tests encoding and decoding for all         if not original_text.strip():
            print("   ❌ ERROR: File is empty, skipping")
            return False, "Empty file"
        
        print(f"   📄 ✅ Loaded {len(original_text)} characters")files in the test_cases directory.
It performs the following for each file:
1. Loads the original structured text
2. Encodes it to TTLV binary format
3. Decodes the binary back to structured text
4. Compares the original with the decoded result
5. Reports any differences or errors

Usage:
    python test_roundtrip.py
"""

import os
import sys
import traceback
from pathlib import Path

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from encode_ttlv import load_from_structured_text_file, encode_from_structured_text
    from decode_ttlv import DecodeTTLV
    import subprocess
    import io
    from contextlib import redirect_stdout
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure encode_ttlv.py and decode_ttlv.py are in the current directory")
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

def test_file(file_path):
    """Test encoding and decoding for a single file."""
    if isinstance(file_path, str):
        file_name = os.path.basename(file_path)
    else:
        file_name = file_path.name
    
    print(f"\n{'='*60}")
    print(f"Testing: {file_name}")
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

def main():
    """Main function to test all files in test_cases directory."""
    print("🧪 TTLV Round-Trip Validation Script")
    print("=" * 50)
    
    # Find the test_cases directory
    tests_dir = Path("test_cases")
    if not tests_dir.exists():
        print(f"❌ ERROR: Directory {tests_dir} not found!")
        print("Make sure you're running this script from the project root directory.")
        return
    
    # Find all .txt files
    txt_files = list(tests_dir.glob("*.txt"))
    if not txt_files:
        print(f"❌ ERROR: No .txt files found in {tests_dir}")
        return
    
    print(f"📁 Found {len(txt_files)} .txt files to test")
    
    # Test each file
    results = []
    passed = 0
    failed = 0
    
    for file_path in sorted(txt_files):
        success, message = test_file(file_path)
        results.append((file_path.name, success, message))
        
        if success:
            passed += 1
        else:
            failed += 1
    
    # Print summary
    print(f"\n{'='*80}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"📈 Total files tested: {len(txt_files)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success rate: {(passed/len(txt_files)*100):.1f}%")
    
    if failed > 0:
        print(f"\n{'='*50}")
        print("💥 FAILED FILES:")
        print(f"{'='*50}")
        for filename, success, message in results:
            if not success:
                print(f"❌ {filename}: {message}")
    
    print(f"\n{'='*50}")
    print("📋 ALL FILES SUMMARY:")
    print(f"{'='*50}")
    for filename, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {filename}")
    
    # Exit with error code if any tests failed
    if failed > 0:
        print(f"\n⚠️  {failed} test(s) failed. Check the output above for details.")
        sys.exit(1)
    else:
        print(f"\n🎉 All {passed} tests passed successfully!")

if __name__ == "__main__":
    main()
