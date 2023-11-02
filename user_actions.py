import rulers
import clock
import action




master_clock = clock.Clock(80, 4)

master = action.Master(10, 4)
trigger = action.Trigger()
note = action.Note(2, 4, [None, "1.0"])

master.addRuler("actions", "triggers", [trigger])
master.addRuler("actions", "notes", [note])
master.addRuler("actions", "notes", [note])

master.placeRuler('actions', "1.1")
master.placeRuler('actions', "2.1")
master.placeRuler('actions', "4.1")
print(master.filterRulers(["actions"]))



master.addRuler("keys", "generic", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "generic", ['c', 'c#', 'd', None, 'e', None])
master.addRuler("keys", "generic", ['d', 'c#', 'd', 'd#', 'e', None])
master.addRuler("keys", "specific", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "specific", ['a', 'b', 'd', None, 'f', None])
master.addRuler("keys", "specific", [None, 'c#', 'd', 'd#', 'e', None])
#print(master)

#master.listRulers()
#print(master.filterRulers())
#master.listStaffGroups()

master.placeRuler("keys", "first", "2.1")
master.placeRuler("keys", "second", "1.1")
master.placeRuler("keys", "third", "3.1", -1)

#master.listStaffGroups()

master.placeRuler("keys", "fourth", "3.0")
master.placeRuler("keys", "fifth", "1.0", -2)
master.placeRuler("keys", "sixth", "2.0")

#master.listStaffGroups()
# print(master.stackStaffRulers(["keys"], ["generic"], "3.0"))
# print(master.stackStaffRulers(["keys"], position="3.0"))

#master.listRulers()
#print(master.filterRulers(positions = ["1.1"]))



master.connectClock(master_clock)
note.connectClock(master_clock)
trigger.connectClock(master_clock)
master_clock.start()
print("\n\n\nNEXT ITERATION\n\n")
master_clock.start(["4.0", "6.0"])