import clock
import event

master_clock = clock.Clock(80, 6)

master = event.Master("master", 10, 4)
trigger = event.Trigger("trigger")
note = event.Note("note", 2, 4, ["1.0"])

master.connectClock(master_clock)
note.connectClock(master_clock)
trigger.connectClock(master_clock)

master.addRuler("events", "triggers", trigger.name, [trigger.play])
master.addRuler("events", "notes", note.name, [note.play])

master.placeRuler('events', trigger.name,"1.1")
master.placeRuler('events', note.name,"2.1")
print(master.filterRulers(["events"]))



master.addRuler("keys", "generic", "first", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "generic", "second", ['c', 'c#', 'd', None, 'e', None])
master.addRuler("keys", "generic", "third", ['c', 'c#', 'd', 'd#', 'e', None])
master.addRuler("keys", "specific", "fourth", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "specific", "fifth", ['a', 'b', 'd', None, 'f', None])
master.addRuler("keys", "specific", "sixth", [None, 'c#', 'd', 'd#', 'e', None])
print(master)

#master.listRulers()
#print(master.filterRulers())
master.listStaffGroups()
master.placeRuler("keys", "first", "2.1")
master.placeRuler("keys", "second", "1.1")
master.placeRuler("keys", "third", "3.1", -1)
master.listStaffGroups()
master.placeRuler("keys", "fourth", "3.0")
master.placeRuler("keys", "fifth", "1.0", -2)
master.placeRuler("keys", "sixth", "2.0")
master.listStaffGroups()

print(master.stackStaffRulers(["keys"], ["generic"], "3.0"))
print(master.stackStaffRulers(["keys"], position="3.0"))

master.listRulers()
#print(master.filterRulers(positions = ["1.1"]))

master.listStaffGroups()



master.play()




master_clock.start()