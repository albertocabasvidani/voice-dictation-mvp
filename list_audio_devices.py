"""List all audio devices detected by sounddevice"""
import sounddevice as sd

print("\n" + "="*60)
print("AUDIO DEVICES")
print("="*60)

devices = sd.query_devices()
default_in = sd.default.device[0]
default_out = sd.default.device[1]

print(f"\nDefault INPUT device: {default_in}")
print(f"Default OUTPUT device: {default_out}\n")

print("ALL DEVICES:")
print("-" * 60)
for i, device in enumerate(devices):
    marker = ""
    if i == default_in:
        marker += " [DEFAULT INPUT]"
    if i == default_out:
        marker += " [DEFAULT OUTPUT]"

    print(f"\nIndex: {i}{marker}")
    print(f"  Name: {device['name']}")
    print(f"  Input channels: {device['max_input_channels']}")
    print(f"  Output channels: {device['max_output_channels']}")
    print(f"  Default sample rate: {device['default_samplerate']}")

print("\n" + "="*60)
print(f"Total devices: {len(devices)}")
print("="*60)
