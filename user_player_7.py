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

stage_midi = STAGE_MIDI.StageMidi()

# add a master player to stage
stage_midi.add("master")
stage_midi.add("note", type="Note")
stage_midi.add("repeat", type="Master")

note = stage_midi.print().player("note").print()

note.use_resource("loop").enable_resource()

note.print()