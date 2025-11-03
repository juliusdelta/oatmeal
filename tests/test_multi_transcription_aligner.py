"""
Tests for MultiTranscriptionAligner enhanced functionality.

Tests all completed features from the enhanced transcription format:
- align_enhanced() method implementation
- Speaker attribution (User/Others)
- Enhanced format structure
- Summary statistics calculation
- Chronological ordering
- Silence gap detection
"""

import pytest
from processing.multi_transcription_aligner import MultiTranscriptionAligner


class TestMultiTranscriptionAlignerEnhanced:
    """Test suite for MultiTranscriptionAligner.align_enhanced() method"""
    
    def setup_method(self):
        """Set up test data for each test method"""
        # Sample user (mic) transcription data
        self.user_timestamps = [
            {"timestamp": [0.0, 2.5], "text": "Hello, this is the user speaking"},
            {"timestamp": [5.0, 7.2], "text": "I'm asking a question"},
            {"timestamp": [10.5, 12.8], "text": "Thanks for the help"}
        ]
        
        # Sample monitor transcription data
        self.monitor_timestamps = [
            {"timestamp": [2.8, 4.9], "text": "System response here"},
            {"timestamp": [7.5, 9.3], "text": "This is the answer to your question"},
            {"timestamp": [13.0, 15.2], "text": "You're welcome"}
        ]
        
        # Sample session metadata
        self.session_metadata = {
            "timestamp": "2025-11-03_10-30-00",
            "duration_seconds": 15.2
        }
    
    def test_align_enhanced_basic_structure(self):
        """Test that align_enhanced returns the correct basic structure"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        # Verify top-level structure
        assert isinstance(result, dict)
        assert "session_metadata" in result
        assert "conversation" in result
        assert "summary_hints" in result
        
        # Verify session_metadata structure
        session_meta = result["session_metadata"]
        assert session_meta["timestamp"] == "2025-11-03_10-30-00"
        assert session_meta["duration_seconds"] == 15.2
        assert session_meta["total_segments"] == 6
        assert session_meta["channels"] == {"mic": "User", "monitor": "Others"}
        
        # Verify conversation is a list
        assert isinstance(result["conversation"], list)
        assert len(result["conversation"]) == 6
        
        # Verify summary_hints structure
        hints = result["summary_hints"]
        assert "user_talk_time_seconds" in hints
        assert "others_talk_time_seconds" in hints
        assert "silence_gaps" in hints
        assert "avg_segment_length" in hints
        assert "total_segments" in hints
    
    def test_speaker_attribution_correct(self):
        """Test that speaker attribution is correct (User for mic, Others for monitor)"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        # Count speakers by source
        user_segments = [seg for seg in conversation if seg["speaker"] == "User"]
        others_segments = [seg for seg in conversation if seg["speaker"] == "Others"]
        
        # Verify counts match input
        assert len(user_segments) == len(self.user_timestamps)
        assert len(others_segments) == len(self.monitor_timestamps)
        
        # Verify all User segments have source "mic"
        for seg in user_segments:
            assert seg["source"] == "mic"
            
        # Verify all Others segments have source "monitor"  
        for seg in others_segments:
            assert seg["source"] == "monitor"
    
    def test_chronological_ordering(self):
        """Test that conversation segments are ordered chronologically by start_time"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        # Verify chronological ordering
        for i in range(1, len(conversation)):
            assert conversation[i]["start_time"] >= conversation[i-1]["start_time"]
        
        # Verify specific expected order based on test data
        expected_order = [0.0, 2.8, 5.0, 7.5, 10.5, 13.0]
        actual_order = [seg["start_time"] for seg in conversation]
        assert actual_order == expected_order
    
    def test_segment_time_calculations(self):
        """Test that start_time, end_time, and duration are calculated correctly"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        for segment in conversation:
            # Verify all time fields are present
            assert "start_time" in segment
            assert "end_time" in segment
            assert "duration" in segment
            
            # Verify duration calculation is correct
            expected_duration = round(segment["end_time"] - segment["start_time"], 2)
            assert segment["duration"] == expected_duration
            
            # Verify time fields are numeric
            assert isinstance(segment["start_time"], (int, float))
            assert isinstance(segment["end_time"], (int, float))
            assert isinstance(segment["duration"], (int, float))
            
            # Verify logical time relationships
            assert segment["end_time"] > segment["start_time"]
            assert segment["duration"] > 0
    
    def test_summary_hints_calculations(self):
        """Test that summary hints are calculated correctly"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        hints = result["summary_hints"]
        conversation = result["conversation"]
        
        # Calculate expected values
        user_segments = [seg for seg in conversation if seg["speaker"] == "User"]
        others_segments = [seg for seg in conversation if seg["speaker"] == "Others"]
        
        expected_user_time = sum(seg["duration"] for seg in user_segments)
        expected_others_time = sum(seg["duration"] for seg in others_segments)
        expected_total_segments = len(conversation)
        expected_avg_length = round(sum(seg["duration"] for seg in conversation) / len(conversation), 2)
        
        # Verify calculations
        assert hints["user_talk_time_seconds"] == round(expected_user_time, 2)
        assert hints["others_talk_time_seconds"] == round(expected_others_time, 2) 
        assert hints["total_segments"] == expected_total_segments
        assert hints["avg_segment_length"] == expected_avg_length
        
        # Verify silence gaps calculation (>1 second threshold)
        expected_gaps = 0
        for i in range(1, len(conversation)):
            gap = conversation[i]["start_time"] - conversation[i-1]["end_time"]
            if gap > 1.0:
                expected_gaps += 1
        assert hints["silence_gaps"] == expected_gaps
    
    def test_silence_gap_detection(self):
        """Test silence gap detection with various gap sizes"""
        # Create test data with known gaps
        user_timestamps = [
            {"timestamp": [0.0, 2.0], "text": "First segment"},
            {"timestamp": [4.5, 6.0], "text": "After 2.5s gap"}  # 2.5s gap > 1s threshold
        ]
        monitor_timestamps = [
            {"timestamp": [2.5, 3.0], "text": "Short gap"},  # 0.5s gap < 1s threshold
            {"timestamp": [7.0, 8.5], "text": "Another segment"}  # 1.0s gap = threshold
        ]
        
        result = MultiTranscriptionAligner.align_enhanced(
            user_timestamps, 
            monitor_timestamps, 
            self.session_metadata
        )
        
        # Expected gaps: 2.5s gap should be counted, 0.5s should not, 1.0s should not
        # Order: [0.0-2.0], [2.5-3.0], [4.5-6.0], [7.0-8.5]
        # Gaps: 0.5s, 1.5s, 1.0s
        # Only 1.5s gap > 1.0s threshold
        expected_gaps = 1
        assert result["summary_hints"]["silence_gaps"] == expected_gaps
    
    def test_enhanced_format_with_empty_inputs(self):
        """Test align_enhanced handles empty input gracefully"""
        result = MultiTranscriptionAligner.align_enhanced(
            [], [], self.session_metadata
        )
        
        # Should return valid structure even with empty inputs
        assert result["conversation"] == []
        assert result["summary_hints"]["total_segments"] == 0
        assert result["summary_hints"]["user_talk_time_seconds"] == 0
        assert result["summary_hints"]["others_talk_time_seconds"] == 0
        assert result["summary_hints"]["silence_gaps"] == 0
        assert result["summary_hints"]["avg_segment_length"] == 0
    
    def test_enhanced_format_with_single_speaker(self):
        """Test align_enhanced with only one speaker present"""
        # Only user segments
        result_user_only = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, [], self.session_metadata
        )
        
        assert len(result_user_only["conversation"]) == 3
        assert all(seg["speaker"] == "User" for seg in result_user_only["conversation"])
        assert result_user_only["summary_hints"]["others_talk_time_seconds"] == 0
        assert result_user_only["summary_hints"]["user_talk_time_seconds"] > 0
        
        # Only monitor segments
        result_monitor_only = MultiTranscriptionAligner.align_enhanced(
            [], self.monitor_timestamps, self.session_metadata
        )
        
        assert len(result_monitor_only["conversation"]) == 3
        assert all(seg["speaker"] == "Others" for seg in result_monitor_only["conversation"])
        assert result_monitor_only["summary_hints"]["user_talk_time_seconds"] == 0
        assert result_monitor_only["summary_hints"]["others_talk_time_seconds"] > 0
    
    def test_enhanced_format_preserves_text_content(self):
        """Test that text content is preserved correctly in enhanced format"""
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            self.session_metadata
        )
        
        conversation = result["conversation"]
        
        # Collect all text content
        user_texts = [seg["text"] for seg in conversation if seg["speaker"] == "User"]
        others_texts = [seg["text"] for seg in conversation if seg["speaker"] == "Others"]
        
        # Verify all original texts are preserved
        original_user_texts = [seg["text"] for seg in self.user_timestamps]
        original_monitor_texts = [seg["text"] for seg in self.monitor_timestamps]
        
        assert set(user_texts) == set(original_user_texts)
        assert set(others_texts) == set(original_monitor_texts)
    
    def test_enhanced_format_session_metadata_integration(self):
        """Test that session metadata is properly integrated and enhanced"""
        custom_metadata = {
            "timestamp": "2025-11-03_15-45-30",
            "duration_seconds": 120.5,
            "custom_field": "test_value"
        }
        
        result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps, 
            custom_metadata
        )
        
        session_meta = result["session_metadata"]
        
        # Verify original metadata is preserved
        assert session_meta["timestamp"] == "2025-11-03_15-45-30"
        assert session_meta["duration_seconds"] == 120.5
        assert session_meta["custom_field"] == "test_value"
        
        # Verify enhanced metadata is added
        assert session_meta["total_segments"] == 6
        assert session_meta["channels"] == {"mic": "User", "monitor": "Others"}
    
    def test_backward_compatibility_with_legacy_align(self):
        """Test that the legacy align method still works unchanged"""
        # Test legacy align method for backward compatibility
        legacy_result = MultiTranscriptionAligner.align(
            self.user_timestamps, 
            self.monitor_timestamps
        )
        
        # Should return simple list format
        assert isinstance(legacy_result, list)
        assert len(legacy_result) == 6
        
        # Verify chronological ordering in legacy format
        for i in range(1, len(legacy_result)):
            assert legacy_result[i]["timestamp"][0] >= legacy_result[i-1]["timestamp"][0]
        
        # Verify structure is legacy format (not enhanced)
        for segment in legacy_result:
            assert "timestamp" in segment
            assert "text" in segment
            # Enhanced fields should not be present
            assert "speaker" not in segment
            assert "source" not in segment
            assert "start_time" not in segment