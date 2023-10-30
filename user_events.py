import clock
import action

master_clock = clock.Clock(80, 6)

master = action.Master("master", 10, 4)
trigger = action.Trigger("trigger")
note = action.Note("note", 2, 4, [None, "1.0"])

master.connectClock(master_clock)
note.connectClock(master_clock)
trigger.connectClock(master_clock)

master.addRuler("actions", "triggers", trigger.name, [trigger.actionPlay])
master.addRuler("actions", "notes", note.name, [note.actionPlay])
master.addRuler("actions", "notes", note.name + "_2", [note.actionPlay])

master.placeRuler('actions', trigger.name,"1.1")
master.placeRuler('actions', note.name,"2.1")
master.placeRuler('actions', note.name + "_2","4.1")
print(master.filterRulers(["actions"]))



master.addRuler("keys", "generic", "first", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "generic", "second", ['c', 'c#', 'd', None, 'e', None])
master.addRuler("keys", "generic", "third", ['d', 'c#', 'd', 'd#', 'e', None])
master.addRuler("keys", "specific", "fourth", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "specific", "fifth", ['a', 'b', 'd', None, 'f', None])
master.addRuler("keys", "specific", "sixth", [None, 'c#', 'd', 'd#', 'e', None])
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



master.actionPlay()



#master_clock.start()

master_clock.start(4, ["4.0", "6.0"])