import time
import rtmidi

out = rtmidi.MidiOut()
ports = out.get_ports()

print(ports)

out.open_port(0)

with out:
    note_on = [0x94, 48, 100]
    note_off = [0x84, 48, 0]
    out.send_message(note_on)
    time.sleep(1)
    out.send_message(note_off)
    time.sleep(0.4)