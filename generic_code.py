list_1 = [1, 2, 3, 4]
list_2 = [1, 2]

# list_3 = list_1 - list_2

# print(list_3)


list_empty = []

sliced_list = list_empty[:2]
print (sliced_list)

my_list = [1, 2, 3, 4, 5]
last_element = my_list[-3:]
print(last_element)
last_element = my_list[::2]
print(last_element)
last_element = my_list[1::2]
print(last_element)

def position(sequence):
    steps = int(sequence / 4)
    frames = sequence % 4
    if sequence < 0:
        frames = -(-sequence % 4)
    return [steps, frames]

sequence = -13
print (position(sequence))

sequence = 13
print (position(sequence))


dict_1 = {'value': 10, 'value2': 11, 'value3': 12, 'value4': 13, 'value5': 14, 'list1': [1, 2, 3, "a"]}
dict_2 = {'value': 10, 'value2': 11, 'value3': 12, 'value4': 13, 'value5': 14, 'list1': [1, 2, 3, "a"]}
dic_list = []
dic_list.append(dict_1)
print (dic_list)
print (dict_1 == dict_2)
print (dict_2 in dic_list)

list_1 = [1, 5]
list_2 = [1, 5]
big_list = []
big_list.append(list_1)
print (big_list)
print (list_1 == list_2)
print (list_2 in big_list)


list_a = ["A"]
list_b = list_a
list_b[0] = "B"
print (list_a)

# keys_1 = {'enabled': 1, 'total': 2}
# keys_2 = {'enabled': 2, 'total': 3}
# keys_3 = keys_1 + keys_2
# print (keys_3)