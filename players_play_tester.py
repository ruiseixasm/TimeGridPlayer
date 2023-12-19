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

stage = STAGE_MIDI.StageMidi()

# add a master player to stage
master = stage.add("master").last().player()

# add note with the respective midi resource already enabled
note = stage.add("note", type="Note").last().player().use_resource("loop").enable_resource()

# type 'python -i interactive_mode_startup.py' to use the present script in interactive mode
# type 'exit()' to exit


pattern = stage.add("pattern").last().player()
pattern.rulers().add({'link': "note", 'lines': ["1/4"]}).print_lines()
pattern.set_length(1)

stage.json_load("james_brown_1.json").print()
stage.play()
