import smbus
import time
import math
import random

# Initialize I2C bus (1 for newer Raspberry Pi models)
bus = smbus.SMBus(1)

# MCP4728 I2C address (default is 0x60)
MCP4728_ADDR = 0x60

# BPM settings
BPM = 120
BEAT_DURATION = 60.0 / BPM  # Duration of one beat in seconds (0.5s for 120 BPM)
GATE_DURATION = 0.25  # Gate pulse duration in seconds
SINE_WAVE_BEATS = 4  # Number of beats for one complete sine wave cycle

def set_dac_channel(channel, value):
    """
    Set MCP4728 DAC output value for a specific channel
    channel: 0-3 (A, B, C, D)
    value: 0-4095 (12-bit)
    """
    if channel < 0 or channel > 3:
        raise ValueError("Channel must be between 0 and 3")
    if value < 0 or value > 4095:
        raise ValueError("Value must be between 0 and 4095")
    
    # Single Write command: 0x40 | (channel << 1)
    cmd = 0x40 | (channel << 1)
    
    # Split 12-bit value into two bytes
    msb = (value >> 8) & 0x0F  # Upper 4 bits
    lsb = value & 0xFF          # Lower 8 bits
    
    # Write to the specified channel
    bus.write_i2c_block_data(MCP4728_ADDR, cmd, [msb, lsb])

def set_channel_a(value):
    """Convenience function for channel A"""
    set_dac_channel(0, value)

def set_channel_b(value):
    """Convenience function for channel B"""
    set_dac_channel(1, value)

def sine_wave_value(phase, amplitude=1.0):
    """
    Generate a sine wave value (0-4095)
    phase: 0.0 to 1.0 representing one complete cycle
    amplitude: 0.0 to 1.0 representing the amplitude of the sine wave
    """
    # sine wave oscillates between -1 and 1
    sine = math.sin(2 * math.pi * phase) * amplitude
    # Convert to 0-4095 range
    value = int((sine + 1) * 2047.5)  # Scale -1..1 to 0..4095
    return max(0, min(4095, value))  # Clamp to valid range

# Main loop
if __name__ == "__main__":
    sine_cycle_duration = BEAT_DURATION * SINE_WAVE_BEATS
    print(f"MCP4728 Random Amplitude Sine Wave and Gate at {BPM} BPM")
    print(f"Channel A: Sine wave with random amplitude every {SINE_WAVE_BEATS} beats ({sine_cycle_duration:.2f}s)")
    print(f"Channel B: {GATE_DURATION}s gate pulse every beat ({BEAT_DURATION:.3f}s)")
    print("Press Ctrl+C to exit\n")
    
    try:
        # Initialize both channels to LOW
        set_channel_a(0)
        set_channel_b(0)
        
        beat_count = 0
        total_step = 0
        steps_per_beat = 50  # Steps per beat for smooth updates
        total_steps_per_cycle = steps_per_beat * SINE_WAVE_BEATS  # Total steps for complete sine wave
        step_duration = BEAT_DURATION / steps_per_beat
        
        # Initialize first random amplitude
        current_amplitude = random.uniform(0.2, 1.0)  # Random amplitude between 20% and 100%
        print(f"Starting sine wave cycle with amplitude: {current_amplitude:.2f}")
        
        while True:
            beat_count += 1
            sine_beat = ((beat_count - 1) % SINE_WAVE_BEATS) + 1
            
            # At the start of a new sine wave cycle, pick a new random amplitude
            if sine_beat == 1:
                current_amplitude = random.uniform(0.2, 1.0)  # Random amplitude between 20% and 100%
                print(f"\nNew sine wave cycle {(beat_count - 1) // SINE_WAVE_BEATS + 1} - Amplitude: {current_amplitude:.2f}")
            
            print(f"Beat {beat_count} (Sine beat {sine_beat}/{SINE_WAVE_BEATS}) - Gate pulse")
            
            # Start gate pulse on Channel B (HIGH)
            set_channel_b(4095)
            
            # Process one beat worth of steps
            for step in range(steps_per_beat):
                # Calculate overall phase across all 4 beats (0.0 to 1.0)
                phase = (total_step % total_steps_per_cycle) / total_steps_per_cycle
                
                # Set Channel A to sine wave value with current amplitude
                sine_value = sine_wave_value(phase, current_amplitude)
                set_channel_a(sine_value)
                
                # Turn off gate after GATE_DURATION
                elapsed_time = step * step_duration
                if elapsed_time >= GATE_DURATION and elapsed_time < (GATE_DURATION + step_duration):
                    set_channel_b(0)  # Gate goes LOW
                
                # Wait for next step
                time.sleep(step_duration)
                total_step += 1
            
            # Ensure gate is off at end of beat
            set_channel_b(0)
    
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
        # Set all outputs to 0 when exiting
        for channel in range(4):
            set_dac_channel(channel, 0)
        print("All channels set to 0V")