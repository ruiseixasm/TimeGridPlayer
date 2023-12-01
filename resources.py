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
        self._available_resources = []
        self._next_id = 0

    def __del__(self):
        for available_resource in self._available_resources:
            available_resource['resource'].disable()

    @property
    def is_none(self):
        return (self.__class__ == ResourcesNone)
    
    def resourceFactoryMethod(self, name):
        return Resources.ResourceNone()

    def add(self, name):

        if name != None and not self.is_none:
        
            for available_resource in self._available_resources:
                if available_resource['name'] == name:
                    available_resource['users'] += 1
                    return available_resource['resource'] # IF EXISTENT
            new_resource = {
                'id': self._next_id,
                'type': self.__class__.__name__,
                'name': name,
                'resource': self.resourceFactoryMethod(name),
                'users': 1, # starts with the first user count
                'enables': 0
            }
            if not new_resource['resource'].is_none:
                self._next_id += 1
                self._available_resources.append(new_resource)
            return new_resource['resource'] # IF NON EXISTENT
        
        return Resources.ResourceNone()
    
    def disable(self, resource):
        for available_resource in self._available_resources:
            if available_resource['resource'] == resource:
                available_resource['enables'] -= 1
                if available_resource['enables'] == 0:
                    available_resource['resource'].disable()
                break
        
        return self
        
    def enable(self, resource):
        for available_resource in self._available_resources:
            if available_resource['resource'] == resource:
                if available_resource['enables'] == 0:
                    available_resource['resource'].enable()
                available_resource['enables'] += 1
                break
        
        return self
        
    def enabled(self, resource):
        for available_resource in self._available_resources:
            if available_resource['resource'] == resource:
                if available_resource['enables'] > 0:
                    return True
                break
        
        return False
            
    def remove(self, resource, force=False):
        for available_resource in self._available_resources[:]:
            if available_resource['resource'] == resource:
                available_resource['users'] -= 1
                if force == True or available_resource['users'] == 0:
                    available_resource['resource'].disable()
                    self._available_resources.remove(available_resource)
                break

        return self
    
    class Resource():
        
        @property
        def is_none(self):
            return (self.__class__ == ResourcesNone.ResourceNone)

        def enable(self):
            return self

        def enabled(self):
            return False

        def disable(self):
            return self

    class ResourceNone(Resource):
        def __init__(self):
            super().__init__()
            print ("Some needed resources were not allocated!")


class ResourcesNone(Resources):
    def __init__(self):
        super().__init__()
