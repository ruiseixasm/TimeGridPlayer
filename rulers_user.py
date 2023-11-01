import rulers


newRuler = {
    'type': "keys",
    'group': "main",
    'lines': [None],
    'position': [0, 0],
    'offset': 0,
    'enabled': True
}

userRulers = rulers.Rulers([newRuler])
userRulers.add({'type': "actions"}).print()

copied_rulers = userRulers.copy()

userRulers.filter(["actions"]).print()
userRulers.filter(["actions"]).remove().print()

userRulers.print()

copied_rulers.print()

print(copied_rulers.list())