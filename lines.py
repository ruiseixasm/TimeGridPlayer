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

class Lines:
        
    def __init__(self):
        self._lines = { 'lines': [], 'offset': 0 }

    def __str__(self) -> str:
        return "{ lines: " + f"{self._lines['lines']}" + "    offset: " + f"{self._lines['offset']}" + " }"

    def clear(self):
        self._lines['lines'].clear()

        return self

    def empty(self, length=1):
        self._lines['lines'] = [None] * length

        return self
    
    def lines(self):
        return self._lines

    def print(self):
        print("{ lines: " + f"{self._lines['lines']}" + "    offset: " + f"{self._lines['offset']}" + " }")

        return self

    def reset(self):
        self._lines['lines'].clear()
        self._lines['offset'] = 0

        return self

    def set_offset(self, offset=0):
        self._lines['offset'] = offset

        return self
    
