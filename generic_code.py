'''TimeGridPlayer - Time Grid Player triggers Actions on a Staff
Original Copyright (c) 2023 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.'''

# list_1 = [1, 2, 3, 4]
# list_2 = [1, 2]

# list_3 = list_1 - list_2

# print(list_3)


# list_empty = []

# sliced_list = list_empty[:2]
# print (sliced_list)

# my_list = [1, 2, 3, 4, 5]
# last_element = my_list[-3:]
# print(last_element)
# last_element = my_list[::2]
# print(last_element)
# last_element = my_list[1::2]
# print(last_element)

# def position(sequence):
#     steps = int(sequence / 4)
#     frames = sequence % 4
#     if sequence < 0:
#         frames = -(-sequence % 4)
#     return [steps, frames]

# sequence = -13
# print (position(sequence))

# sequence = 13
# print (position(sequence))


# dict_1 = {'value': 10, 'value2': 11, 'value3': 12, 'value4': 13, 'value5': 14, 'list1': [1, 2, 3, "a"]}
# dict_2 = {'value': 10, 'value2': 11, 'value3': 12, 'value4': 13, 'value5': 14, 'list1': [1, 2, 3, "a"]}
# dic_list = []
# dic_list.append(dict_1)
# print (dic_list)
# print (dict_1 == dict_2)
# print (dict_2 in dic_list)

# list_1 = [1, 5]
# list_2 = [1, 5]
# big_list = []
# big_list.append(list_1)
# print (big_list)
# print (list_1 == list_2)
# print (list_2 in big_list)


# list_a = ["A"]
# list_b = list_a
# list_b[0] = "B"
# print (list_a)

# keys_1 = {'enabled': 1, 'total': 2}
# keys_2 = {'enabled': 2, 'total': 3}
# keys_3 = keys_1 + keys_2
# print (keys_3)

# int_1 = 10
# int_2 = 3
# print (int_1 / int_2)

# print(round(-1.2))
# print(round(-1.5))
# print(round(-1.6))

# print (2.5 % 2)
# print (round(2.777777 % 2, 6))

# test = "TEST"
# o = "{"
# c = "}"
# print(f"{o}{test}{c}")

# int_number = 2
# float_number = 3.0
# another_float_number = 4.3

# print (f"{int_number} {float_number:.6f} {another_float_number:.0f}")

# print ("  `  ´  .  -  _  ")


# one_list_1 = ["A"]
# one_list_2 = one_list_1

# one_list_1.clear()
# print(one_list_2)
# one_list_1.append("B")

# print(one_list_2)



# def trimString(full_string):
#     string_maxum_size = 16
#     long_string_termination = "…"
#     trimmed_string = full_string
#     if len(full_string) > string_maxum_size:
#         trimmed_string = full_string[:string_maxum_size] + long_string_termination

#     return trimmed_string

# string_1 = "small"
# string_2 = "very big string again it's true"

# print (trimString(string_1))
# print (trimString(string_2))


# some_list = {}

# print(type(some_list))
# print(type(some_list) == type({}))

some_list = [1]

print(len(some_list))

print(len(some_list*0))

print (True if None else False)