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

import time
import json
import resources as RESOURCES
import staff as STAFF
import group as GROUP

class Player:

    def __init__(self, name, description="A Player of actions based on arguments", resources=None):

        self._none = False

        self._name = name
        self._description = description

        self._resources = resources
        if self._resources == None:
            self._resources = RESOURCES.ResourcesNone()
        self._resource = None
        self._enabled_resource = False

        self._staff = STAFF.Staff(self)
        self._clock = Player.Clock(self)
        self._internal_clock = False

        # Iterator & Composite patterns for managing aggregates
        self._lower_group = GROUP.Group(owner_player=self)
        
        self._actions = []

    def __del__(self):
        self.discard_resource()

    @property
    def resources(self):
        return self._resources
            
    @resources.setter
    def resources(self, resources):
        self._resources = resources
            
    @resources.deleter
    def resources(self):
        self._resources = None

    @property
    def resource(self):
        return self._resource
            
    def use_resource(self, name=None):
        if self._resources != None:
            self._resource = self._resources.add(name)
        return self

    def enable_resource(self):
        if self._resources != None and self._resource != None and not self._enabled_resource:
            self._resources.enable(self._resource)
            self._enabled_resource = True
        return self

    def disable_resource(self):
        if self._resources != None and self._resource != None and self._enabled_resource:
            self._resources.disable(self._resource)
            self._enabled_resource = False
        return self

    def discard_resource(self):
        if self._resources != None and self._resource != None:
            self.disable_resource()
            self._resources.remove(self._resource)
        return self

    @property
    def is_none(self):
        return (self.__class__ == PlayerNone)

    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description
    
    @property
    def lower_group(self):
        return self._lower_group
            
    @lower_group.setter
    def lower_group(self, group):
        self._lower_group = group

    @lower_group.deleter
    def lower_group(self):
        self._lower_group = GROUP.GroupNone()
            
    class Action():

        def __init__(self, player):

            self._player = player
            self._staff = self._player.getStaff()

            self._internal_arguments_rulers = self._player.rulers().empty()
            self._external_arguments_rulers = self._player.rulers().empty()

            self._play_mode = True # By default whenever a new Action is created is considered in play mode
            self._start_pulse = self._player.rangePulses()['start']
            self._finish_pulse = self._player.rangePulses()['finish']
            self._play_pulse = self._start_pulse

            self._clocked_actions = []
            self._next_clocked_pulse = -1

        # using property decorator 
        # a getter function 
        @property
        def external_arguments_rulers(self):
            return self._external_arguments_rulers
    
        # a setter function (requires previous @property decorator)
        @external_arguments_rulers.setter 
        def external_arguments_rulers(self, rulers):
            self._external_arguments_rulers = rulers

        # a deleter function (requires previous @property decorator)
        @external_arguments_rulers.deleter 
        def external_arguments_rulers(self):
            #del self._external_arguments_rulers
            self._external_arguments_rulers = self._player.rulers().empty()

        def addClockedAction(self, clocked_action, tick): # Clocked actions AREN'T rulers!
            if (clocked_action['duration'] != None and clocked_action['action'] != None):
                time_signature = self._staff.time_signature()
                pulses_duration = clocked_action['duration'] * time_signature['pulses_per_beat'] / time_signature['steps_per_beat'] # Action pulses per step considered
                clocked_action['pulse'] = round(tick['pulse'] + pulses_duration)
                clocked_action['stack_id'] = len(self._clocked_actions)
                self._clocked_actions.append(clocked_action)

                if (not self._next_clocked_pulse < tick['pulse']):
                    self._next_clocked_pulse = min(self._next_clocked_pulse, clocked_action['pulse'])
                else:
                    self._next_clocked_pulse = clocked_action['pulse']

            return self

        def isPlaying(self):
            return self._play_mode

        def pickTriggeredLineArgumentValue(self, merged_staff_arguments, argument_name):
            line_argument_value = None

            line_argument_ruler = merged_staff_arguments.group(argument_name)
            if line_argument_ruler.len() > 0 and line_argument_ruler.list()[0]['line'] != None and \
                    line_argument_ruler.list()[0]['lines'][line_argument_ruler.list()[0]['line']] != None:
                
                line_argument_value = line_argument_ruler.list()[0]['lines'][line_argument_ruler.list()[0]['line']]

            else:
                line_argument_ruler = merged_staff_arguments.group("staff_" + argument_name)
                if line_argument_ruler.len() > 0:
                    line_argument_value = line_argument_ruler.list()[0]['lines'][0]

            return line_argument_value

        def pulse(self, tick):

            # clock triggers staked to be called
            if (self._next_clocked_pulse == tick['pulse']):
                clockedActions = [
                    clockedAction for clockedAction in self._clocked_actions if clockedAction['pulse'] == tick['pulse']
                ].copy() # To enable deletion of the original list while looping

                for clockedAction in clockedActions:
                    action_object = clockedAction['action']
                    action_object.actionTrigger(clockedAction, clockedAction['staff_arguments'], None, tick) # WHERE ACTION IS TRIGGERED
                        
                self._clocked_actions = [
                    clockedAction for clockedAction in self._clocked_actions if clockedAction['pulse'] > tick['pulse']
                ] # Cleans up pass actions
                if (len(self._clocked_actions) > 0): # gets the next pulse to be triggered
                    self._next_clocked_pulse = self._clocked_actions[0]['pulse']
                    for clocked_action in self._clocked_actions:
                        self._next_clocked_pulse = min(self._next_clocked_pulse, clocked_action['pulse'])

            if (self._play_pulse < self._finish_pulse): # plays staff range from start to finish

                position = self._staff.position(pulses=self._play_pulse)
                enabled_arguments_rulers = self._staff.filterList(pulse=self._play_pulse)[0]['arguments']['enabled']
                enabled_actions_rulers = self._staff.filterList(pulse=self._play_pulse)[0]['actions']['enabled']

                if self._staff.pulseRemainders(self._play_pulse)['beat'] == 0 and tick['player'] == self._player:
                    self._staff.printSinglePulse(self._play_pulse, "beat", extra_string=f" ticks: {tick['tick_pulse']}")

                if (enabled_arguments_rulers > 0):
                    
                    pulse_arguments_rulers = self._player.rulers().filter(type='arguments', positions=[position], enabled=True)
                    self._internal_arguments_rulers = (pulse_arguments_rulers + self._internal_arguments_rulers).merge()

                if (enabled_actions_rulers > 0):
                    
                    pulse_actions_rulers = self._player.rulers().filter(type='actions', positions=[position], enabled=True)
                    merged_staff_arguments = (self._external_arguments_rulers + self._internal_arguments_rulers).merge()

                    for triggered_action in pulse_actions_rulers: # single ruler actions
                        for action_line in range(len(triggered_action['lines'])):
                            if (triggered_action['lines'][action_line] != None):
                                triggered_action['line'] = action_line
                                for arguments_ruler in merged_staff_arguments:
                                    arguments_ruler['line'] = action_line + triggered_action['offset'] - arguments_ruler['offset']
                                    if (arguments_ruler['line'] < 0 or not (arguments_ruler['line'] < len(arguments_ruler['lines']))):
                                        arguments_ruler['line'] = None # in case key line is out of range of the triggered action line

                                action_name = triggered_action['lines'][action_line]
                                action_players = self._player.getPlayablePlayers(action_name)
                                for action_player in action_players:
                                    action_player['player'].actionTrigger(triggered_action, merged_staff_arguments, self._staff, tick) # WHERE ACTION IS TRIGGERED

                self._play_pulse += 1

            elif len(self._clocked_actions) == 0:
                self._play_mode = False
                self._play_pulse = self._start_pulse

            return self
        
        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
                pass

    class Clock():
        def __init__(self, player):
            self._player = player
            self._tempo = {}
            self.set()

        def getClockTempo(self):
            return self._tempo

        def getPulseDuration(self, beats_per_minute, pulses_per_beat): # in seconds
            return 60.0 / (pulses_per_beat * beats_per_minute)
        
        def json_dictionnaire(self):
            return {
                    'part': "clock",
                    'class': self.__class__.__name__,
                    'tempo': self._tempo,
                    'pulse_duration': self._pulse_duration
                }
     
        def json_load(self, file_name="clock.json", json_object=None):

            if json_object == None:
                # Opening JSON file
                with open(file_name, 'r') as openfile:
                    # Reading from json file
                    json_object = json.load(openfile)

            for dictionnaire in json_object:
                if dictionnaire['part'] == "clock":
                    self._tempo = dictionnaire['tempo']
                    self._pulse_duration = dictionnaire['pulse_duration']
                    break

            return self

        def json_save(self, file_name="clock.json"):

            clock = [ self.json_dictionnaire() ]

            # Writing to sample.json
            with open(file_name, "w") as outfile:
                json.dump(clock, outfile)

            return self

        def set(self, beats_per_minute=None, steps_per_beat=None, pulses_per_quarter_note=None):

            if self._tempo == {}:
                self._tempo['beats_per_minute'] = beats_per_minute
                if beats_per_minute == None:
                    self._tempo['beats_per_minute'] = 120
                self._tempo['steps_per_beat'] = steps_per_beat
                if steps_per_beat == None:
                    self._tempo['steps_per_beat'] = 4
                self._tempo['pulses_per_quarter_note'] = pulses_per_quarter_note
                if pulses_per_quarter_note == None:
                    self._tempo['pulses_per_quarter_note'] = 24
            else:
                if beats_per_minute != None:
                    self._tempo['beats_per_minute'] = beats_per_minute
                if steps_per_beat != None:
                    self._tempo['steps_per_beat'] = steps_per_beat
                if pulses_per_quarter_note != None:
                    self._tempo['pulses_per_quarter_note'] = pulses_per_quarter_note

            pulses_per_beat = self._tempo['steps_per_beat'] * round(converter_PPQN_PPB(self._tempo['pulses_per_quarter_note']) / self._tempo['steps_per_beat'])
            self._tempo['pulses_per_beat'] = pulses_per_beat
            
            self._pulse_duration = self.getPulseDuration(self._tempo['beats_per_minute'], self._tempo['pulses_per_beat']) # in seconds

        def start(self, non_fast_forward_range_pulses = []): # Where a non fast forward range is set

            self._non_fast_forward_range_pulses = None
            if non_fast_forward_range_pulses != None and non_fast_forward_range_pulses != [] and len(non_fast_forward_range_pulses) == 2:
                self._non_fast_forward_range_pulses = non_fast_forward_range_pulses

            self._tick_pulse = 0
            self._next_pulse = 0
            self._next_pulse_time = time.time()

            self._tick = {'tempo': self._tempo, 'pulse': None, 'clock': self, 'player': self._player, 'fast_forward': False, 'tick_pulse': 0}
            
        def stop(self, FORCE_STOP = False):
            pass

        def tick(self):

            self._tick['tick_pulse'] = self._tick_pulse
            self._tick_pulse += 1

            if not self._next_pulse_time > time.time():

                self._tick['pulse'] = self._next_pulse
                self._tick['fast_forward'] = self._non_fast_forward_range_pulses != None \
                    and (self._non_fast_forward_range_pulses[0] != None and self._next_pulse < self._non_fast_forward_range_pulses[0] \
                    or self._non_fast_forward_range_pulses[1] != None and not self._next_pulse < self._non_fast_forward_range_pulses[1])
            
                if self._tick['fast_forward']:
                    self._next_pulse_time = time.time()
                elif self._next_pulse_time + self._pulse_duration < time.time(): # It has to happen inside pulse duration time window
                    self._next_pulse_time = time.time() + self._pulse_duration
                else:
                    self._next_pulse_time += self._pulse_duration
                    
                self._next_pulse += 1
                self._tick_pulse = 0

            else:
                self._tick['pulse'] = None

            return self._tick

# Player METHODS ###############################################################################################################################

    def add(self, player):

        # get all sub-players of player | self can't be on them or a infinite loop happens!!
        player_sub_players = player.get_all_lower_groups().unique()
        not_present_self_player = True
        for sub_player in player_sub_players:
            if sub_player['player'] == self:
                not_present_self_player = False
                break

        if not_present_self_player:
            self._lower_group.add(player)
        else:
            print (f"Player {self} already descendent of Player {player}!")

        return self
    
    def finish(self):
        if self._internal_clock:
            self._clock.stop()

    def get_all_lower_groups(self):
        
        lower_group = self.lower_group
        all_lower_groups = lower_group

        if lower_group.len() > 0:
            for player in lower_group:
                all_lower_groups += player['player'].get_all_lower_groups() # + operator already does a copy

        return all_lower_groups # Last LEAF group is an empty group

    def getClock(self):
        return self._clock

    def getFinishPulse(self):
        return self._finish_pulse

    def getPlayablePlayers(self, name):
        return [
            playable_player for playable_player in self._playable_sub_players if playable_player['name'] == name
        ]

    def getStaff(self):
        return self._staff

    def getStartPulse(self):
        return self._start_pulse

    def isPlaying(self):
        is_playing = False
        actions = self._actions[:]
        for action in actions:
            if action.isPlaying():
                is_playing = True
            else:
                self._actions.remove(action)
        return is_playing

    def json_dictionnaire(self):
        return {
                'part': "player",
                'class': self.__class__.__name__,
                'name': self._name,
                'description': self._description,
                'resource': None if self._resource == None else self._resource['name'],
                'internal_clock': self._internal_clock,
                'clock': [ self._clock.json_dictionnaire() ],
                'staff': [ self._staff.json_dictionnaire() ]
            }

    def json_load(self, file_name="player.json", json_object=None):

        if json_object == None:
            # Opening JSON file
            with open(file_name, 'r') as openfile:
                # Reading from json file
                json_object = json.load(openfile)

        for dictionnaire in json_object:
            if dictionnaire['part'] == "player":
                self._name = dictionnaire['name']
                self._description = dictionnaire['description']
                self._internal_clock = dictionnaire['internal_clock']

                self._clock.json_load(file_name, dictionnaire['clock'])
                self._staff.json_load(file_name, dictionnaire['staff'])

                break

        return self

    def json_save(self, file_name="player.json"):
        player = [ self.json_dictionnaire() ]
            
        # Writing to sample.json
        with open(file_name, "w") as outfile:
            json.dump(player, outfile)

        return self

    def print(self):

        print("{ class: " + f"{self.__class__.__name__}    name: {self._name}    " + \
              f"description: {trimString(self.description)}    sub-players: {self.lower_group.len()}" + " }")

        return self

    def print_group(self):
        self._lower_group.print()

        return self

    def play(self, start=None, finish=None, enabled_group_players=None):

        self._clocked_players = [
            {'name': self._name, 'player': self}
        ]

        all_enabled_players = self.get_all_lower_groups().filter(enabled=True)
        if enabled_group_players != None:
            all_enabled_players += enabled_group_players
        
        for enabled_player in all_enabled_players:
            clockable_player = {
                'name': enabled_player['name'],
                'player': enabled_player['player']
            }
            if not clockable_player in self._clocked_players:
                self._clocked_players.append(clockable_player)

        for clocked_player in self._clocked_players:
            clocked_player['player']._playable_sub_players = []
            playable_sub_players = clocked_player['player'].get_all_lower_groups().filter(enabled=True)
            for playable_player in playable_sub_players:
                playable_player = {
                    'name': playable_player['name'],
                    'player': playable_player['player']
                }
                if not playable_player in clocked_player['player']._playable_sub_players:
                    clocked_player['player']._playable_sub_players.append(playable_player)

        for player in self._clocked_players:
            player['player'].start()
        
        non_fast_forward_range = [None, None]
        if start != None:
            non_fast_forward_range[0] = self._staff.pulses(start)
        if finish != None:
            non_fast_forward_range[1] = self._staff.pulses(finish)

        # At least one Action needs to be externally triggered
        self._clock.start(non_fast_forward_range)
        tick = self._clock.tick()
        self.actionTrigger(None, self.rulers().empty(), self._staff, tick)

        self._clock.start(non_fast_forward_range)

        still_playing = True
        while still_playing:
            tick = self._clock.tick()
            still_playing = False
            for player in self._clocked_players:
                player['player'].tick(tick)
                if player['player'].isPlaying():
                    still_playing = True
        
        self._clock.stop()
        for player in self._clocked_players:
            player['player'].finish()

        return self

    def rangePulses(self):
        range_pulses = self._staff.playRange()
        start_pulses = self._staff.pulses(range_pulses[0])
        finish_pulses = self._staff.pulses(range_pulses[1])
        return {'start': start_pulses, 'finish': finish_pulses}

    def rulers(self):
        return self._staff.rulers()

    def set(self, name=None, description=None, staff=None):

        if name != None:
            self._name = name
        if description != None:
            self._description = description
        if staff != None:
            self._staff = staff

        return self
    
    def set_tempo(self, tempo=120):
        self._clock.set(beats_per_minute=tempo)
        return self

    def set_staff(self, staff):
        self._staff = staff
        time_signature = self._staff.time_signature()
        self._clock.set(beats_per_minute=None, steps_per_beat=time_signature['steps_per_beat'], pulses_per_quarter_note=time_signature['pulses_per_quarter_note'])

        return self

    def set_time_signature(self, size_measures=None, beats_per_measure=None, steps_per_beat=None, pulses_per_quarter_note=None):
        self._clock.set(beats_per_minute=None, steps_per_beat=steps_per_beat, pulses_per_quarter_note=pulses_per_quarter_note)
        self._staff.set(size_measures, beats_per_measure, steps_per_beat, pulses_per_quarter_note)

    def staff(self):
        return self._staff
    
    def start(self):
        if self._internal_clock:
            self._clock.start()
        return self

    def tempo(self):
        return self._clock.getClockTempo()['beats_per_minute']

    def tick(self, tick):
        if self._internal_clock:
            tick = self._clock.tick()
        if tick['pulse'] != None:
            for action in self._actions:
                action.pulse(tick)

        return self        

    def time_signature(self):
        return self._staff.time_signature()

    def useInternalClock(self, internal_clock=False):
        self._internal_clock = internal_clock

        return self

    ### PLAYER ACTIONS ###

    def actionFactoryMethod(self):
        return self.Action(self) # self. and not Player. because the derived Player class has its own Action (Extended one) !! (DYNAMIC)

    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick): # Factory Method Pattern
        player_action = self.actionFactoryMethod()
        self._actions.append(player_action)
        player_action.external_arguments_rulers = merged_staff_arguments
        player_action.actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
        if triggered_action != None:
            player_action.pulse(tick)

    ### CLASS ###
    
    def __str__(self):
        return self._name

class Trigger(Player):
    
    def __init__(self, name, description="A simple trigger action"):
        super().__init__(name, description) # not self init
        
    class Action(Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
            if staff == None: # CLOCKED TRIGGER
                print("CLOCKED TRIGGERED OFF")
            else: # EXTERNAL TRIGGER
                print("EXTERNALLY TRIGGERED ON")
                self.addClockedAction(
                    {'triggered_action': triggered_action, 'staff_arguments': merged_staff_arguments, 'duration': 16, 'action': self},
                    tick
                )

class PlayerNone(Player):

    def __init__(self):
        super().__init__("None", "Player considered as None!")

        self._none = True

        self._staff = STAFF.StaffNone(self)
        self._lower_group = GROUP.GroupNone()

# GLOBAL CLASS METHODS

def converter_PPQN_PPB(pulses_per_quarter_note=24, steps_per_beat=4): # 4 steps per beat is a constant
    '''Converts Pulses Per Quarter Note into Pulses Per Beat'''
    STEPS_PER_QUARTER_NOTE = 4
    pulses_per_beat = pulses_per_quarter_note * (steps_per_beat / STEPS_PER_QUARTER_NOTE)
    return int(pulses_per_beat)

def trimString(full_string):
    string_maxum_size = 60
    long_string_termination = "…"
    trimmed_string = full_string
    if len(full_string) > string_maxum_size:
        trimmed_string = full_string[:string_maxum_size] + long_string_termination
    return trimmed_string
