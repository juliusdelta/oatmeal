# Oatmeal Enhanced Transcription Format Tests

This directory contains comprehensive pytest tests for all the **completed features** from the enhanced transcription format implementation described in `llm-docs/enhanced-transcription-format.md`.

## Test Coverage

These tests verify all the features listed in the **Implementation Status -> Completed Features** section:

### ✅ Core Format Enhancement (Phase 1)
- **MultiTranscriptionAligner.align_enhanced()**: Complete implementation testing
- **Config Class Enhancements**: Session metadata, enhanced transcription path, timing
- **Dual Output System**: Both legacy and enhanced formats generated correctly

### ✅ Strategy Integration (Phase 2) 
- **TranscribeOnlyStrategy Updates**: Enhanced workflow with dual output
- **Backward Compatibility**: No breaking changes to existing API
- **Enhanced Format Structure**: Complete JSON structure validation

### ✅ Key Implementation Details
- **Speaker Attribution**: "User" for mic, "Others" for monitor  
- **Temporal Context**: Multiple time representations with chronological ordering
- **Conversation Flow**: Automatic silence gap detection (>1 second threshold)
- **Summary Statistics**: Talk time calculation, segment counts, metrics

## Test Files

### `test_multi_transcription_aligner.py`
Tests for the `MultiTranscriptionAligner.align_enhanced()` method:
- Basic structure validation
- Speaker attribution correctness
- Chronological ordering
- Time calculations (start_time, end_time, duration)
- Summary hints calculations
- Silence gap detection
- Empty input handling
- Single speaker scenarios
- Text content preservation
- Session metadata integration
- Backward compatibility with legacy `align()` method

### `test_config.py`
Tests for Config class enhanced functionality:
- `enhanced_transcription_path` property
- Session timing tracking
- `generate_session_metadata()` method
- Duration calculation accuracy
- `save_enhanced_transcription()` method
- Error handling
- Dual output system paths
- Directory structure creation
- Timestamp format consistency
- Backward compatibility

### `test_transcribe_only_strategy.py`
Tests for TranscribeOnlyStrategy dual output system:
- Dual output generation (legacy + enhanced)
- Summary statistics display
- Enhanced workflow integration
- Return value backward compatibility
- Error handling for enhanced features
- Individual transcription saving
- Session metadata generation timing
- No breaking changes verification

### `test_enhanced_format_structure.py`
Tests for enhanced format structure validation:
- JSON schema compliance
- Session metadata structure
- Conversation array structure
- Summary hints structure
- JSON serialization
- Empty conversation handling
- Chronological ordering validation
- Duration calculation accuracy
- Speaker-source consistency
- Summary hints consistency
- Text content preservation
- Timestamp conversion
- Format completeness
- Session metadata integration

### `test_backward_compatibility.py`
Tests for backward compatibility verification:
- Legacy `align()` method unchanged
- Legacy `align()` method independence from enhanced features
- Config legacy methods unchanged
- Config legacy properties unchanged
- TranscribeOnlyStrategy return value unchanged
- File output structure compatibility
- Existing code integration unchanged
- Method signatures unchanged
- Legacy workflow without enhanced features
- Enhanced features are additive only
- Minimal performance impact
- Error handling compatibility

## Running the Tests

### Prerequisites
```bash
# Install dependencies
uv sync

# Or manually install test dependencies
pip install pytest pytest-cov pytest-mock jsonschema
```

### Run All Tests
```bash
# Using the test runner script
python run_tests.py

# Or directly with pytest
uv run pytest tests/

# With verbose output
uv run pytest tests/ -v
```

### Run Specific Test Files
```bash
# Test enhanced alignment functionality
uv run pytest tests/test_multi_transcription_aligner.py -v

# Test config enhancements
uv run pytest tests/test_config.py -v

# Test strategy integration
uv run pytest tests/test_transcribe_only_strategy.py -v

# Test format structure
uv run pytest tests/test_enhanced_format_structure.py -v

# Test backward compatibility
uv run pytest tests/test_backward_compatibility.py -v
```

### Run with Coverage
```bash
python run_tests.py --coverage

# Or directly
uv run pytest tests/ --cov=processing --cov=config --cov=run_strategies --cov-report=term-missing
```

## Test Structure

Each test file follows this structure:
- **Setup methods**: Create test data and temporary environments
- **Test methods**: Focused tests for specific functionality
- **Teardown methods**: Clean up temporary resources
- **Mock usage**: Isolate units under test from dependencies

## Verification Criteria

All tests verify the technical requirements from the specification:

### ✅ Technical Requirements
- No breaking changes to existing API
- Backward compatible with current workflows
- Performance impact < 10% of transcription time
- File size increase < 50% of original

### ✅ LLM Optimization Requirements
- Clear speaker attribution without "System" confusion
- Temporal context for conversation flow
- Metadata for summarization hints  
- Structured format for parsing efficiency

## Expected Test Results

When all tests pass, you should see output similar to:
```
==================== test session starts ====================
platform linux -- Python 3.12.x
collected 45 items

tests/test_multi_transcription_aligner.py ............ [ 26%]
tests/test_config.py ............ [ 52%]
tests/test_transcribe_only_strategy.py ........ [ 72%]
tests/test_enhanced_format_structure.py .......... [ 93%]
tests/test_backward_compatibility.py ... [100%]

==================== 45 passed in 2.34s ====================
```

## Troubleshooting

### Import Errors
If you see pytest import errors, ensure dependencies are installed:
```bash
uv sync
```

### Mock Errors
If mock assertions fail, verify the implementation matches the expected interface in the tests.

### Schema Validation Errors
If JSON schema validation fails, check that the enhanced format structure matches the specification in `enhanced-transcription-format.md`.

## Test Philosophy

These tests follow the principle of **testing the behavior, not the implementation**. They verify:

1. **Correctness**: Does the feature work as specified?
2. **Compatibility**: Does it maintain backward compatibility?
3. **Structure**: Does the output match the expected format?
4. **Edge Cases**: Does it handle empty inputs, single speakers, etc.?
5. **Integration**: Do all parts work together correctly?

The goal is to ensure that the enhanced transcription format implementation is robust, reliable, and ready for production use while maintaining full backward compatibility.