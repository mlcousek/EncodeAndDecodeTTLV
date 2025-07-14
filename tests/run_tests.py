#!/usr/bin/env python

"""
Test Runner for TTLV Encoder
This script runs both basic tests and KMIP protocol tests
"""

import subprocess
import sys
import os

def run_test_file(filename, description):
    """Run a test file and capture output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {filename}")
    print('='*60)
    
    try:
        # Run the test file
        result = subprocess.run([sys.executable, filename], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("[SUCCESS]")
            print("\nOutput:")
            print(result.stdout)
        else:
            print("[FAILED]")
            print("\nStdout:")
            print(result.stdout)
            print("\nStderr:")
            print(result.stderr)
            
    except Exception as e:
        print(f"[ERROR] running {filename}: {e}")

def run_basic_encoder_test():
    """Run the built-in encoder test"""
    print(f"\n{'='*60}")
    print("Running: Built-in Encoder Test")
    print("Command: python ../encode_ttlv.py test")
    print('='*60)
    
    try:
        result = subprocess.run([sys.executable, '../encode_ttlv.py', 'test'],
                              capture_output=True,
                              text=True,
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print("[SUCCESS]")
            print("\nOutput:")
            print(result.stdout)
        else:
            print("[FAILED]")
            print("\nStdout:")
            print(result.stdout)
            print("\nStderr:")
            print(result.stderr)
            
    except Exception as e:
        print(f"[ERROR] running built-in test: {e}")

def main():
    print("TTLV Encoder Test Suite Runner")
    print("This will run all available tests for the TTLV encoder")
    
    # Check if we're in the right directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = ['../encode_ttlv.py', '../decode_ttlv.py']

    for file in required_files:
        if not os.path.exists(os.path.join(current_dir, file)):
            print(f"ERROR: Required file {file} not found in {current_dir}")
            return
    
    # Run tests in order
    tests_to_run = [
        ('ttlvEncoder.py', 'Built-in Basic Encoder Test', run_basic_encoder_test),
    ]
    
    # Add test files if they exist
    test_files = [
        ('test_encoder.py', 'Comprehensive Basic Tests'),
        ('kmip_protocol_tests.py', 'KMIP Protocol Structure Tests')
    ]
    
    for filename, description in test_files:
        if os.path.exists(os.path.join(current_dir, filename)):
            tests_to_run.append((filename, description, lambda f=filename, d=description: run_test_file(f, d)))
    
    # Run all tests
    total_tests = len(tests_to_run)
    for i, (filename, description, test_func) in enumerate(tests_to_run, 1):
        print(f"\n\n[{i}/{total_tests}] Starting test...")
        test_func()
    
    print(f"\n\n{'='*60}")
    print("All tests completed!")
    print(f"Total test suites run: {total_tests}")
    print('='*60)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'basic':
            run_basic_encoder_test()
        elif test_type == 'comprehensive':
            if os.path.exists('test_encoder.py'):
                run_test_file('test_encoder.py', 'Comprehensive Basic Tests')
            else:
                print("test_encoder.py not found")
        elif test_type == 'kmip':
            if os.path.exists('kmip_protocol_tests.py'):
                run_test_file('kmip_protocol_tests.py', 'KMIP Protocol Tests')
            else:
                print("kmip_protocol_tests.py not found")
        elif test_type == 'help':
            print("Usage:")
            print("  python run_tests.py          - Run all available tests")
            print("  python run_tests.py basic    - Run only basic encoder test")
            print("  python run_tests.py comprehensive - Run comprehensive basic tests")
            print("  python run_tests.py kmip     - Run KMIP protocol tests")
            print("  python run_tests.py help     - Show this help")
        else:
            print("Unknown test type. Use 'help' for usage information.")
    else:
        main()
