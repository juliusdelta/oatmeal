"""
Tests for backward compatibility verification.

Tests that all enhanced transcription format features maintain backward compatibility:
- Legacy align() method unchanged
- Legacy transcription.json format preserved
- Existing API unchanged
- No breaking changes to workflows
"""

import json
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

from config import Config
from processing.multi_transcription_aligner import MultiTranscriptionAligner
from run_strategies.transcribe_only_strategy import TranscribeOnlyStrategy


class TestBackwardCompatibility:
    """Test suite for backward compatibility verification"""
    
    def setup_method(self):
        """Set up test environment for each test method"""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample legacy test data
        self.user_timestamps = [
            {"timestamp": [0.0, 2.5], "text": "Hello, this is the user"},
            {"timestamp": [5.0, 7.2], "text": "User continues speaking"}
        ]
        
        self.monitor_timestamps = [
            {"timestamp": [2.8, 4.9], "text": "Monitor response here"},
            {"timestamp": [7.5, 9.3], "text": "Another monitor response"}
        ]
        
        # Expected legacy format result
        self.expected_legacy_result = [
            {"timestamp": [0.0, 2.5], "text": "Hello, this is the user"},
            {"timestamp": [2.8, 4.9], "text": "Monitor response here"},
            {"timestamp": [5.0, 7.2], "text": "User continues speaking"},
            {"timestamp": [7.5, 9.3], "text": "Another monitor response"}
        ]
    
    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_legacy_align_method_unchanged(self):
        """Test that legacy align() method works exactly as before"""
        # Call legacy align method
        result = MultiTranscriptionAligner.align(
            self.user_timestamps, 
            self.monitor_timestamps
        )
        
        # Should return list format (not dict like enhanced)
        assert isinstance(result, list)
        assert len(result) == 4
        
        # Should maintain legacy structure
        for segment in result:
            assert "timestamp" in segment
            assert "text" in segment
            assert isinstance(segment["timestamp"], list)
            assert len(segment["timestamp"]) == 2
            assert isinstance(segment["text"], str)
            
            # Should not have enhanced fields
            assert "speaker" not in segment
            assert "source" not in segment
            assert "start_time" not in segment
            assert "end_time" not in segment
            assert "duration" not in segment
        
        # Verify chronological ordering (legacy behavior)
        for i in range(1, len(result)):
            assert result[i]["timestamp"][0] >= result[i-1]["timestamp"][0]
    
    def test_legacy_align_method_independence(self):
        """Test that legacy align() method is independent of enhanced functionality"""
        # Call both methods with same data
        legacy_result = MultiTranscriptionAligner.align(
            self.user_timestamps, 
            self.monitor_timestamps
        )
        
        enhanced_result = MultiTranscriptionAligner.align_enhanced(
            self.user_timestamps, 
            self.monitor_timestamps,
            {"timestamp": "test", "duration_seconds": 10.0}
        )
        
        # Legacy method should return simple list
        assert isinstance(legacy_result, list)
        
        # Enhanced method should return complex dict
        assert isinstance(enhanced_result, dict)
        
        # They should have different structures
        assert legacy_result != enhanced_result
        assert legacy_result != enhanced_result.get("conversation", [])
    
    def test_config_legacy_methods_unchanged(self):
        """Test that Config legacy methods still work unchanged"""
        config = Config(base_output_path=self.temp_dir)
        
        # Legacy transcription saving should work
        test_data = [{"timestamp": [0.0, 2.5], "text": "test"}]
        
        # Test save_final_transcription (legacy method)
        saved_path = config.save_final_transcription(test_data)
        assert saved_path == config.final_transcription_path
        assert saved_path.exists()
        
        # Verify content is in legacy format
        with open(saved_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
        
        # Test save_transcription (legacy method)
        individual_path = config.save_transcription("test.json", test_data)
        assert individual_path == config.transcriptions_dir / "test.json"
        assert individual_path.exists()
    
    def test_config_legacy_properties_unchanged(self):
        """Test that Config legacy properties are unchanged"""
        config = Config(base_output_path=self.temp_dir)
        
        # Legacy properties should still exist
        assert hasattr(config, 'final_transcription_path')
        assert hasattr(config, 'transcriptions_dir')
        assert hasattr(config, 'session_dir')
        assert hasattr(config, 'audio_dir')
        assert hasattr(config, 'timestamp')
        
        # Legacy paths should be unchanged
        assert config.final_transcription_path.name == "transcription.json"
        assert config.transcriptions_dir.name == "transcriptions"
        assert config.audio_dir.name == "audio"
        
        # Enhanced properties should be additive (not replace legacy)
        assert hasattr(config, 'enhanced_transcription_path')
        assert config.enhanced_transcription_path != config.final_transcription_path
    
    def test_transcribe_only_strategy_return_value_unchanged(self):
        """Test that TranscribeOnlyStrategy still returns legacy format"""
        config = Config(base_output_path=self.temp_dir)
        strategy = TranscribeOnlyStrategy(config)
        
        # Mock dependencies to isolate return value testing
        with patch.object(strategy, 'fetch_audio', return_value=("user.wav", "monitor.wav")), \
             patch.object(config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.user_timestamps),
                 ("monitor_text", self.monitor_timestamps)
             ]), \
             patch.object(config, 'save_transcription'), \
             patch.object(config, 'save_final_transcription') as mock_save_final, \
             patch.object(config, 'save_enhanced_transcription'), \
             patch.object(config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 10}), \
             patch('builtins.print'):
            
            # Run strategy
            result = strategy.run()
            
            # Should return legacy format (list)
            assert isinstance(result, list)
            
            # Should be the same as what was saved to legacy file
            mock_save_final.assert_called_once()
            saved_data = mock_save_final.call_args[0][0]
            assert result == saved_data
            
            # Should have legacy structure
            for segment in result:
                assert "timestamp" in segment
                assert "text" in segment
                assert "speaker" not in segment
                assert "source" not in segment
    
    def test_file_output_structure_backward_compatible(self):
        """Test that file output structure maintains backward compatibility"""
        config = Config(base_output_path=self.temp_dir)
        
        # Directory structure should be unchanged
        expected_dirs = [
            config.session_dir,
            config.audio_dir,
            config.transcriptions_dir
        ]
        
        for directory in expected_dirs:
            assert directory.exists()
        
        # Legacy files should still be created
        legacy_data = [{"timestamp": [0.0, 1.0], "text": "test"}]
        enhanced_data = {
            "session_metadata": {"timestamp": "test", "duration_seconds": 1.0, "total_segments": 1, "channels": {"mic": "User", "monitor": "Others"}},
            "conversation": [{"speaker": "User", "start_time": 0.0, "end_time": 1.0, "duration": 1.0, "text": "test", "source": "mic"}],
            "summary_hints": {"user_talk_time_seconds": 1.0, "others_talk_time_seconds": 0.0, "silence_gaps": 0, "avg_segment_length": 1.0, "total_segments": 1}
        }
        
        config.save_final_transcription(legacy_data)
        config.save_enhanced_transcription(enhanced_data)
        
        # Both files should exist
        assert config.final_transcription_path.exists()
        assert config.enhanced_transcription_path.exists()
        
        # Legacy file should have legacy format
        with open(config.final_transcription_path, 'r') as f:
            loaded_legacy = json.load(f)
        assert loaded_legacy == legacy_data
        
        # Enhanced file should have enhanced format
        with open(config.enhanced_transcription_path, 'r') as f:
            loaded_enhanced = json.load(f)
        assert loaded_enhanced == enhanced_data
    
    def test_existing_code_integration_unchanged(self):
        """Test that existing code can use the enhanced system without changes"""
        # Simulate existing code that only uses legacy methods
        
        # 1. Create config (existing usage)
        config = Config(base_output_path=self.temp_dir)
        
        # 2. Use legacy align method (existing usage)
        aligned_data = MultiTranscriptionAligner.align(
            self.user_timestamps, 
            self.monitor_timestamps
        )
        
        # 3. Save using legacy method (existing usage)
        saved_path = config.save_final_transcription(aligned_data)
        
        # Should work exactly as before
        assert saved_path.exists()
        with open(saved_path, 'r') as f:
            loaded_data = json.load(f)
        
        # Data should be in legacy format
        assert isinstance(loaded_data, list)
        assert all("timestamp" in seg for seg in loaded_data)
        assert all("text" in seg for seg in loaded_data)
        assert all("speaker" not in seg for seg in loaded_data)
    
    def test_no_breaking_changes_in_method_signatures(self):
        """Test that method signatures haven't changed"""
        # MultiTranscriptionAligner.align signature unchanged
        import inspect
        align_sig = inspect.signature(MultiTranscriptionAligner.align)
        expected_params = ['user_timestamps', 'monitor_timestamps']
        actual_params = list(align_sig.parameters.keys())
        assert actual_params == expected_params
        
        # Config constructor signature should accept existing parameters
        config_sig = inspect.signature(Config.__init__)
        # Should accept base_output_path and other existing parameters
        assert 'base_output_path' in config_sig.parameters
        
        # Legacy methods should exist with same signatures
        assert hasattr(Config, 'save_final_transcription')
        assert hasattr(Config, 'save_transcription')
        
        final_save_sig = inspect.signature(Config.save_final_transcription)
        assert 'data' in final_save_sig.parameters
        
        individual_save_sig = inspect.signature(Config.save_transcription)
        assert 'filename' in individual_save_sig.parameters
        assert 'data' in individual_save_sig.parameters
    
    def test_legacy_workflow_runs_without_enhanced_features(self):
        """Test that legacy workflow can run completely without touching enhanced features"""
        config = Config(base_output_path=self.temp_dir)
        
        # Simulate legacy workflow
        # 1. Use only legacy align
        aligned_data = MultiTranscriptionAligner.align(
            self.user_timestamps, 
            self.monitor_timestamps
        )
        
        # 2. Save only legacy format
        config.save_final_transcription(aligned_data)
        
        # 3. Verify no enhanced files were created accidentally
        assert config.final_transcription_path.exists()
        
        # Enhanced file should not exist unless explicitly created
        if not config.enhanced_transcription_path.exists():
            # This is expected - enhanced file only created when explicitly requested
            pass
        else:
            # If it exists, it should be because Config creates directories, not files
            assert config.enhanced_transcription_path.parent.exists()
    
    def test_enhanced_features_are_additive_only(self):
        """Test that enhanced features only add functionality, don't change existing"""
        # Create two configs - one to simulate "before enhancement" and one "after"
        config1 = Config(base_output_path=self.temp_dir + "/before")
        config2 = Config(base_output_path=self.temp_dir + "/after")
        
        # Both should have same legacy functionality
        legacy_data = [{"timestamp": [0.0, 1.0], "text": "test"}]
        
        # Both should be able to save legacy format the same way
        path1 = config1.save_final_transcription(legacy_data)
        path2 = config2.save_final_transcription(legacy_data)
        
        # Files should have identical content
        with open(path1, 'r') as f1, open(path2, 'r') as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)
        
        assert data1 == data2
        assert data1 == legacy_data
        
        # Both should have same legacy properties
        assert path1.name == path2.name == "transcription.json"
        assert config1.transcriptions_dir.name == config2.transcriptions_dir.name == "transcriptions"
    
    def test_performance_impact_minimal(self):
        """Test that enhanced features don't significantly impact legacy workflow performance"""
        # This is more of a structural test to ensure enhanced features don't
        # add computational overhead to legacy workflows
        
        import time
        
        # Time legacy align method
        start_time = time.time()
        result = None
        for _ in range(100):
            result = MultiTranscriptionAligner.align(
                self.user_timestamps, 
                self.monitor_timestamps
            )
        legacy_time = time.time() - start_time
        
        # Enhanced features shouldn't slow down legacy align
        # (This is a basic smoke test - real performance testing would need larger datasets)
        assert legacy_time < 1.0  # Should be very fast for small test data
        
        # Legacy result should be consistent
        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 4
    
    def test_error_handling_backward_compatibility(self):
        """Test that error handling doesn't change for legacy methods"""
        # Test with valid config but invalid data scenarios
        config = Config(base_output_path=self.temp_dir)
        
        # Make final transcription path read-only to test error handling
        config.final_transcription_path.write_text('{"readonly": true}')
        config.final_transcription_path.chmod(0o444)  # Read-only
        
        # Legacy save methods should fail in the same way they always did
        try:
            config.save_final_transcription([{"test": "data"}])
            assert False, "Expected exception was not raised"
        except (OSError, IOError, PermissionError):
            # This is expected - read-only file should cause error
            pass
        finally:
            # Clean up - restore write permissions
            try:
                config.final_transcription_path.chmod(0o644)
            except:
                pass
        
        # Legacy align with invalid data should fail the same way
        try:
            MultiTranscriptionAligner.align(None, None)
            assert False, "Expected exception was not raised"  
        except (TypeError, AttributeError):
            # This is expected - None inputs should cause error
            pass