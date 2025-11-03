import asyncio
import math

from asyncBPMTimer import AsyncBPMTimer

async def print_sequence(timer, interval_beats=4):
    """Print a value every N beats"""
    target_beat = 0
    sequence_length = 16
    
    while True:
        current_beat = timer.get_current_beat()
        sequenced_beat = int(current_beat % sequence_length)
        
        print(f"Print Sequence - Beat: {current_beat:>8.2f} | Sequenced: {sequenced_beat:>2d}")
        
        target_beat += interval_beats
        await timer.async_wait_until_beat(target_beat)

async def array_sequence(timer, pattern):
    """Print when array value is greater than 0, checking every beat"""
    target_beat = 0
    sequence_length = len(pattern)
    
    while True:
        current_beat = timer.get_current_beat()
        sequenced_beat = int(current_beat % sequence_length)
        array_value = pattern[sequenced_beat]
        
        # Only print if value is greater than 0
        if array_value > 0:
            print(f"Array Sequence - Beat: {current_beat:>8.2f} | Sequenced: {sequenced_beat:>2d} | Value: {array_value}")
        
        target_beat += 1  # Check every beat
        await timer.async_wait_until_beat(target_beat)

async def sine_wave_sequence(timer, pattern, wave_length_beats=8, dac=None):
    """Generate smoothly interpolated sine wave with array-controlled restart"""
    sample_rate = 100  # Hz - smooth interpolation for DAC
    sample_interval_seconds = 1.0 / sample_rate
    sample_interval_beats = sample_interval_seconds / timer.beat_duration
    
    target_beat = 0
    sequence_length = len(pattern)
    beat_multiplier = 1.0 / wave_length_beats  # One cycle per wave_length_beats
    
    waveform = timer.phase_to_sine(beat_multiplier=beat_multiplier)
    
    # DAC voltage range (0-5V typical)
    v_min = 0.0
    v_max = 5.0
    v_center = (v_max + v_min) / 2.0
    v_amplitude = (v_max - v_min) / 2.0
    
    print_counter = 0
    print_every = sample_rate // 8  # Print 8 times per second
    
    wave_start_beat = 0  # Track where the current wave cycle started
    
    while True:
        current_beat = timer.get_current_beat()
        sequenced_beat_int = int(current_beat % sequence_length)
        sequenced_beat = current_beat % sequence_length
        
        # Check if pattern indicates restart
        if pattern[sequenced_beat_int] > 0:
            wave_start_beat = current_beat
        
        # Calculate sine value relative to wave start
        wave_position = current_beat - wave_start_beat
        sine_value = waveform(wave_position)  # -1.0 to 1.0
        
        # Scale sine wave to DAC voltage range
        voltage = v_center + (sine_value * v_amplitude)
        
        # Set DAC voltage if DAC object is provided
        if dac is not None:
            dac.set_voltage(voltage)
        
        # Print periodically (not every sample to avoid flooding output)
        if print_counter % print_every == 0:
            print(f"Sine Sequence  - Beat: {current_beat:>8.2f} | Sequenced: {sequenced_beat:>5.2f} | Wave Pos: {wave_position:>5.2f} | Sine: {sine_value:>6.3f} | Voltage: {voltage:>5.2f}V")
        
        print_counter += 1
        target_beat += sample_interval_beats
        await timer.async_wait_until_beat(target_beat)

async def main():
    timer = AsyncBPMTimer(180)  # 180 BPM
    
    # Define the pattern array used by both array_sequence and sine_wave_sequence
    beat_pattern = [
        1.0, 0.0, 1.0, 0.0,  # beats 0-3
        1.0, 1.0, 1.0, 0.0,  # beats 4-7
        1.0, 1.0, 1.0, 0.0,  # beats 8-11
        1.0, 0.0, 0.0, 0.0   # beats 12-15
    ]

    sine_pattern = [
        1.0, 0.0, 0.0, 0.0,  # beats 0-3
        1.0, 0.0, 1.0, 0.0,  # beats 4-7
        1.0, 0.0, 0.0, 0.0,  # beats 8-11
        1.0, 0.0, 1.0, 0.0   # beats 12-15
    ]
    
    # Optional: Initialize DAC here
    # from mcp_4728 import MCP4728
    # dac = MCP4728()
    dac = None

    
    # Run all three sequences concurrently
    await asyncio.gather(
        print_sequence(timer, interval_beats=4),
        array_sequence(timer, beat_pattern),
        sine_wave_sequence(timer, sine_pattern, wave_length_beats=4, dac=dac)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped by user")

