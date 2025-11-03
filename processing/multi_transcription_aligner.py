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
