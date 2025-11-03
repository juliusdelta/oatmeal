"""
Tests for enhanced transcription format structure validation.

Tests all completed features from the enhanced transcription format:
- Complete enhanced format structure validation
- Required fields verification
- Data type validation
- Format compliance with specification
- JSON schema validation
"""

import json
from jsonschema import validate, ValidationError

from processing.multi_transcription_aligner import MultiTranscriptionAligner


class TestEnhancedFormatStructure:
    """Test suite for enhanced transcription format structure validation"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        # Sample test data
        self.user_timestamps = [
            {"timestamp": [0.0, 2.5], "text": "Hello, this is the user speaking"},
            {"timestamp": [5.0, 7.2], "text": "I'm asking a question"}
        ]
        
        self.monitor_timestamps = [
            {"timestamp": [2.8, 4.9], "text": "System response here"},
            {"timestamp": [7.5, 9.3], "text": "This is the answer"}
        ]
        
        self.session_metadata = {
            "timestamp": "2025-11-03_10-30-00",
            "duration_seconds": 15.2
        }
        
        # Expected JSON schema for enhanced format
        self.enhanced_format_schema = {
            "type": "object",
            "required": ["session_metadata", "conversation", "summary_hints"],
            "properties": {
                "session_metadata": {
                    "type": "object",
                    "required": ["timestamp", "duration_seconds", "total_segments", "channels"],
                    "properties": {
                        "timestamp": {"type": "string"},
                        "duration_seconds": {"type": "number"},
                        "total_segments": {"type": "integer", "minimum": 0},
                        "channels": {
                            "type": "object",
                            "required": ["mic", "monitor"],
                            "properties": {
                                "mic": {"type": "string", "enum": ["User"]},
                                "monitor": {"type": "string", "enum": ["Others"]}
                            }
                        }
                    }
                },
                "conversation": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["speaker", "start_time", "end_time", "duration", "text", "source"],
                        "properties": {
                            "speaker": {"type": "string", "enum": ["User", "Others"]},
                            "start_time": {"type": "number", "minimum": 0},
                            "end_time": {"type": "number", "minimum": 0},
                            "duration": {"type": "number", "minimum": 0},
                            "text": {"type": "string"},
                            "source": {"type": "string", "enum": ["mic", "monitor"]}
                        }
                    }
                },
                "summary_hints": {
                    "type": "object",
                    "required": ["user_talk_time_seconds", "others_talk_time_seconds", "silence_gaps", "avg_segment_length", "total_segments"],
                    "properties": {
                        "user_talk_time_seconds": {"type": "number", "minimum": 0},
                        "others_talk_time_seconds": {"type": "number", "minimum": 0},
                        "silence_gaps": {"type": "integer", "minimum": 0},
                        "avg_segment_length": {"type": "number", "minimum": 0},
                        "total_segments": {"type": "integer", "minimum": 0}
                    }
                }
            }
        }
    
    def test_enhanced_format_schema_compliance(self):
        """Test that generated enhanced format complies with the expected schema"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        # Should not raise ValidationError if schema is valid
        try:
            validate(instance=result, schema=self.enhanced_format_schema)
        except ValidationError as e:
            assert False, f"Enhanced format does not comply with schema: {e.message}"
    
    def test_session_metadata_structure(self):
        """Test that session_metadata has all required fields with correct types"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        session_meta = result["session_metadata"]
        
        # Required fields
        assert "timestamp" in session_meta
        assert "duration_seconds" in session_meta
        assert "total_segments" in session_meta
        assert "channels" in session_meta
        
        # Data types
        assert isinstance(session_meta["timestamp"], str)
        assert isinstance(session_meta["duration_seconds"], (int, float))
        assert isinstance(session_meta["total_segments"], int)
        assert isinstance(session_meta["channels"], dict)
        
        # Channel structure
        channels = session_meta["channels"]
        assert channels["mic"] == "User"
        assert channels["monitor"] == "Others"
        
        # Value constraints
        assert session_meta["total_segments"] >= 0
        assert session_meta["duration_seconds"] >= 0
    
    def test_conversation_structure(self):
        """Test that conversation array has correct structure for all segments"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        # Should be a list
        assert isinstance(conversation, list)
        assert len(conversation) > 0
        
        # Test each segment structure
        for segment in conversation:
            # Required fields
            required_fields = ["speaker", "start_time", "end_time", "duration", "text", "source"]
            for field in required_fields:
                assert field in segment, f"Missing required field: {field}"
            
            # Data types
            assert isinstance(segment["speaker"], str)
            assert isinstance(segment["start_time"], (int, float))
            assert isinstance(segment["end_time"], (int, float))
            assert isinstance(segment["duration"], (int, float))
            assert isinstance(segment["text"], str)
            assert isinstance(segment["source"], str)
            
            # Value constraints
            assert segment["speaker"] in ["User", "Others"]
            assert segment["source"] in ["mic", "monitor"]
            assert segment["start_time"] >= 0
            assert segment["end_time"] >= 0
            assert segment["duration"] >= 0
            assert segment["end_time"] > segment["start_time"]
            assert len(segment["text"]) > 0
            
            # Speaker-source consistency
            if segment["speaker"] == "User":
                assert segment["source"] == "mic"
            elif segment["speaker"] == "Others":
                assert segment["source"] == "monitor"
    
    def test_summary_hints_structure(self):
        """Test that summary_hints has all required fields with correct types"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        hints = result["summary_hints"]
        
        # Required fields
        required_fields = ["user_talk_time_seconds", "others_talk_time_seconds", "silence_gaps", "avg_segment_length", "total_segments"]
        for field in required_fields:
            assert field in hints, f"Missing required field: {field}"
        
        # Data types and constraints
        assert isinstance(hints["user_talk_time_seconds"], (int, float))
        assert isinstance(hints["others_talk_time_seconds"], (int, float))
        assert isinstance(hints["silence_gaps"], int)
        assert isinstance(hints["avg_segment_length"], (int, float))
        assert isinstance(hints["total_segments"], int)
        
        # Value constraints
        assert hints["user_talk_time_seconds"] >= 0
        assert hints["others_talk_time_seconds"] >= 0
        assert hints["silence_gaps"] >= 0
        assert hints["avg_segment_length"] >= 0
        assert hints["total_segments"] >= 0
    
    def test_enhanced_format_json_serializable(self):
        """Test that enhanced format can be serialized to JSON"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        # Should not raise exception
        try:
            json_str = json.dumps(result, ensure_ascii=False, indent=4)
            assert len(json_str) > 0
            
            # Should be able to parse back
            parsed = json.loads(json_str)
            assert parsed == result
            
        except (TypeError, ValueError) as e:
            assert False, f"Enhanced format is not JSON serializable: {e}"
    
    def test_enhanced_format_with_empty_conversation(self):
        """Test enhanced format structure when conversation is empty"""
        result = MultiTranscriptionAligner.align_enhanced(
            [], [], self.session_metadata
        )
        
        # Should still comply with schema
        try:
            validate(instance=result, schema=self.enhanced_format_schema)
        except ValidationError as e:
            assert False, f"Empty conversation format does not comply with schema: {e.message}"
        
        # Specific checks for empty case
        assert result["conversation"] == []
        assert result["summary_hints"]["total_segments"] == 0
        assert result["summary_hints"]["user_talk_time_seconds"] == 0
        assert result["summary_hints"]["others_talk_time_seconds"] == 0
    
    def test_chronological_ordering_validation(self):
        """Test that conversation segments are in chronological order"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        # Verify chronological ordering
        for i in range(1, len(conversation)):
            assert conversation[i]["start_time"] >= conversation[i-1]["start_time"], \
                f"Segments not in chronological order: {conversation[i-1]['start_time']} > {conversation[i]['start_time']}"
    
    def test_duration_calculation_accuracy(self):
        """Test that duration calculations are accurate for all segments"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        for segment in conversation:
            expected_duration = round(segment["end_time"] - segment["start_time"], 2)
            assert segment["duration"] == expected_duration, \
                f"Duration calculation incorrect: expected {expected_duration}, got {segment['duration']}"
    
    def test_speaker_source_consistency(self):
        """Test that speaker and source fields are consistent throughout"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        for segment in conversation:
            if segment["source"] == "mic":
                assert segment["speaker"] == "User", \
                    f"Mic source should have User speaker, got {segment['speaker']}"
            elif segment["source"] == "monitor":
                assert segment["speaker"] == "Others", \
                    f"Monitor source should have Others speaker, got {segment['speaker']}"
    
    def test_summary_hints_consistency(self):
        """Test that summary hints are consistent with conversation data"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        hints = result["summary_hints"]
        
        # Calculate expected values
        user_segments = [seg for seg in conversation if seg["speaker"] == "User"]
        others_segments = [seg for seg in conversation if seg["speaker"] == "Others"]
        
        expected_user_time = sum(seg["duration"] for seg in user_segments)
        expected_others_time = sum(seg["duration"] for seg in others_segments)
        expected_total_segments = len(conversation)
        expected_avg_length = round(sum(seg["duration"] for seg in conversation) / len(conversation), 2) if conversation else 0
        
        # Verify consistency
        assert hints["user_talk_time_seconds"] == round(expected_user_time, 2)
        assert hints["others_talk_time_seconds"] == round(expected_others_time, 2)
        assert hints["total_segments"] == expected_total_segments
        assert hints["avg_segment_length"] == expected_avg_length
        
        # Total segments should match session metadata
        assert hints["total_segments"] == result["session_metadata"]["total_segments"]
    
    def test_text_content_preservation(self):
        """Test that original text content is preserved in enhanced format"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        # Collect all texts by source
        user_texts = [seg["text"] for seg in conversation if seg["source"] == "mic"]
        monitor_texts = [seg["text"] for seg in conversation if seg["source"] == "monitor"]
        
        # Original texts
        original_user_texts = [seg["text"] for seg in self.user_timestamps]
        original_monitor_texts = [seg["text"] for seg in self.monitor_timestamps]
        
        # Verify all original texts are preserved
        assert set(user_texts) == set(original_user_texts)
        assert set(monitor_texts) == set(original_monitor_texts)
    
    def test_timestamp_preservation_and_conversion(self):
        """Test that original timestamp data is correctly converted to enhanced format"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        # Create mapping of text to original timestamp for verification
        original_timestamps = {}
        for seg in self.user_timestamps + self.monitor_timestamps:
            original_timestamps[seg["text"]] = seg["timestamp"]
        
        # Verify timestamp conversion
        for segment in conversation:
            original_timestamp = original_timestamps[segment["text"]]
            assert segment["start_time"] == original_timestamp[0]
            assert segment["end_time"] == original_timestamp[1]
    
    def test_enhanced_format_completeness(self):
        """Test that enhanced format includes all required top-level sections"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        # Top-level structure must be complete
        required_sections = ["session_metadata", "conversation", "summary_hints"]
        
        for section in required_sections:
            assert section in result, f"Missing required section: {section}"
            assert result[section] is not None, f"Section {section} is None"
        
        # Verify no extra fields at top level (strict structure)
        for key in result.keys():
            assert key in required_sections, f"Unexpected top-level field: {key}"
    
    def test_session_metadata_integration(self):
        """Test that input session metadata is properly integrated and enhanced"""
        custom_metadata = {
            "timestamp": "2025-11-03_15-45-30",
            "duration_seconds": 120.5,
            "custom_field": "test_value",
            "another_field": 42
        }
        
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            custom_metadata
        )
        
        session_meta = result["session_metadata"]
        
        # Original metadata should be preserved
        assert session_meta["timestamp"] == "2025-11-03_15-45-30"
        assert session_meta["duration_seconds"] == 120.5
        assert session_meta["custom_field"] == "test_value"
        assert session_meta["another_field"] == 42
        
        # Enhanced metadata should be added
        assert session_meta["total_segments"] == 4  # 2 user + 2 monitor
        assert session_meta["channels"] == {"mic": "User", "monitor": "Others"}