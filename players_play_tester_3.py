'''TimeGridPlayer - Time Grid Player triggers Actions on a Staff
Original Copyright (c) 2023 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.'''

import stage_midi as STAGE_MIDI
import lines_scales as LINES_SCALES

scales = LINES_SCALES.Scales()
keys_major_scale = scales.scale("major", "A", 5).lines()

# add a master player to a new stage
stage = STAGE_MIDI.StageMidi()

# stage.set_tempo(90).add("clock", type="Clock")
# stage.set_time_signature(steps_per_quarternote=6, pulses_per_quarternote=48)
# master = stage.add("master", default=True).last().player()
# note = stage.add("note", type="Note").last().player()
# pattern = stage.add("pattern").last().player().set_length(1)
# stage.use_resource("loop").enable_resource().print()

# pattern.rulers().add({'link': "note.channel.staff", 'lines': 10}).print()
# stage.json_save("players_play_tester_3.json").print()

stage.json_load("players_play_tester_3.json").print()
master = stage.player(name="master")
note = stage.player(name="note")
pattern = stage.player(name="pattern")

pattern.rulers().print().every(3).print()

#pattern.rulers().print().ids(2).drag(2,3).root().print()

#stage.play()
