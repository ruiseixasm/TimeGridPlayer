import midi_tools

windows_synth = midi_tools.Instrument()

print(windows_synth.list())

windows_synth.connect(name="loop").print().test()

windows_synth.disconnect()