import clock as Clock
import actions_piano as Piano

master_clock = Clock.Clock(80, 24)

master = Piano.Master("master")
trigger = Piano.Trigger("trigger")
note = Piano.Note("notes", 1, 4, 1, play_range=[[0, 0], [1, 0]])

print("\n\n")

master.rulers().add({'type': "actions", 'group': "triggers", 'position': [1, 1], 'lines': [trigger]})
master.rulers().add({'type': "actions", 'group': "triggers", 'position': [3, 1], 'lines': [trigger]})
master.rulers().add({'type': "actions", 'group': "notes", 'position': [2, 1], 'lines': [note]})
master.rulers().add({'type': "actions", 'group': "notes", 'position': [4, 1], 'lines': [note]})
master.rulers().filter(type="actions").sort().print().print_lines()

master.rulers().add({'type': "arguments", 'group': "generic", 'position': [2, 1], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "generic", 'position': [1, 0], 'lines': ['c', 'c#', 'd', None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "generic", 'position': [3, 0], 'lines': ['d', 'c#', 'd', 'd#', 'e', None], 'offset': -1})
master.rulers().add({'type': "arguments", 'group': "specific", 'position': [2, 2], 'lines': [None, 'c#', None, None, 'e', None]})
master.rulers().add({'type': "arguments", 'group': "specific", 'position': [1, 1], 'lines': ['a', 'b', 'd', None, 'f', None], 'offset': -2})
master.rulers().add({'type': "arguments", 'group': "specific", 'position': [3, 2], 'lines': [None, 'c#', 'd', 'd#', 'e', None]})
master.rulers().filter(type="arguments").sort().print().print_lines(None, 8).spread_lines(-2).print_lines(None, 8).print()

# master.staff().print()
# trigger.staff().print()
# note.staff().print()


master.connectClock(master_clock)
note.connectClock(master_clock)
trigger.connectClock(master_clock)
master_clock.start()
print("\n\n\nNEXT ITERATION\n\n")
range_pulses = master.staff().setPlayRange([4, 0], [6, 0])
#master_clock.start(range_pulses)


print(master)
