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

        # SETS AND AUTOMATIONS
        self._set_auto_parameter_values = []
        self._actions = []

    def __del__(self):
        self.discard_resource()

    #region Player Properties

    @property
    def enabled(self):
        self_player_data = self._stage.filter(player = self).list()[0]
        return self_player_data['enabled']

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
            
    @property
    def set_auto_parameter_values(self):
        return self._set_auto_parameter_values

    #endregion

    class Action():

        def __init__(self, player, trigger_player):

            self._player = player
            self._staff = self._player.getStaff()
            self._trigger_player = trigger_player

            self._internal_arguments_rulers = self._player.rulers().empty()
            self._external_arguments_rulers = self._player.rulers().empty()

            self._play_mode = True # By default whenever a new Action is created is considered in play mode
            self._start_pulse = self._player.rangePulses()['start']
            self._finish_pulse = self._player.rangePulses()['finish']
            self._play_pulse = self._start_pulse

            self._clocked_actions = []      # clocked actions list
            self._next_clocked_pulse = -1   # next programmed pulse on clocked actions list
            self._next_clock_pulse = -1     # next expected pulse from Clock

            self._total_ticks = 0
            self._min_ticks = 100000 * 100000

        #region Action Properties

        @property
        def player(self):
            return self._player
    
        @property
        def trigger_player(self):
            return self._trigger_player
    
        # a getter function 
        @property
        def play_mode(self):
            return self._play_mode
    
        # a setter function (requires previous @property decorator)
        @play_mode.setter 
        def play_mode(self, mode):
            self._play_mode = mode

        @property
        def set_auto_ruler_values(self):
            
            for set_automation in self._player.set_auto_parameter_values:
                if set_automation['trigger_player'] == self._trigger_player:
                    return set_automation['set_auto_ruler_values']
                
            trigger_player_set_automation = {
                    'trigger_player': self._trigger_player,
                    'set_auto_ruler_values': {},
                    'parameters_ruler_values': {}
                }
            self.player.set_auto_parameter_values.append(trigger_player_set_automation)
  
            return trigger_player_set_automation['set_auto_ruler_values']
        
        @property
        def parameters_ruler_values(self):
            
            for set_automation in self._player.set_auto_parameter_values:
                if set_automation['trigger_player'] == self._trigger_player:
                    return set_automation['parameters_ruler_values']
                
            trigger_player_set_automation = {
                    'trigger_player': self._trigger_player,
                    'set_auto_ruler_values': {},
                    'parameters_ruler_values': {}
                }
            self.player.set_auto_parameter_values.append(trigger_player_set_automation)
  
            return trigger_player_set_automation['parameters_ruler_values']
        
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

        #endregion

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

        def pulseSetAutomations(self, tick):
            if tick['pulse'] == self._next_clock_pulse: # avoids repeated processed pulses for any single pulse
                self.automationUpdater(tick)

        def pulseClockedAction(self, tick):

            if tick['pulse'] == self._next_clock_pulse: # avoids repeated processed pulses for any single pulse

                if len(self._clocked_actions) > 0:

                    # clocked triggers staked to be called
                    maximum_while_loops = 100
                    while (self._next_clocked_pulse == tick['pulse'] and maximum_while_loops > 0):
                        clockedActions = [
                            clockedAction for clockedAction in self._clocked_actions if clockedAction['pulse'] == tick['pulse']
                        ] # New list enables deletion of the original list while looping

                        for clockedAction in clockedActions:
                            clockedAction['action'].clockedTrigger(clockedAction, clockedAction['staff_arguments'], tick) # WHERE ACTION IS TRIGGERED
                            self._clocked_actions.remove(clockedAction)
                                
                        if (len(self._clocked_actions) > 0): # gets the next pulse to be triggered
                            self._next_clocked_pulse = self._clocked_actions[0]['pulse']
                            for clocked_action in self._clocked_actions:
                                self._next_clocked_pulse = min(self._next_clocked_pulse, clocked_action['pulse'])
                        else:
                            self._next_clocked_pulse = -1

                        maximum_while_loops -= 1

        def pulseStaffAction(self, tick, first_pulse=False):

            if first_pulse:
                self._next_clock_pulse = tick['pulse']

            if tick['pulse'] == self._next_clock_pulse: # avoids repeated processed pulses for any single pulse

                if (self._play_pulse < self._finish_pulse): # plays staff range from start to finish

                    position = self._staff.position(pulses=self._play_pulse)

                    self._total_ticks += tick['pulse_ticks']
                    self._min_ticks = min(self._min_ticks, tick['pulse_ticks'])
                    if self._staff.pulseRemainders(self._play_pulse)['beat'] == 0 and tick['player'] == self._player:
                        self._staff.printSinglePulse(self._play_pulse, "beat", extra_string=f"\ttotal_ticks: {self._total_ticks}\tmin_ticks: {self._min_ticks}")
                        self._total_ticks = 0
                        self._min_ticks = 100000 * 100000

                    pulse_data = self._staff.pulse(pulse=self._play_pulse)
                    if (pulse_data['arguments']['enabled'] > 0):
                        
                        # FEED AUTOMATIONS HERE (NEED EXISTENT ACTIONS)
                        pulse_sets_and_automations_rulers = self._player.sets_and_automations_rulers.filter(positions=[position])
                        if pulse_sets_and_automations_rulers.len() > 0:
                            for pulse_automation_ruler_dict in pulse_sets_and_automations_rulers:

                                player_pulse_sets_and_automations_rulers = STAFF.Staff.Rulers(self._staff, [ pulse_automation_ruler_dict ])
                                pulse_automation_ruler_dict['player'].playerAutomationTrigger(player_pulse_sets_and_automations_rulers, self._staff, tick) # WHERE AUTOMATION IS TRIGGERED

                        pulse_arguments_rulers = self._player.arguments_rulers.filter(positions=[position], enabled=True)
                        self._internal_arguments_rulers = (pulse_arguments_rulers + self._internal_arguments_rulers).merge() # Where internal arguments are merged
                        pulse_reset_arguments_rulers = pulse_arguments_rulers.link_find(".reset").link_name_strip(".reset")
                        self._internal_arguments_rulers = (pulse_reset_arguments_rulers + self._internal_arguments_rulers).merge(merge_none=True) # Where arguments reset rulers are merged

                    if (pulse_data['actions']['enabled'] > 0):
                        
                        pulse_actions_rulers = self._player.actions_rulers.filter(positions=[position], enabled=True)
                        merged_staff_arguments = (self._external_arguments_rulers + self._internal_arguments_rulers).merge() # Where external arguments are merged

                        for triggered_action in pulse_actions_rulers: # single ruler actions
                            player_merged_staff_arguments = merged_staff_arguments.filter(player=triggered_action['player'], enabled=True)
                            for action_line in range(len(triggered_action['lines'])):
                                if (triggered_action['lines'][action_line] != None):
                                    triggered_action['line'] = action_line
                                    for arguments_ruler in player_merged_staff_arguments:
                                        arguments_ruler['line'] = action_line + triggered_action['offset'] - arguments_ruler['offset']
                                        if (arguments_ruler['line'] < 0 or not (arguments_ruler['line'] < len(arguments_ruler['lines']))):
                                            arguments_ruler['line'] = None # in case key line is out of range of the triggered action line

                                    triggered_action['player'].playerActionTrigger(triggered_action, player_merged_staff_arguments, self._staff, tick) # WHERE ACTION IS TRIGGERED

                    self._play_pulse += 1

                elif self.pulseSetAutomationsCleaner() and len(self._clocked_actions) == 0:
                    self._play_mode = False
                    self._play_pulse = self._start_pulse

                self._next_clock_pulse += 1

            return self
        
        def pulseSetAutomationsCleaner(self):
            for parameter, values in self.set_auto_ruler_values.copy().items():
                if not len(values) > 1 or values[1] == None:
                    del self.set_auto_ruler_values[parameter]

            return self.set_auto_ruler_values == {}
        
        ### ACTION ACTIONS ###

        def automationUpdater(self, tick):
            
            for parameter, values in self.set_auto_ruler_values.items():
                start_value = values[0]
                finish_value = values[1]
                distance_pulses = values[2]
                start_pulse = values[3]
                actual_pulse = tick['pulse']
                calculated_value = start_value
                if finish_value != None and \
                    isinstance(start_value, int) or isinstance(start_value, float) and (isinstance(finish_value, int) or isinstance(finish_value, float)):

                    calculated_value = start_value + (finish_value - start_value) * (actual_pulse - start_pulse) / distance_pulses
                    
                self.parameters_ruler_values[parameter] = calculated_value

            return self
       
        def clockedTrigger(self, triggered_action, self_merged_staff_arguments, tick):
            pass
                 
        def actionTrigger(self, triggered_action, self_merged_staff_arguments, staff, tick):
            self._trigger_steps_per_beat = staff.time_signature()['steps_per_beat']
            self._clock_steps_per_beat = tick['tempo']['steps_per_beat']
            self._clock_pulses_per_step = tick['tempo']['pulses_per_beat'] / tick['tempo']['steps_per_beat']
            self._clock_trigger_steps_per_beat_ratio = self._clock_steps_per_beat / self._trigger_steps_per_beat
                      
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
                          'pulse': self._next_pulse, 'clock': self, 'fast_forward': False, 'pulse_ticks': self._pulse_ticks, 'delayed': False, 'overhead': 0}

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
                    self._tick['overhead'] = 1
                    self._next_pulse_time = time.time()
                elif self._next_pulse_time + self._pulse_duration < time.time(): # It has to happen inside pulse duration time window
                    self._tick['delayed'] = True
                    self._tick['overhead'] = 0
                    if self._tick['delayed']:
                        print(f"--------------------- PULSE {self._tick['pulse']} OF PLAYER {self._player}'S CLOCK WAS DELAYED! -----------------------")
                    self._next_pulse_time = time.time() + self._pulse_duration
                else:
                    self._tick['overhead'] = 1 - (time.time() - self._next_pulse_time) / self._pulse_duration
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
            return self._clock.tick(tick) # changes the tick for the internal clock one | WHERE INTERNAL CLOCK IS USED
        return tick

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

        # Assembling of clockable players
        for enabled_player in self._stage:
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
        self.playerActionTrigger(None , self.rulers().empty(), self._staff, tick)

        still_playing = True
        while still_playing:
            tick = self._clock.tick() # where it ticks
            for player in self._clocked_players:
                player_tick = player['player']._tick(tick)
                if player_tick['pulse'] != None:
                    for action in player['player']._actions:
                        action.pulseSetAutomations(player_tick)
            for player in self._clocked_players:
                player_tick = player['player']._tick(tick)
                if player_tick['pulse'] != None:
                    for action in player['player']._actions:
                        action.pulseClockedAction(player_tick)
            for player in self._clocked_players:
                player_tick = player['player']._tick(tick)
                if player_tick['pulse'] != None:
                    for action in player['player']._actions:
                        action.pulseStaffAction(player_tick)
                    player['player'].playerAutomationCleaner(player_tick)
            still_playing = False
            for player in self._clocked_players:
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

    def time_signature(self):
        return self._staff.time_signature()

    def useInternalClock(self, internal_clock=False):
        self._internal_clock = internal_clock

        return self

    #region ### PLAYER ACTIONS ###

    def string_to_value_converter(self, original_value, parameter):
        try:
            return float(original_value)
        except:
            return original_value

    def actionFactoryMethod(self, triggered_action, self_merged_staff_arguments, staff, tick): # Factory Method Pattern
        return self.Action(self, staff.player) # self. and not Player. because the derived Player class has its own Action (Extended one) !! (DYNAMIC)

    def playerActionTrigger(self, triggered_action, self_merged_staff_arguments, staff, tick):
        if self.enabled and staff.player.enabled:
            player_action = self.actionFactoryMethod(triggered_action, self_merged_staff_arguments, staff, tick) # Factory Method Pattern
            if player_action not in self._actions:
                self._actions.append(player_action)
            else:
                player_action.play_mode = True
            player_action.external_arguments_rulers = self_merged_staff_arguments
            player_action.actionTrigger(triggered_action, self_merged_staff_arguments, staff, tick)
            player_action.pulseStaffAction(tick, first_pulse=True) # first pulse on Action, has to be processed
            # apply existing automations, overriding the action defaults if automated or set
            player_action.automationUpdater(tick)

        return self

    def playerAutomationTrigger(self, player_pulse_sets_and_automations_rulers, staff, tick):

        trigger_player_set_automation = {
                'trigger_player': staff.player,
                'set_auto_ruler_values': {},
                'parameters_ruler_values': {},
            }

        new_trigger_player_set_automation = True
        for set_automation in self._set_auto_parameter_values:
            if set_automation['trigger_player'] == staff.player:
                new_trigger_player_set_automation = False
                trigger_player_set_automation = set_automation
                break

        if new_trigger_player_set_automation:
            self._set_auto_parameter_values.append(trigger_player_set_automation)

        for set_auto_ruler in player_pulse_sets_and_automations_rulers:
            link_list = set_auto_ruler['link'].split(".")
            if len(link_list) > 2:
                total_lines = len(set_auto_ruler['lines'])
                ruler_parameter = link_list[1]
                if total_lines > 0: # meaning it's a SET (DOESN'T REQUIRE NUMERIC VALUES)
                    total_arguments = len(set_auto_ruler['lines'][0])
                    if total_arguments > 0:
                        trigger_player_set_automation['set_auto_ruler_values'][ruler_parameter] \
                            = [ self.string_to_value_converter(set_auto_ruler['lines'][0][0], ruler_parameter) ] # OVERWRITES THE EXISTENT AUTO RULER
                        if total_lines == 3: # meaning it's an AUTOMATION (DOES REQUIRE NUMERIC VALUES)
                            set_auto_ruler['lines'][1][0] = self.string_to_value_converter(set_auto_ruler['lines'][1][0], ruler_parameter)
                            trigger_player_set_automation['set_auto_ruler_values'][ruler_parameter].append(set_auto_ruler['lines'][1][0])
                            trigger_player_set_automation['set_auto_ruler_values'][ruler_parameter].append(set_auto_ruler['lines'][2][0])
                            trigger_player_set_automation['set_auto_ruler_values'][ruler_parameter].append(tick['pulse']) # 4th element                      
                    
        return self

    def playerAutomationCleaner(self, tick):

        if tick['overhead'] > 0.5: # avoids unecessary delays

            for set_automation in self.set_auto_parameter_values.copy():

                if set_automation['set_auto_ruler_values'] == {}:

                    found_active_action = False
                    for action in self._actions:
                        if set_automation['trigger_player'] == action.trigger_player:
                            found_active_action = True
                            break

                    if not found_active_action:
                        self.set_auto_parameter_values.remove(set_automation)

    #endregion

    ### CLASS ###
    
    def __str__(self):
        return self._name

class Trigger(Player):
    
    def __init__(self, stage, name, description="A simple trigger action"):
        super().__init__(stage, name, description) # not self init
        
    class Action(Player.Action):
        
        def __init__(self, player, trigger_player):
            super().__init__(player, trigger_player) # not self init

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

    def playerActionTrigger(self, triggered_action, self_merged_staff_arguments, staff, tick):
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
