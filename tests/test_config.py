"""
Tests for Config class enhanced functionality.

Tests all completed features from the enhanced transcription format:
- generate_session_metadata() method
- enhanced_transcription_path property
- session timing tracking
- dual output system support
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from config import Config


class TestConfigEnhanced:
    """Test suite for Config class enhanced functionality"""
    
    def setup_method(self):
        """Set up test environment for each test method"""
        # Use temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = Config(base_output_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_enhanced_transcription_path_property(self):
        """Test that enhanced_transcription_path property returns correct path"""
        expected_path = self.test_config.session_dir / "enhanced_transcription.json"
        assert self.test_config.enhanced_transcription_path == expected_path
        assert isinstance(self.test_config.enhanced_transcription_path, Path)
        
        # Verify path structure
        assert self.test_config.enhanced_transcription_path.name == "enhanced_transcription.json"
        assert self.test_config.enhanced_transcription_path.parent == self.test_config.session_dir
    
    def test_session_timing_tracking(self):
        """Test that session start time is tracked correctly"""
        # Verify session_start_time is set during initialization
        assert hasattr(self.test_config, 'session_start_time')
        assert isinstance(self.test_config.session_start_time, datetime)
        
        # Should be very recent (within last few seconds)
        time_diff = datetime.now() - self.test_config.session_start_time
        assert time_diff.total_seconds() < 5  # Should be very recent
    
    def test_generate_session_metadata_basic(self):
        """Test basic session metadata generation"""
        metadata = self.test_config.generate_session_metadata()
        
        # Verify structure
        assert isinstance(metadata, dict)
        assert "timestamp" in metadata
        assert "duration_seconds" in metadata
        
        # Verify timestamp format
        assert metadata["timestamp"] == self.test_config.timestamp
        assert isinstance(metadata["duration_seconds"], float)
        assert metadata["duration_seconds"] >= 0
    
    def test_generate_session_metadata_duration_calculation(self):
        """Test that session duration is calculated correctly"""
        # Mock session start time to test duration calculation
        mock_start_time = datetime.now() - timedelta(seconds=60)  # 60 seconds ago
        self.test_config.session_start_time = mock_start_time
        
        with patch('config.datetime') as mock_datetime:
            mock_end_time = mock_start_time + timedelta(seconds=60)
            mock_datetime.now.return_value = mock_end_time
            
            metadata = self.test_config.generate_session_metadata()
            
            # Should be approximately 60 seconds
            assert abs(metadata["duration_seconds"] - 60.0) < 1.0
    
    def test_generate_session_metadata_precision(self):
        """Test that duration is rounded to 2 decimal places"""
        # Mock session start time for precise duration control
        mock_start_time = datetime.now() - timedelta(seconds=12.345678)
        self.test_config.session_start_time = mock_start_time
        
        with patch('config.datetime') as mock_datetime:
            mock_end_time = mock_start_time + timedelta(seconds=12.345678)
            mock_datetime.now.return_value = mock_end_time
            
            metadata = self.test_config.generate_session_metadata()
            
            # Verify rounding to 2 decimal places
            assert metadata["duration_seconds"] == 12.35
    
    def test_save_enhanced_transcription_method(self):
        """Test save_enhanced_transcription method functionality"""
        test_data = {
            "session_metadata": {
                "timestamp": "2025-11-03_10-30-00",
                "duration_seconds": 15.2,
                "total_segments": 3,
                "channels": {"mic": "User", "monitor": "Others"}
            },
            "conversation": [
                {
                    "speaker": "User",
                    "start_time": 0.0,
                    "end_time": 2.5,
                    "duration": 2.5,
                    "text": "Hello",
                    "source": "mic"
                }
            ],
            "summary_hints": {
                "user_talk_time_seconds": 2.5,
                "others_talk_time_seconds": 0.0,
                "silence_gaps": 0,
                "avg_segment_length": 2.5,
                "total_segments": 1
            }
        }
        
        # Save enhanced transcription
        saved_path = self.test_config.save_enhanced_transcription(test_data)
        
        # Verify file was saved correctly
        assert saved_path == self.test_config.enhanced_transcription_path
        assert saved_path.exists()
        
        # Verify content is correct
        with open(saved_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data
    
    def test_save_enhanced_transcription_error_handling(self):
        """Test error handling in save_enhanced_transcription"""
        # Create a config and then make the enhanced transcription path read-only
        config = Config(base_output_path=self.temp_dir)
        
        # Make the enhanced transcription file read-only by creating it first
        config.enhanced_transcription_path.write_text('{"readonly": true}')
        config.enhanced_transcription_path.chmod(0o444)  # Read-only
        
        test_data = {"test": "data"}
        
        # Should raise exception for read-only file
        try:
            config.save_enhanced_transcription(test_data)
            assert False, "Expected exception was not raised"
        except Exception as e:
            # Should be a permission or IO error
            assert isinstance(e, (OSError, IOError, PermissionError))
        finally:
            # Clean up - restore write permissions
            try:
                config.enhanced_transcription_path.chmod(0o644)
            except:
                pass
    
    def test_dual_output_system_paths(self):
        """Test that both legacy and enhanced transcription paths are available"""
        # Verify both paths exist and are different
        assert self.test_config.final_transcription_path != self.test_config.enhanced_transcription_path
        
        # Verify path names
        assert self.test_config.final_transcription_path.name == "transcription.json"
        assert self.test_config.enhanced_transcription_path.name == "enhanced_transcription.json"
        
        # Verify they're in the same directory
        assert self.test_config.final_transcription_path.parent == self.test_config.enhanced_transcription_path.parent
        assert self.test_config.final_transcription_path.parent == self.test_config.session_dir
    
    def test_directory_structure_creation(self):
        """Test that enhanced transcription support doesn't break directory creation"""
        # Directories should be created during initialization
        assert self.test_config.session_dir.exists()
        assert self.test_config.audio_dir.exists()
        assert self.test_config.transcriptions_dir.exists()
        
        # Verify directory structure
        assert self.test_config.audio_dir == self.test_config.session_dir / "audio"
        assert self.test_config.transcriptions_dir == self.test_config.session_dir / "transcriptions"
    
    def test_timestamp_format_consistency(self):
        """Test that timestamp format is consistent across methods"""
        # Timestamp should be in YYYY-MM-DD_HH-MM-SS format
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$'
        import re
        
        assert re.match(timestamp_pattern, self.test_config.timestamp)
        
        # Should match in generated metadata
        metadata = self.test_config.generate_session_metadata()
        assert metadata["timestamp"] == self.test_config.timestamp
    
    def test_session_metadata_immutability(self):
        """Test that session metadata generation is consistent over time"""
        # Generate metadata at different times
        metadata1 = self.test_config.generate_session_metadata()
        
        # Small delay
        import time
        time.sleep(0.1)
        
        metadata2 = self.test_config.generate_session_metadata()
        
        # Timestamp should be the same (from initialization)
        assert metadata1["timestamp"] == metadata2["timestamp"]
        
        # Duration should increase
        assert metadata2["duration_seconds"] >= metadata1["duration_seconds"]
    
    def test_config_initialization_with_enhanced_features(self):
        """Test that Config initialization properly sets up enhanced features"""
        custom_config = Config(base_output_path=self.temp_dir)
        
        # Verify all enhanced properties are available
        assert hasattr(custom_config, 'enhanced_transcription_path')
        assert hasattr(custom_config, 'session_start_time')
        
        # Verify methods are available
        assert callable(getattr(custom_config, 'generate_session_metadata'))
        assert callable(getattr(custom_config, 'save_enhanced_transcription'))
    
    def test_backward_compatibility_with_legacy_methods(self):
        """Test that legacy methods still work with enhanced Config"""
        # Legacy transcription saving should still work
        test_data = [{"timestamp": [0.0, 2.5], "text": "test"}]
        
        # Save using legacy method
        saved_path = self.test_config.save_final_transcription(test_data)
        
        # Verify legacy path is used
        assert saved_path == self.test_config.final_transcription_path
        assert saved_path.exists()
        
        # Verify content
        with open(saved_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
    
    def test_enhanced_transcription_path_uniqueness(self):
        """Test that each Config instance has unique enhanced transcription path"""
        # Create multiple configs
        config1 = Config(base_output_path=self.temp_dir)
        
        # Small delay to ensure different timestamp
        import time
        time.sleep(1)
        
        config2 = Config(base_output_path=self.temp_dir)
        
        # Should have different paths due to different timestamps
        assert config1.enhanced_transcription_path != config2.enhanced_transcription_path
        assert config1.session_dir != config2.session_dir