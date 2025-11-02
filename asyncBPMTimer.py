import asyncio
import time

from BPMTimer import BPMTimer

class AsyncBPMTimer(BPMTimer):
    """Async version of BPMTimer"""
    
    async def async_wait_until_beat(self, target_beat):
        """Async version of wait_until_beat"""
        target_time = self.beat_to_time(target_beat)
        sleep_time = target_time - time.perf_counter()
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
    
    async def async_wait_for_beats(self, num_beats):
        """Async version of wait_for_beats"""
        await asyncio.sleep(num_beats * self.beat_duration)

async def async_drum_pattern(timer, name, pattern, subdivision=0.25):
    """Async drum pattern"""
    step = 0
    while True:
        if pattern[step % len(pattern)]:
            print(f"{name}: ▶ Beat {timer.get_current_beat():.2f}")
        
        await timer.async_wait_for_beats(subdivision)
        step += 1

async def async_dac_control(timer, dac, waveform_func):
    """Async DAC control loop"""
    sample_rate = 1000
    interval = 1.0 / sample_rate
    sample = 0
    start = time.perf_counter()
    
    while True:
        # Get current musical time
        current_beat = timer.get_current_beat()
        
        # Generate voltage
        voltage = waveform_func(current_beat)
        dac.set_voltage(voltage)
        
        # Precise timing
        sample += 1
        next_time = start + (sample * interval)
        sleep_time = next_time - time.perf_counter()
        
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)

async def main():
    timer = AsyncBPMTimer(120)
    
    kick = [1, 0, 0, 0, 1, 0, 0, 0]
    snare = [0, 0, 1, 0, 0, 0, 1, 0]
    hihat = [1, 1, 1, 1, 1, 1, 1, 1]
    
    # Run all patterns concurrently
    await asyncio.gather(
        async_drum_pattern(timer, "Kick", kick, 0.5),
        async_drum_pattern(timer, "Snare", snare, 0.5),
        async_drum_pattern(timer, "HiHat", hihat, 0.25),
    )

# Run
# asyncio.run(main())