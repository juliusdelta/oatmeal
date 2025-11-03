class MultiTranscriptionAligner:
    @staticmethod
    def align(user_timestamps, monitor_timestamps):
        """
        Aligns and merges two JSON arrays of timestamped segments into a single ordered list.

        Args:
            user_timestamps (list): List of dicts with structure:
                [
                    {"timestamp": [start1, end1], "text": "user text 1"},
                    {"timestamp": [start2, end2], "text": "user text 2"},
                    ...
                ]
            monitor_timestamps (list): List of dicts with structure:
                [
                    {"timestamp": [start1, end1], "text": "monitor text 1"},
                    {"timestamp": [start2, end2], "text": "monitor text 2"},
                    ...
                ]
        Returns:
            list: Merged list ordered by start timestamp.
        """
        merged = []
        i = 0
        j = 0
        while i < len(user_timestamps) and j < len(monitor_timestamps):
            if user_timestamps[i]["timestamp"][0] <= monitor_timestamps[j]["timestamp"][0]:
                merged.append(user_timestamps[i])
                i += 1
            else:
                merged.append(monitor_timestamps[j])
                j += 1
        while i < len(user_timestamps):
            merged.append(user_timestamps[i])
            i += 1
        while j < len(monitor_timestamps):
            merged.append(monitor_timestamps[j])
            j += 1
        return merged

    @staticmethod
    def align_enhanced(user_timestamps, monitor_timestamps, session_metadata):
        """
        Enhanced alignment with speaker attribution and metadata.
        
        Args:
            user_timestamps (list): List of dicts with mic transcription segments
            monitor_timestamps (list): List of dicts with monitor transcription segments
            session_metadata (dict): Session metadata including timestamp and duration
            
        Returns:
            dict: Complete enhanced format with speaker attribution and metadata
        """
        conversation = []
        
        # Convert user (mic) segments to enhanced format
        for segment in user_timestamps:
            start_time = segment["timestamp"][0]
            end_time = segment["timestamp"][1]
            conversation.append({
                "speaker": "User",
                "start_time": start_time,
                "end_time": end_time,
                "duration": round(end_time - start_time, 2),
                "text": segment["text"],
                "source": "mic"
            })
        
        # Convert monitor segments to enhanced format
        for segment in monitor_timestamps:
            start_time = segment["timestamp"][0]
            end_time = segment["timestamp"][1]
            conversation.append({
                "speaker": "Others",
                "start_time": start_time,
                "end_time": end_time,
                "duration": round(end_time - start_time, 2),
                "text": segment["text"],
                "source": "monitor"
            })
        
        # Sort by start time
        conversation.sort(key=lambda x: x["start_time"])
        
        # Calculate summary hints
        user_talk_time = sum(seg["duration"] for seg in conversation if seg["speaker"] == "User")
        others_talk_time = sum(seg["duration"] for seg in conversation if seg["speaker"] == "Others")
        total_segments = len(conversation)
        avg_segment_length = round(sum(seg["duration"] for seg in conversation) / total_segments, 2) if total_segments > 0 else 0
        
        # Calculate silence gaps (simplified - count gaps > 1 second between segments)
        silence_gaps = 0
        for i in range(1, len(conversation)):
            gap = conversation[i]["start_time"] - conversation[i-1]["end_time"]
            if gap > 1.0:  # 1 second threshold
                silence_gaps += 1
        
        # Build the complete enhanced format
        enhanced_format = {
            "session_metadata": {
                **session_metadata,
                "total_segments": total_segments,
                "channels": {
                    "mic": "User",
                    "monitor": "Others"
                }
            },
            "conversation": conversation,
            "summary_hints": {
                "user_talk_time_seconds": round(user_talk_time, 2),
                "others_talk_time_seconds": round(others_talk_time, 2),
                "silence_gaps": silence_gaps,
                "avg_segment_length": avg_segment_length,
                "total_segments": total_segments
            }
        }
        
        return enhanced_format
