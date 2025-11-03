"""
Tests for TranscribeOnlyStrategy enhanced functionality.

Tests all completed features from the enhanced transcription format:
- Dual output system (legacy + enhanced formats)
- Enhanced workflow integration
- Summary statistics display
- Backward compatibility
"""

import json
import tempfile
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

from config import Config
from run_strategies.transcribe_only_strategy import TranscribeOnlyStrategy


class TestTranscribeOnlyStrategyEnhanced:
    """Test suite for TranscribeOnlyStrategy enhanced functionality"""
    
    def setup_method(self):
        """Set up test environment for each test method"""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock config
        self.mock_config = Config(base_output_path=self.temp_dir)
        
        # Create strategy instance
        self.strategy = TranscribeOnlyStrategy(self.mock_config)
        
        # Mock transcription data
        self.mock_user_transcription = [
            {"timestamp": [0.0, 2.5], "text": "Hello, this is the user"},
            {"timestamp": [5.0, 7.2], "text": "I have a question"}
        ]
        
        self.mock_monitor_transcription = [
            {"timestamp": [2.8, 4.9], "text": "Response from system"},
            {"timestamp": [7.5, 9.3], "text": "Here is the answer"}
        ]
        
        # Mock audio files
        self.mock_user_audio = "/path/to/user.wav"
        self.mock_monitor_audio = "/path/to/monitor.wav"
    
    def teardown_method(self):
        """Clean up after each test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner')
    def test_dual_output_generation(self, mock_aligner):
        """Test that both legacy and enhanced formats are generated"""
        # Mock the alignment methods
        mock_legacy_result = [
            {"timestamp": [0.0, 2.5], "text": "Hello, this is the user"},
            {"timestamp": [2.8, 4.9], "text": "Response from system"}
        ]
        
        mock_enhanced_result = {
            "session_metadata": {
                "timestamp": "2025-11-03_10-30-00",
                "duration_seconds": 15.2,
                "total_segments": 2,
                "channels": {"mic": "User", "monitor": "Others"}
            },
            "conversation": [
                {
                    "speaker": "User",
                    "start_time": 0.0,
                    "end_time": 2.5,
                    "duration": 2.5,
                    "text": "Hello, this is the user",
                    "source": "mic"
                }
            ],
            "summary_hints": {
                "user_talk_time_seconds": 2.5,
                "others_talk_time_seconds": 2.1,
                "silence_gaps": 0,
                "avg_segment_length": 2.3,
                "total_segments": 2
            }
        }
        
        mock_aligner.align.return_value = mock_legacy_result
        mock_aligner.align_enhanced.return_value = mock_enhanced_result
        
        # Mock other dependencies
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]), \
             patch.object(self.mock_config, 'save_transcription'), \
             patch.object(self.mock_config, 'save_final_transcription'), \
             patch.object(self.mock_config, 'save_enhanced_transcription'), \
             patch.object(self.mock_config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 15.2}), \
             patch('builtins.print'):  # Mock print to suppress output
            
            # Run the strategy
            result = self.strategy.run()
            
            # Verify both alignment methods were called
            mock_aligner.align.assert_called_once_with(
                self.mock_user_transcription, self.mock_monitor_transcription
            )
            mock_aligner.align_enhanced.assert_called_once_with(
                self.mock_user_transcription, self.mock_monitor_transcription, {"timestamp": "test", "duration_seconds": 15.2}
            )
            
            # Verify both save methods were called
            self.mock_config.save_final_transcription.assert_called_once_with(mock_legacy_result)
            self.mock_config.save_enhanced_transcription.assert_called_once_with(mock_enhanced_result)
    
    def test_summary_statistics_display(self):
        """Test that summary statistics are displayed correctly"""
        # Mock dependencies
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]), \
             patch.object(self.mock_config, 'save_transcription'), \
             patch.object(self.mock_config, 'save_final_transcription'), \
             patch.object(self.mock_config, 'save_enhanced_transcription'), \
             patch.object(self.mock_config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 15.2}), \
             patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner') as mock_aligner, \
             patch('builtins.print') as mock_print:
            
            # Mock enhanced alignment result with specific stats
            mock_enhanced_result = {
                "session_metadata": {"timestamp": "test", "duration_seconds": 15.2},
                "conversation": [],
                "summary_hints": {
                    "total_segments": 4,
                    "user_talk_time_seconds": 4.7,
                    "others_talk_time_seconds": 4.2,
                    "avg_segment_length": 2.2,
                    "silence_gaps": 2
                }
            }
            
            mock_aligner.align.return_value = []
            mock_aligner.align_enhanced.return_value = mock_enhanced_result
            
            # Run the strategy
            self.strategy.run()
            
            # Verify summary statistics were printed
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            
            assert any("Session Summary:" in call for call in print_calls)
            assert any("Total segments: 4" in call for call in print_calls)
            assert any("User talk time: 4.7s" in call for call in print_calls)
            assert any("Others talk time: 4.2s" in call for call in print_calls)
            assert any("Average segment length: 2.2s" in call for call in print_calls)
            assert any("Silence gaps detected: 2" in call for call in print_calls)
    
    def test_enhanced_workflow_integration(self):
        """Test that enhanced workflow is properly integrated with existing workflow"""
        # Mock dependencies
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]), \
             patch.object(self.mock_config, 'save_transcription') as mock_save_individual, \
             patch.object(self.mock_config, 'save_final_transcription') as mock_save_final, \
             patch.object(self.mock_config, 'save_enhanced_transcription') as mock_save_enhanced, \
             patch.object(self.mock_config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 15.2}) as mock_metadata, \
             patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner') as mock_aligner, \
             patch('builtins.print'):
            
            mock_aligner.align.return_value = []
            mock_aligner.align_enhanced.return_value = {"summary_hints": {"total_segments": 0, "user_talk_time_seconds": 0, "others_talk_time_seconds": 0, "avg_segment_length": 0, "silence_gaps": 0}}
            
            # Run the strategy
            self.strategy.run()
            
            # Verify workflow order
            # 1. Individual transcriptions saved
            assert mock_save_individual.call_count == 2
            mock_save_individual.assert_any_call("mic.json", self.mock_user_transcription)
            mock_save_individual.assert_any_call("monitor.json", self.mock_monitor_transcription)
            
            # 2. Session metadata generated
            mock_metadata.assert_called_once()
            
            # 3. Both alignment methods called
            mock_aligner.align.assert_called_once()
            mock_aligner.align_enhanced.assert_called_once()
            
            # 4. Both formats saved
            mock_save_final.assert_called_once()
            mock_save_enhanced.assert_called_once()
    
    def test_backward_compatibility_return_value(self):
        """Test that the strategy still returns the legacy format for backward compatibility"""
        mock_legacy_result = [
            {"timestamp": [0.0, 2.5], "text": "Hello, this is the user"}
        ]
        
        # Mock dependencies
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]), \
             patch.object(self.mock_config, 'save_transcription'), \
             patch.object(self.mock_config, 'save_final_transcription'), \
             patch.object(self.mock_config, 'save_enhanced_transcription'), \
             patch.object(self.mock_config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 15.2}), \
             patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner') as mock_aligner, \
             patch('builtins.print'):
            
            mock_aligner.align.return_value = mock_legacy_result
            mock_aligner.align_enhanced.return_value = {"summary_hints": {"total_segments": 0, "user_talk_time_seconds": 0, "others_talk_time_seconds": 0, "avg_segment_length": 0, "silence_gaps": 0}}
            
            # Run the strategy
            result = self.strategy.run()
            
            # Should return the legacy format for backward compatibility
            assert result == mock_legacy_result
    
    def test_error_handling_enhanced_transcription(self):
        """Test error handling when enhanced transcription fails"""
        # Mock dependencies with enhanced transcription failure
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]), \
             patch.object(self.mock_config, 'save_transcription'), \
             patch.object(self.mock_config, 'save_final_transcription'), \
             patch.object(self.mock_config, 'save_enhanced_transcription', side_effect=Exception("Enhanced save failed")), \
             patch.object(self.mock_config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 15.2}), \
             patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner') as mock_aligner, \
             patch('builtins.print'):
            
            mock_aligner.align.return_value = []
            mock_aligner.align_enhanced.return_value = {"summary_hints": {"total_segments": 0, "user_talk_time_seconds": 0, "others_talk_time_seconds": 0, "avg_segment_length": 0, "silence_gaps": 0}}
            
            # Should raise exception
            try:
                self.strategy.run()
                assert False, "Expected exception was not raised"
            except Exception as e:
                assert "Enhanced save failed" in str(e)
    
    def test_individual_transcription_saving(self):
        """Test that individual transcriptions are still saved correctly"""
        # Mock dependencies
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]) as mock_transcribe, \
             patch.object(self.mock_config, 'save_transcription') as mock_save_individual, \
             patch.object(self.mock_config, 'save_final_transcription'), \
             patch.object(self.mock_config, 'save_enhanced_transcription'), \
             patch.object(self.mock_config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 15.2}), \
             patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner') as mock_aligner, \
             patch('builtins.print'):
            
            mock_aligner.align.return_value = []
            mock_aligner.align_enhanced.return_value = {"summary_hints": {"total_segments": 0, "user_talk_time_seconds": 0, "others_talk_time_seconds": 0, "avg_segment_length": 0, "silence_gaps": 0}}
            
            # Run the strategy
            self.strategy.run()
            
            # Verify transcription was called for both channels
            assert mock_transcribe.call_count == 2
            mock_transcribe.assert_any_call(self.mock_user_audio)
            mock_transcribe.assert_any_call(self.mock_monitor_audio)
            
            # Verify individual transcriptions were saved
            assert mock_save_individual.call_count == 2
            mock_save_individual.assert_any_call("mic.json", self.mock_user_transcription)
            mock_save_individual.assert_any_call("monitor.json", self.mock_monitor_transcription)
    
    def test_session_metadata_generation_timing(self):
        """Test that session metadata is generated at the correct time in workflow"""
        call_order = []
        
        def track_calls(method_name):
            def wrapper(*args, **kwargs):
                call_order.append(method_name)
                if method_name == 'generate_session_metadata':
                    return {"timestamp": "test", "duration_seconds": 15.2}
                elif method_name == 'align_enhanced':
                    return {"summary_hints": {"total_segments": 0, "user_talk_time_seconds": 0, "others_talk_time_seconds": 0, "avg_segment_length": 0, "silence_gaps": 0}}
                return []
            return wrapper
        
        # Mock dependencies with call tracking
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]), \
             patch.object(self.mock_config, 'save_transcription'), \
             patch.object(self.mock_config, 'save_final_transcription'), \
             patch.object(self.mock_config, 'save_enhanced_transcription'), \
             patch.object(self.mock_config, 'generate_session_metadata', side_effect=track_calls('generate_session_metadata')), \
             patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner') as mock_aligner, \
             patch('builtins.print'):
            
            mock_aligner.align.side_effect = track_calls('align')
            mock_aligner.align_enhanced.side_effect = track_calls('align_enhanced')
            
            # Run the strategy
            self.strategy.run()
            
            # Verify metadata generation happens before enhanced alignment
            assert 'generate_session_metadata' in call_order
            assert 'align_enhanced' in call_order
            metadata_index = call_order.index('generate_session_metadata')
            enhanced_index = call_order.index('align_enhanced')
            assert metadata_index < enhanced_index
    
    def test_enhanced_workflow_no_breaking_changes(self):
        """Test that enhanced workflow doesn't break existing functionality"""
        # This test verifies that all the original functionality still works
        
        # Mock dependencies exactly as they would be in original workflow
        with patch.object(self.strategy, 'fetch_audio', return_value=(self.mock_user_audio, self.mock_monitor_audio)), \
             patch.object(self.mock_config.transcriber, 'transcribe', side_effect=[
                 ("user_text", self.mock_user_transcription),
                 ("monitor_text", self.mock_monitor_transcription)
             ]), \
             patch.object(self.mock_config, 'save_transcription') as mock_save_individual, \
             patch.object(self.mock_config, 'save_final_transcription') as mock_save_final, \
             patch.object(self.mock_config, 'save_enhanced_transcription'), \
             patch.object(self.mock_config, 'generate_session_metadata', return_value={"timestamp": "test", "duration_seconds": 15.2}), \
             patch('run_strategies.transcribe_only_strategy.MultiTranscriptionAligner') as mock_aligner, \
             patch('builtins.print'):
            
            expected_legacy_result = [
                {"timestamp": [0.0, 2.5], "text": "Hello, this is the user"},
                {"timestamp": [2.8, 4.9], "text": "Response from system"}
            ]
            
            mock_aligner.align.return_value = expected_legacy_result
            mock_aligner.align_enhanced.return_value = {"summary_hints": {"total_segments": 2, "user_talk_time_seconds": 2.5, "others_talk_time_seconds": 2.1, "avg_segment_length": 2.3, "silence_gaps": 0}}
            
            # Run the strategy
            result = self.strategy.run()
            
            # Verify original functionality is unchanged
            # 1. Audio capture still works
            # 2. Individual transcriptions still saved
            assert mock_save_individual.call_count == 2
            
            # 3. Legacy alignment still works
            mock_aligner.align.assert_called_once_with(
                self.mock_user_transcription, self.mock_monitor_transcription
            )
            
            # 4. Final transcription still saved
            mock_save_final.assert_called_once_with(expected_legacy_result)
            
            # 5. Return value is still the legacy format
            assert result == expected_legacy_result