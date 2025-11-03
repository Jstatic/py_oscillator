import time
import math

class BPMTimer:
    """Convert between perf_counter timestamps and musical timing (BPM)"""
    
    def __init__(self, bpm, start_time=None):
        """
        Initialize BPM timer
        
        Args:
            bpm: Beats per minute
            start_time: Starting perf_counter time (defaults to now)
        """
        self.bpm = bpm
        self.start_time = start_time if start_time is not None else time.perf_counter()
        self.beat_duration = 60.0 / bpm  # seconds per beat
    
    def get_current_beat(self):
        """Get current beat number (float) since start"""
        elapsed = time.perf_counter() - self.start_time
        return elapsed / self.beat_duration
    
    def get_current_bar(self, beats_per_bar=4):
        """Get current bar number (float) since start"""
        return self.get_current_beat() / beats_per_bar
    
    def time_to_beat(self, timestamp):
        """Convert perf_counter timestamp to beat number"""
        elapsed = timestamp - self.start_time
        return elapsed / self.beat_duration
    
    def beat_to_time(self, beat_number):
        """Convert beat number to perf_counter timestamp"""
        return self.start_time + (beat_number * self.beat_duration)
    
    def wait_until_beat(self, target_beat):
        """Sleep until a specific beat number"""
        target_time = self.beat_to_time(target_beat)
        sleep_time = target_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    def wait_for_beats(self, num_beats):
        """Wait for a specific number of beats"""
        time.sleep(num_beats * self.beat_duration)
    
    def get_phase(self):
        """Get current phase within beat (0.0 to 1.0)"""
        beat = self.get_current_beat()
        return beat - int(beat)
    
    def sync_to_next_beat(self):
        """Wait until the next whole beat"""
        current_beat = self.get_current_beat()
        next_beat = int(current_beat) + 1
        self.wait_until_beat(next_beat)
    
    def change_bpm(self, new_bpm, smooth=False):
        """
        Change BPM, optionally maintaining current beat position
        
        Args:
            new_bpm: New tempo
            smooth: If True, maintain current beat position
        """
        if smooth:
            current_beat = self.get_current_beat()
            self.bpm = new_bpm
            self.beat_duration = 60.0 / new_bpm
            # Adjust start time to maintain beat position
            self.start_time = time.perf_counter() - (current_beat * self.beat_duration)
        else:
            self.bpm = new_bpm
            self.beat_duration = 60.0 / new_bpm
            self.start_time = time.perf_counter()
    
    def phase_to_sine(self, phase_offset=0.0, beat_multiplier=1.0):
        def waveform_func(beat):
            # Calculate phase: (beat * multiplier + offset) * 2π
            phase = (beat * beat_multiplier + phase_offset) * 2 * math.pi
            return math.sin(phase)
        
        return waveform_func