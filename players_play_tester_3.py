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
# stage.set_tempo(90)
# stage.set_time_signature(steps_per_quarternote=6, pulses_per_quarternote=48)
# master = stage.add("master").last().player()
# note = stage.add("note", type="Note").last().player()
# pattern = stage.add("pattern").last().player().set_length(1)
# stage.add("clock", type="Clock").use_resource("loop").enable_resource()

stage.json_load("players_play_tester_3.json")
master = stage.player("master")
note = stage.player("note")
pattern = stage.player("pattern")
pattern.rulers().print().ids(2).drag(2,3).root().print()

#stage.play()
