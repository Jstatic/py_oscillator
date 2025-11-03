import math
from BPMTimer import BPMTimer

timer = BPMTimer(120)

if __name__ == "__main__":
    prev_beat = None
    prev_sine = None
    subdivision = 0.25
    target_beat = 0
    sequence_length = 16
    try:
        while True:
            waveform = timer.phase_to_sine()
            current_beat = timer.get_current_beat()
            sine_value = waveform(current_beat)
            
            print(f"beat: {current_beat:>8.2f}  sine: {sine_value:>8.2f}")
            
            if prev_beat is not None:
                beat_diff = current_beat - prev_beat
                beat_drift = beat_diff - subdivision
                beat_drift_ms = beat_drift * timer.beat_duration * 1000  # Convert to milliseconds
                
                # Calculate expected sine change for perfect subdivision
                expected_sine = waveform(prev_beat + subdivision)
                actual_sine_diff = sine_value - prev_sine
                expected_sine_diff = expected_sine - prev_sine
                sine_drift = actual_sine_diff - expected_sine_diff
                sequenced_beat = math.floor(current_beat % sequence_length) + 1
                print(f"sequenced beat: {sequenced_beat}")
                print(f"  Δbeat: {beat_drift:>8.4f} ({beat_drift_ms:>6.2f}ms)  Δsine: {sine_drift:>8.4f}")
            
            prev_beat = current_beat
            prev_sine = sine_value
            
            # Wait until next absolute beat position to avoid drift accumulation
            target_beat += subdivision
            timer.wait_until_beat(target_beat)
    except KeyboardInterrupt:
        print("Program stopped by user") 