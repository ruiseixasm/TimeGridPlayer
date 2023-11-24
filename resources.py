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

import json

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
    
    def json_dictionnaire(self):
        resources = {
                'part': "resources",
                'type': self.__class__.__name__,
                'next_id': self._next_id,
                'resources': []
            }
        
        for resource_dictionnaire in self._available_resources:
            resource_json = {}
            resource_json['part'] = "resource",
            resource_json['type'] = resource_dictionnaire['resource'].__class__.__name__,
            resource_json['id'] = resource_dictionnaire['id']
            resource_json['name'] = resource_dictionnaire['name']
            resource_json['users'] = resource_dictionnaire['users']
            resource_json['enables'] = resource_dictionnaire['enables']
            resources['resources'].append( resource_json )

        return resources
    
    def json_load(self, file_name="group.json", json_object=None):

        if json_object == None:
            # Opening JSON file
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)

        self._root_self._players_list.clear()

        for group_dictionnaire in json_object:
            if group_dictionnaire['part'] == "group":
                self._root_self._next_id = group_dictionnaire['next_id']
                for player_dictionnaire in group_dictionnaire['players']:
                    player = self._root_self._playerFactoryMethod(player_dictionnaire)
                    if player != None:
                        player.json_load(file_name, [ player_dictionnaire ])
                        player_data = {
                            'id': player_dictionnaire['id'],
                            'type': player.__class__.__name__,
                            'name': player.name,
                            'player': player,
                            'enabled': player_dictionnaire['enabled']
                        }
                        self._root_self._players_list.append(player_data)
                break

        return self

    def json_save(self, file_name="group.json"):

        group = [ self.json_dictionnaire() ]

        # Writing to sample.json
        with open(file_name, "w") as outfile:
            json.dump(group, outfile)

        return self

    class Resource():
        
        @property
        def is_none(self):
            return (self.__class__.__name__ == ResourcesNone.ResourceNone.__name__)

        def enable(self):
            return self

        def enabled(self):
            return False

        def disable(self):
            return self

    class ResourceNone(Resource):
        def __init__(self):
            super().__init__()


class ResourcesNone(Resources):
    def __init__(self):
        super().__init__()
