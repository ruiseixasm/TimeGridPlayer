import time
import mido

msg_on = mido.Message('note_on', note=60)
msg_on.type
# 'note_on'
msg_on.note
# 60
msg_on.bytes()
# [144, 60, 64]
#msg_on.copy(channel=2)
# Message('note_on', channel=2, note=60, velocity=64, time=0)


msg_off = mido.Message('note_off', note=60)


port = mido.open_output("Microsoft GS Wavetable Synth 0")
port.send(msg_on)

time.sleep(2)

port.send(msg_off)