from master import Master

master = Master(4, 4, 3.123)

master.addRuler("keys", "first", "generic", ['c', 'c#', 'd', 'd#', 'e', 'f'])
master.listRulers()
print(master.filterRulers())
master.placeRuler("keys", "first", "1.1")
master.listRulers()
print(master.filterRulers(positions = ["1.1"]))

print_hello = lambda rule : print("Hello ", rule)

master.addRuler("events", "first", "generic", [
        None,
        print_hello, None,
        lambda rule : print("Hi ", rule),
        None, None
    ])
#print(master)
#master.play()