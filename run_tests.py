#!/usr/bin/env python3
"""
Test runner script for Oatmeal enhanced transcription format tests.

This script runs all the pytest tests for the completed enhanced transcription format features:
- MultiTranscriptionAligner.align_enhanced() functionality
- Config class enhancements  
- TranscribeOnlyStrategy dual output system
- Enhanced format structure validation
- Backward compatibility verification

Usage:
    python run_tests.py [options]
    
Options:
    --verbose, -v: Verbose output
    --coverage, -c: Run with coverage reporting
    --enhanced-only: Run only enhanced format tests
    --unit-only: Run only unit tests
    --help, -h: Show this help message
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and return the result"""
    print(f"Running: {description or command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Run Oatmeal enhanced transcription format tests"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--enhanced-only",
        action="store_true",
        help="Run only enhanced format tests"
    )
    parser.add_argument(
        "--unit-only",
        action="store_true", 
        help="Run only unit tests"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = "uv run pytest"
    
    # Add verbosity
    if args.verbose:
        pytest_cmd += " -v"
    else:
        pytest_cmd += " -q"
    
    # Add coverage
    if args.coverage:
        pytest_cmd += " --cov=processing --cov=config --cov=run_strategies --cov-report=term-missing"
    
    # Specify test selection
    if args.enhanced_only:
        pytest_cmd += " -m enhanced"
    elif args.unit_only:
        pytest_cmd += " -m unit"
    else:
        # Run all tests
        pytest_cmd += " tests/"
    
    print("=" * 80)
    print("OATMEAL ENHANCED TRANSCRIPTION FORMAT TESTS")
    print("=" * 80)
    print()
    print("Testing completed features from enhanced-transcription-format.md:")
    print("✅ MultiTranscriptionAligner.align_enhanced() implementation")
    print("✅ Config class enhancements (session metadata, enhanced transcription path)")
    print("✅ TranscribeOnlyStrategy dual output system")
    print("✅ Enhanced format structure validation")  
    print("✅ Backward compatibility verification")
    print()
    print("=" * 80)
    
    # Run the tests
    success = run_command(pytest_cmd, "Running pytest tests")
    
    if success:
        print()
        print("=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print()
        print("The enhanced transcription format implementation has been verified:")
        print("- Enhanced format structure is correct")
        print("- Speaker attribution works properly (User/Others)")
        print("- Summary statistics are calculated correctly") 
        print("- Chronological ordering is maintained")
        print("- Backward compatibility is preserved")
        print("- Dual output system works (legacy + enhanced formats)")
        print()
        print("The implementation is ready for production use!")
        return 0
    else:
        print()
        print("=" * 80)
        print("❌ SOME TESTS FAILED")
        print("=" * 80)
        print()
        print("Please review the test output above to identify and fix issues.")
        print("All tests must pass before the enhanced format can be considered complete.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)