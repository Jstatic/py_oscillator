import time
from BPMTimer import BPMTimer

# Example 1: Basic metronome
def metronome_example():
    timer = BPMTimer(120)  # 120 BPM
    
    for beat in range(16):
        print(f"Beat {beat + 1} at {time.perf_counter():.3f}s")
        timer.wait_until_beat(beat + 1)

metronome_example()
