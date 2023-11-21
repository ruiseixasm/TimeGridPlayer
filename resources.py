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

class Resources:
        
    def __init__(self):
        self._next_id = 0

    @property
    def is_none(self):
        return (self.__class__.__name__ == ResourcesNone.__name__)

    def add(self, name):
        pass
        
    def enable(self, resource):
        pass

    def enabled(self, resource):
        pass

    def disable(self, resource):
        pass

    def remove(self, resource):
        pass

    class Resource():
        
        def enable(self):
            pass

        def enabled(self):
            pass

        def disable(self):
            pass


class ResourcesNone(Resources):

    def __init__(self):
        super().__init__()
