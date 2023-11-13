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

import player as Player

trigger = Player.Trigger("trigger")
# trigger.useInternalClock(True)

print("\n\n")

trigger.rulers().add({'type': "actions", 'group': "triggers", 'position': [1, 1], 'lines': [trigger]})
trigger.rulers().add({'type': "actions", 'group': "triggers", 'position': [3, 1], 'lines': [trigger]})
trigger.rulers().filter(type="actions").sort().print().print_lines()

trigger.play()
print("\n\n\nNEXT ITERATION\n\n")
#trigger.play([1, 0], [4, 0])