from master import Master

master = Master(4, 4, 3.123)

master.addRuler("first", "1.1", ['c', 'c#', 'd', 'd#', 'e', 'f'])

print_hello = lambda rule : print("Hello ", rule)

master.addEvents("first", "2.1", [
        None,
        print_hello, None,
        lambda rule : print("Hi ", rule),
        None, None
    ])
print(master)
master.play()