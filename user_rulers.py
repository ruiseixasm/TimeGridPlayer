import rulers
import staff

staff_grid = staff.Staff(10, 4)

newRuler = {
    'type': "keys",
    'group': "main",
    'position': [1, 3],
    'lines': [None],
    'offset': 0,
    'enabled': True
}

userRulers = rulers.Rulers([newRuler], staff_grid)
userRulers.add({'type': "actions", 'position': [2, 3]})
userRulers.add({'type': "actions", 'position': [2, 3]})

print("\nROOT\n")
userRulers.add({'type': "actions", 'position': [1, 3]}).print()

copied_rulers = userRulers.copy().print()

userRulers.add({'type': "actions", 'position': [0, 3]})

# userRulers.filter(["actions"]).print()
# userRulers.filter(["actions"]).remove().print()

# userRulers.print()



userRulers.unique().sort(key='key').print()
# copied_rulers.print()

print("\n+\n")
add_rulers = (userRulers + copied_rulers).unique().print()
# add_rulers.print()

print("\nSTAFF\n")
staff_grid.print()
print(f"keys: {staff_grid.keys()} actions: {staff_grid.actions()}")
# print("\n-\n")
# sub_rulers = userRulers - copied_rulers
# lines = sub_rulers.print().lines()
# print (lines)

# staff_grid.print()
# print(f"keys: {staff_grid.keys()} actions: {staff_grid.actions()}")

print("\nEVEN\n")
add_rulers.unique().even().print().slide([-2, 0]).print().slide([1, 2]).print()

print("\nODD\n")
add_rulers.unique().odd().print().disable().print()

print("\nROOT\n")
userRulers.print()

print("\nSTAFF\n")
staff_grid.print()
print(f"keys: {staff_grid.keys()} actions: {staff_grid.actions()}")
# print(f"keys: {staff_grid.keys()} actions: {staff_grid.actions()}")

# userRulers.unique().sort().print().filter(positions=[[1, 2], [1, 3]]).print()

print("\nMERGED\n")
userRulers.merge().print()

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