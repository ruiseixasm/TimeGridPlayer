import clock
import event

master = event.Master("master", 10, 6)

master.addRuler("keys", "first", "generic", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "second", "generic", ['c', 'c#', 'd', None, 'e', None])
master.addRuler("keys", "third", "generic", ['c', 'c#', 'd', 'd#', 'e', None])
master.addRuler("keys", "fourth", "specific", [None, 'c#', None, None, 'e', None])
master.addRuler("keys", "fifth", "specific", ['a', 'b', 'd', None, 'f', None])
master.addRuler("keys", "sixth", "specific", [None, 'c#', 'd', 'd#', 'e', None])
print(master)

#master.listRulers()
#print(master.filterRulers())
master.listStaffGroups()
master.placeRuler("keys", "first", "2.1")
master.placeRuler("keys", "second", "1.1")
master.placeRuler("keys", "third", "3.1")
master.listStaffGroups()
master.placeRuler("keys", "fourth", "3.0")
master.placeRuler("keys", "fifth", "1.0")
master.placeRuler("keys", "sixth", "2.0")
master.listStaffGroups()

print(master.stackStaffRulers(["keys"], ["generic"], "3.0"))
print(master.stackStaffRulers(["keys"], [], "3.0"))

master.listRulers()
#print(master.filterRulers(positions = ["1.1"]))

print_hello = lambda line, staffKeys : print(f"Hello\tLine: {line}\t{staffKeys}")

master.addRuler("events", "first", "messages", [
        None,
        print_hello, None,
        lambda line, staffKeys : print(f"Hi\tLine: {line}\t{staffKeys}"),
        None, None
    ])

master.placeRuler("events", "first", "3.0")

master.listStaffGroups()

print(master.filterRulers(["events"]))


note = event.Note("note", 1, 6)

master_clock = clock.Clock(60, 6)
master.connectClock(master_clock)
master.play()
master_clock.start()