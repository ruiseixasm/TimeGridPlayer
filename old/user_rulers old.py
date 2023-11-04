import rulers


newRuler = {
    'type': "keys",
    'group': "main",
    'position': [1, 3],
    'lines': [None],
    'offset': 0,
    'enabled': True
}

userRulers = rulers.Rulers([newRuler])
userRulers.add({'type': "actions", 'position': [2, 3]})
userRulers.add({'type': "actions", 'position': [2, 3]})
userRulers.add({'type': "actions", 'position': [1, 3]})

copied_rulers = userRulers.copy()

userRulers.add({'type': "actions", 'position': [0, 3]})

# userRulers.filter(["actions"]).print()
# userRulers.filter(["actions"]).remove().print()

# userRulers.print()

# copied_rulers.print()

# print(copied_rulers.list()) # FULL LIST

# print("\n\n")

userRulers.print()
copied_rulers.print()

print("\n+\n")
add_rulers = userRulers + copied_rulers
add_rulers.print()

# print("\n-\n")
# sub_rulers = userRulers - copied_rulers
# lines = sub_rulers.print().lines()
# print (lines)

print("\nEVEN\n")
add_rulers.even().print()

# print("\nUNIQUE\n")
# add_rulers.unique().print()

# print("\nSORTED\n")
# add_rulers.sort().print()
# print("\nREVERSE SORTED\n")
# add_rulers.sort(reverse=True).print()
# print("\nMERGED\n")
# add_rulers.merge().print()
# print("\nREVERSED\n")
# add_rulers.reverse().print()
# print("\nUNIQUE\n")
# add_rulers.unique().print()