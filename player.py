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
import lines_scales as LINES_SCALES

class Player:

    def __init__(self, stage, name, description="A Player of actions based on arguments", resources=None):

        self._stage = stage
        self._name = name
        self._description = description

        self._resources = resources
        if resources == None:
            self._resources = RESOURCES.Resources()
        self._resource = None
        self._resource_name = None
        self._resource_enabled = False

        self._staff = STAFF.Staff(self)
        self._clock = Player.Clock(self)
        self._internal_clock = False

        self._actions = []

    def __del__(self):
        self.discard_resource()

    @property
    def stage(self):
        return self._stage
            
    @property
    def name(self):
        return self._name
            
    @property
    def description(self):
        return self._description
            
    @description.setter
    def description(self, description):
        self._description = description
            
    @description.deleter
    def description(self):
        self._description = None

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
            
    @property
    def is_none(self):
        return (self.__class__ == PlayerNone)

    @property
    def actions(self):
        return self._actions
            
    @property
    def arguments_rulers(self):
        return self._arguments_rulers
            
    @property
    def actions_rulers(self):
        return self._actions_rulers
            
    @property
    def sets_and_automations_rulers(self):
        return self._sets_and_automations_rulers
            
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

            self._clocked_actions = []      # clocked actions list
            self._next_clocked_pulse = -1   # next programmed pulse on clocked actions list
            self._next_clock_pulse = -1     # next expected pulse from Clock

            # SETS AND AUTOMATIONS
            self._automations_ruler_values = {
                # NAMED ARGUMENT TYPES GO HERE LIKE "DURATION" AND "RATE"
            }
            self._sets_ruler_value = {
                # NAMED ARGUMENT TYPES GO HERE LIKE "DURATION" AND "RATE"
            }
            self._set_automation_ruler_value = {
                # NAMED ARGUMENT TYPES GO HERE LIKE "DURATION" AND "RATE"
            }

            self._total_ticks = 0
            self._min_ticks = 100000 * 100000

        # using property decorator 
        
        # a getter function 
        @property
        def play_mode(self):
            return self._play_mode
    
        # a setter function (requires previous @property decorator)
        @play_mode.setter 
        def play_mode(self, mode):
            self._play_mode = mode

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
            if (clocked_action['duration'] != None and not clocked_action['duration'] < 0 and clocked_action['action'] != None):

                clocked_action['pulse'] = round(tick['pulse'] + clocked_action['duration'])
                
                if clocked_action not in self._clocked_actions:
                    self._clocked_actions.append(clocked_action)

                    if (not self._next_clocked_pulse < tick['pulse']):
                        self._next_clocked_pulse = min(self._next_clocked_pulse, clocked_action['pulse'])
                    else:
                        self._next_clocked_pulse = clocked_action['pulse']

            return self

        def isPlaying(self):
            return self._play_mode

        def pickTriggeredLineArgumentValue(self, self_merged_staff_arguments, argument_link, global_argument=False):

            line_argument_value = None
            full_argument_link = self._player.name + "." + argument_link
            line_argument_ruler = self_merged_staff_arguments.link(full_argument_link)

            if line_argument_ruler.len() > 0 and (global_argument or line_argument_ruler.list()[0]['line'] != None):
                
                if global_argument:
                    line_argument_value = line_argument_ruler.list()[0]['lines'][0] # lines[0]
                else:
                    line_argument_value = line_argument_ruler.list()[0]['lines'][line_argument_ruler.list()[0]['line']] # lines['line']

            else:
                line_argument_ruler = self_merged_staff_arguments.link(full_argument_link + ".staff")
                if line_argument_ruler.len() > 0:
                    line_argument_value = line_argument_ruler.list()[0]['lines'][0]

            return line_argument_value

        def pulse(self, tick, first_pulse=False):

            if (self._play_pulse < self._finish_pulse): # plays staff range from start to finish

                if first_pulse:
                    self._next_clock_pulse = tick['pulse']

                if tick['pulse'] == self._next_clock_pulse: # avoids repeated action on a single pulse

                    position = self._staff.position(pulses=self._play_pulse)

                    self._total_ticks += tick['pulse_ticks']
                    self._min_ticks = min(self._min_ticks, tick['pulse_ticks'])
                    if self._staff.pulseRemainders(self._play_pulse)['beat'] == 0 and tick['player'] == self._player:
                        self._staff.printSinglePulse(self._play_pulse, "beat", extra_string=f"\ttotal_ticks: {self._total_ticks}\tmin_ticks: {self._min_ticks}")
                        self._total_ticks = 0
                        self._min_ticks = 100000 * 100000

                    pulse_data = self._staff.pulse(pulse=self._play_pulse)
                    if (pulse_data['arguments']['enabled'] > 0):
                        
                        pulse_arguments_rulers = self._player.arguments_rulers.filter(positions=[position])
                        self._internal_arguments_rulers = (pulse_arguments_rulers + self._internal_arguments_rulers).merge() # Where internal arguments are merged
                        pulse_reset_arguments_rulers = pulse_arguments_rulers.find_link(".reset").link_name_strip(".reset")
                        self._internal_arguments_rulers = (pulse_reset_arguments_rulers + self._internal_arguments_rulers).merge(merge_none=True) # Where arguments reset rulers are merged

                        # FEED AUTOMATIONS HERE
                        pulse_sets_and_automations_rulers = self._player.sets_and_automations_rulers.filter(positions=[position])
                        if pulse_sets_and_automations_rulers.len() > 0:
                            for pulse_automation_ruler_dict in pulse_sets_and_automations_rulers:

                                player_pulse_sets_and_automations_rulers = STAFF.Staff.Rulers(self._staff, [ pulse_automation_ruler_dict ])
                                pulse_automation_ruler_dict['player'].actionTrigger(None, player_pulse_sets_and_automations_rulers, self._staff, tick) # WHERE AUTOMATION IS TRIGGERED

                    if (pulse_data['actions']['enabled'] > 0):
                        
                        pulse_actions_rulers = self._player.actions_rulers.filter(positions=[position])
                        merged_staff_arguments = (self._external_arguments_rulers + self._internal_arguments_rulers).merge() # Where external arguments are merged

                        for triggered_action in pulse_actions_rulers: # single ruler actions
                            player_merged_staff_arguments = merged_staff_arguments.filter(player=triggered_action['player'])
                            for action_line in range(len(triggered_action['lines'])):
                                if (triggered_action['lines'][action_line] != None):
                                    triggered_action['line'] = action_line
                                    for arguments_ruler in player_merged_staff_arguments:
                                        arguments_ruler['line'] = action_line + triggered_action['offset'] - arguments_ruler['offset']
                                        if (arguments_ruler['line'] < 0 or not (arguments_ruler['line'] < len(arguments_ruler['lines']))):
                                            arguments_ruler['line'] = None # in case key line is out of range of the triggered action line

                                    triggered_action['player'].actionTrigger(triggered_action, player_merged_staff_arguments, self._staff, tick) # WHERE ACTION IS TRIGGERED

                    self._play_pulse += 1
                    self._next_clock_pulse += 1

            if len(self._clocked_actions) > 0:

                # clocked triggers staked to be called
                maximum_while_loops = 100
                while (self._next_clocked_pulse == tick['pulse'] and maximum_while_loops > 0):
                    clockedActions = [
                        clockedAction for clockedAction in self._clocked_actions if clockedAction['pulse'] == tick['pulse']
                    ] # New list enables deletion of the original list while looping

                    for clockedAction in clockedActions:
                        clockedAction['action'].actionTrigger(clockedAction, clockedAction['staff_arguments'], None, tick) # WHERE ACTION IS TRIGGERED
                        self._clocked_actions.remove(clockedAction)
                            
                    if (len(self._clocked_actions) > 0): # gets the next pulse to be triggered
                        self._next_clocked_pulse = self._clocked_actions[0]['pulse']
                        for clocked_action in self._clocked_actions:
                            self._next_clocked_pulse = min(self._next_clocked_pulse, clocked_action['pulse'])
                    else:
                        self._next_clocked_pulse = -1

                    maximum_while_loops -= 1

            if not self._play_pulse < self._finish_pulse and len(self._clocked_actions) == 0:
                self._play_mode = False
                self._play_pulse = self._start_pulse

            return self
        
        ### ACTION ACTIONS ###

        def string_to_value_converter(self, original_value, parameter):
            try:
                return float(original_value)
            except:
                return original_value

        def automate_parameters(self, tick):

            future_values_to_automate = False
            for parameter, values in self._automations_ruler_values.copy().items():
                start_value = values[0]
                finish_value = values[1]
                distance_pulses = values[2]
                start_pulse = values[3]
                actual_pulse = tick['pulse']
                if isinstance(start_value, int) or isinstance(start_value, float):
                    calculated_value = start_value
                    if finish_value != None and (isinstance(finish_value, int) or isinstance(finish_value, float)):
                        future_values_to_automate = True
                        calculated_value = start_value + (finish_value - start_value) * (actual_pulse - start_pulse) / distance_pulses
                    else:
                        del self._automations_ruler_values[parameter]
                    self._set_automation_ruler_value[parameter] = calculated_value
                else:
                    del self._automations_ruler_values[parameter]

            return future_values_to_automate

        def actionTrigger(self, triggered_action, self_merged_staff_arguments, staff, tick):
            if staff != None: # EXTERNAL TRIGGER
                self._trigger_steps_per_beat = staff.time_signature()['steps_per_beat']
            self._clock_steps_per_beat = tick['tempo']['steps_per_beat']
            self._clock_pulses_per_step = tick['tempo']['pulses_per_beat'] / tick['tempo']['steps_per_beat']
            self._clock_trigger_steps_per_beat_ratio = self._clock_steps_per_beat / self._trigger_steps_per_beat

            if staff == None: # INTERNAL CLOCKED TRIGGER

                if self.automate_parameters(tick):
                    self.addClockedAction(
                        {'triggered_action': None, 'staff_arguments': None, 'duration': 1, 'action': self},
                        tick # updates at least once per pulse
                    )

            elif triggered_action == None: # EXTERNAL AUTOMATION TRIGGER

                for set_auto_ruler in self_merged_staff_arguments:
                    link_list = set_auto_ruler['link'].split(".")
                    if len(link_list) > 1:
                        total_lines = len(set_auto_ruler['lines'])
                        ruler_parameter = link_list[1]
                        if total_lines == 1: # meaning it's a SET (DOESN'T REQUIRE NUMERIC VALUES)
                            self._sets_ruler_value[ruler_parameter] = set_auto_ruler['lines'][0][0]
                            self._set_automation_ruler_value[ruler_parameter] = self._sets_ruler_value[ruler_parameter] # DIRECT SET OF THE VALUE, NO LINEAR PROJECTION
                            # delete any existent automation
                            del self._automations_ruler_values[ruler_parameter]
                        elif total_lines == 3: # meaning it's an AUTOMATION (DOES REQUIRE NUMERIC VALUES)
                            self._automations_ruler_values[ruler_parameter] = []
                            for line_index in range(2): # only the first 2 lines are dedicated to values
                                set_auto_ruler['lines'][line_index][0] = self.string_to_value_converter(set_auto_ruler['lines'][line_index][0], ruler_parameter)
                                self._automations_ruler_values[ruler_parameter].append(set_auto_ruler['lines'][line_index][0])
                            self._automations_ruler_values[ruler_parameter].append(set_auto_ruler['lines'][2][0])
                            self._automations_ruler_values[ruler_parameter].append(tick['pulse']) # 4th element

                if self.automate_parameters(tick):
                    self.addClockedAction(
                        {'triggered_action': None, 'staff_arguments': None, 'duration': 1, 'action': self},
                        tick # updates at least once per pulse
                    )

            else: # EXTERNAL TRIGGER

                if (not tick['fast_forward']):
                    pass
                else:
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
                    'type': self.__class__.__name__,
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

            return self

        def start(self, non_fast_forward_range_pulses = [], tick = None): # Where a non fast forward range is set

            self._non_fast_forward_range_pulses = None
            if non_fast_forward_range_pulses != None and non_fast_forward_range_pulses != [] and len(non_fast_forward_range_pulses) == 2:
                self._non_fast_forward_range_pulses = non_fast_forward_range_pulses

            self._pulse_ticks = 0
            self._next_pulse = 0
            self._next_pulse_time = time.time()

            self._tick = {'player': self._player, 'tempo': self._tempo,
                          'pulse': self._next_pulse, 'clock': self, 'fast_forward': False, 'pulse_ticks': self._pulse_ticks, 'delayed': False}

            return self._tick
            
        def stop(self, tick = None):
            return self._tick

        def tick(self, tick = None):

            self._tick['pulse_ticks'] = self._pulse_ticks
            self._pulse_ticks += 1

            self._tick['delayed'] = False
            if not self._next_pulse_time > time.time():

                self._tick['pulse'] = self._next_pulse

                if tick != None:
                    self._tick['fast_forward'] = tick['fast_forward']
                else:
                    self._tick['fast_forward'] = self._non_fast_forward_range_pulses != None \
                        and (self._non_fast_forward_range_pulses[0] != None and self._next_pulse < self._non_fast_forward_range_pulses[0] \
                        or self._non_fast_forward_range_pulses[1] != None and not self._next_pulse < self._non_fast_forward_range_pulses[1])
            
                if self._tick['fast_forward']:
                    self._next_pulse_time = time.time()
                elif self._next_pulse_time + self._pulse_duration < time.time(): # It has to happen inside pulse duration time window
                    self._tick['delayed'] = True
                    if self._tick['delayed']:
                        print(f"--------------------- PULSE {self._tick['pulse']} WAS DELAYED! -----------------------")
                    self._next_pulse_time = time.time() + self._pulse_duration
                else:
                    self._next_pulse_time += self._pulse_duration
                    
                self._next_pulse += 1
                self._pulse_ticks = 0

            else:
                self._tick['pulse'] = None

            return self._tick

# Player METHODS ###############################################################################################################################

    def _finish(self, tick):
        if self == tick['player']:
            self._clock.stop()
        elif self._internal_clock and self != tick['player']:
                self._clock.stop(tick)

    def _start(self, tick):
        self._arguments_rulers = self.rulers().filter(type='arguments', enabled=True)
        self._actions_rulers = self.rulers().filter(type='actions', enabled=True)
        self._sets_and_automations_rulers = self._staff.rulers()._allocate_players()._sets_and_automations_rulers_generator()
        if self._internal_clock and self != tick['player']:
            self._clock.start(tick=tick)
        return self

    def _tick(self, tick):
        if self._internal_clock and self != tick['player']:
            tick = self._clock.tick(tick) # changes the tick for the internal clock one | WHERE INTERNAL CLOCK IS USED
        if tick['pulse'] != None:
            for action in self._actions:
                action.pulse(tick)

    def use_resource(self, name=None):
        if self._resources != None and name != self._resource_name:
            self.discard_resource()
            self._resource = self._resources.add(name)
            self._resource_name = name
        return self

    def enable_resource(self):
        if self._resources != None and self._resource != None and not self._resource_enabled:
            self._resources.enable(self._resource)
            self._resource_enabled = True
        return self

    def disable_resource(self):
        if self._resources != None and self._resource != None and self._resource_enabled:
            self._resources.disable(self._resource)
            self._resource_enabled = False
        return self

    def discard_resource(self):
        if self._resources != None and self._resource != None:
            self.disable_resource()
            self._resources.remove(self._resource)
            self._resource = None
            self._resource_name = None
        return self

    def disable(self):
        self._stage.filter(player=self).disable()
        return self

    def enable(self):
        self._stage.filter(player=self).enable()
        return self

    def getClock(self):
        return self._clock

    def getFinishPulse(self):
        return self._finish_pulse

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
                self._actions.remove(action) # removal from action is here
        return is_playing

    def json_dictionnaire(self):
        return {
                'part': "player",
                'type': self.__class__.__name__,
                'name': self._name,
                'description': self._description,
                'resources_type': self._resources.__class__.__name__,
                'resource_name': self._resource_name,
                'resource_enabled': self._resource_enabled,
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

        print("{ type: " + f"{self.__class__.__name__}    name: {self._name}    " + \
              f"description: {trimString(self.description)}    " + \
              f"resources_type: {self._resources.__class__.__name__}    resource_name: {self._resource_name}    resource_enabled: {self._resource_enabled}" + " }")

        return self

    def play(self, start=None, finish=None):

        self_player = {'name': self._name, 'player': self}
        self._clocked_players = [ self_player ]

        all_enabled_players = self._stage.filter(enabled=True)
        
        # Assembling of clockable players
        for enabled_player in all_enabled_players:
            clockable_player = {
                'name': enabled_player['name'],
                'player': enabled_player['player']
            }
            if not clockable_player in self._clocked_players:
                self._clocked_players.append(clockable_player)

        non_fast_forward_range = [None, None]
        if start != None:
            non_fast_forward_range[0] = self._staff.pulses(start)
        if finish != None:
            non_fast_forward_range[1] = self._staff.pulses(finish)

        # Self own Action needs to be triggered in order to generate respective Action
        tick = self._clock.start(non_fast_forward_range)
        for player in self._clocked_players:
            player['player']._start(tick)
        self.actionTrigger({ None }, self.rulers().empty(), self._staff, tick)

        still_playing = True
        while still_playing:
            tick = self._clock.tick() # where it ticks
            still_playing = False
            for player in self._clocked_players:
                player['player']._tick(tick)
                if player['player'].isPlaying():
                    still_playing = True
        
        for player in self._clocked_players:
            player['player']._finish(tick)
        self._clock.stop(tick)

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
    
    def set_tempo(self, tempo=None, pulses_per_quarter_note=None):
        self._clock.set(beats_per_minute=tempo, pulses_per_quarter_note=pulses_per_quarter_note)
        self._staff.set(pulses_per_quarter_note=pulses_per_quarter_note)
        return self

    def set_staff(self, staff):
        self._staff = staff
        time_signature = self._staff.time_signature()
        self._clock.set(beats_per_minute=None, steps_per_beat=time_signature['steps_per_beat'], pulses_per_quarter_note=time_signature['pulses_per_quarter_note'])

        return self

    def set_time_signature(self, size_measures=None, beats_per_measure=None, steps_per_beat=None, pulses_per_quarter_note=None):
        self._clock.set(beats_per_minute=None, steps_per_beat=steps_per_beat, pulses_per_quarter_note=pulses_per_quarter_note)
        self._staff.set(size_measures, beats_per_measure, steps_per_beat, pulses_per_quarter_note)

        return self

    def staff(self):
        return self._staff
    
    def tempo(self):
        return self._clock.getClockTempo()['beats_per_minute']

        return self        

    def time_signature(self):
        return self._staff.time_signature()

    def useInternalClock(self, internal_clock=False):
        self._internal_clock = internal_clock

        return self

    ### PLAYER ACTIONS ###

    def actionFactoryMethod(self, triggered_action, self_merged_staff_arguments, staff, tick): # Factory Method Pattern
        return self.Action(self) # self. and not Player. because the derived Player class has its own Action (Extended one) !! (DYNAMIC)

    def actionTrigger(self, triggered_action, self_merged_staff_arguments, staff, tick):
        player_action = self.actionFactoryMethod(triggered_action, self_merged_staff_arguments, staff, tick) # Factory Method Pattern
        if player_action not in self._actions:
            self._actions.append(player_action)
        else:
            player_action.play_mode = True
        if triggered_action != None:
            player_action.external_arguments_rulers = self_merged_staff_arguments
            player_action.actionTrigger(triggered_action, self_merged_staff_arguments, staff, tick)
            player_action.pulse(tick, first_pulse=True) # first pulse on Action, has to be processed
        else: # for automation ".auto" arguments only!
            for player_action in self._actions:
                player_action.actionTrigger(triggered_action, self_merged_staff_arguments, staff, tick)

        return self

    ### CLASS ###
    
    def __str__(self):
        return self._name

class Trigger(Player):
    
    def __init__(self, stage, name, description="A simple trigger action"):
        super().__init__(stage, name, description) # not self init
        
    class Action(Player.Action):
        
        def __init__(self, player):
            super().__init__(player) # not self init

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, self_merged_staff_arguments, staff, tick):
            super().actionTrigger(triggered_action, self_merged_staff_arguments, staff, tick)
            if staff == None: # CLOCKED TRIGGER
                print("CLOCKED TRIGGERED OFF")
            else: # EXTERNAL TRIGGER
                print("EXTERNALLY TRIGGERED ON")
                self.addClockedAction(
                    {'triggered_action': triggered_action, 'staff_arguments': self_merged_staff_arguments, 'duration': 16, 'action': self},
                    tick
                )

class PlayerNone(Player):

    def __init__(self, stage):
        super().__init__(stage, "None", "Player considered as None!")

        self._resources = RESOURCES.ResourcesNone()
        self._staff = STAFF.StaffNone(self)

    def actionTrigger(self, triggered_action, self_merged_staff_arguments, staff, tick):
        pass # does nothing

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
    if full_string != None and len(full_string) > string_maxum_size:
        trimmed_string = full_string[:string_maxum_size] + long_string_termination
    return trimmed_string
