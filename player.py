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
import staff as Staff

class Player:

    def __init__(self, name, beats_per_minute=120, size_measures=8, beats_per_measure=4, steps_per_beat=4, pulses_per_quarter_note=24,
                 play_range=[[], []], staff=None):

        self._name = name
        self._staff = staff
        if self._staff == None:
            self._staff = Staff.Staff(size_measures, beats_per_measure, steps_per_beat, pulses_per_quarter_note, play_range)
        self._rulers = self._staff.getRulers()

        self._clock = self.Clock(self, beats_per_minute, pulses_per_quarter_note, steps_per_beat)
        self._internal_clock = False

        self._actions = []

    class Action():

        def __init__(self, player):

            self._player = player
            if self._player == None:
                self._player = Player()
            self._staff = self._player.getStaff()

            self._rulers = self._player.getRulers()
            self._internal_arguments_rulers = self._rulers.empty()
            self._external_arguments_rulers = self._rulers.empty()

            self._play_mode = True # By default whenever a new Action is created is considered in play mode
            self._start_pulse = self._player.rangePulses()['start']
            self._finish_pulse = self._player.rangePulses()['finish']
            self._play_pulse = self._start_pulse

            self.clocked_actions = []
            self.next_clocked_pulse = -1

        def addClockedAction(self, clocked_action, tick): # Clocked actions AREN'T rulers!
            if (clocked_action['duration'] != None and clocked_action['action'] != None):
                pulses_duration = clocked_action['duration'] * self._staff.signature()['pulses_per_step'] # Action pulses per step considered
                clocked_action['pulse'] = round(tick['pulse'] + pulses_duration)
                clocked_action['stack_id'] = len(self.clocked_actions)
                self.clocked_actions.append(clocked_action)

                if (not self.next_clocked_pulse < tick['pulse']):
                    self.next_clocked_pulse = min(self.next_clocked_pulse, clocked_action['pulse'])
                else:
                    self.next_clocked_pulse = clocked_action['pulse']

            return self

        def isPlaying(self):
            return self._play_mode

        def pulse(self, tick):

            # clock triggers staked to be called
            if (self.next_clocked_pulse == tick['pulse']):
                clockedActions = [
                    clockedAction for clockedAction in self.clocked_actions if clockedAction['pulse'] == tick['pulse']
                ].copy() # To enable deletion of the original list while looping

                for clockedAction in clockedActions:
                    action_object = clockedAction['action']
                    action_object.actionTrigger(clockedAction, clockedAction['staff_arguments'], None, tick) # WHERE ACTION IS TRIGGERED
                        
                self.clocked_actions = [
                    clockedAction for clockedAction in self.clocked_actions if clockedAction['pulse'] > tick['pulse']
                ] # Cleans up pass actions
                if (len(self.clocked_actions) > 0): # gets the next pulse to be triggered
                    self.next_clocked_pulse = self.clocked_actions[0]['pulse']
                    for clocked_action in self.clocked_actions:
                        self.next_clocked_pulse = min(self.next_clocked_pulse, clocked_action['pulse'])

            if (self._play_pulse < self._finish_pulse): # plays staff range from start to finish

                position = self._staff.position(pulses=self._play_pulse)
                enabled_arguments_rulers = self._staff.filterList(pulse=self._play_pulse)[0]['arguments']['enabled']
                enabled_actions_rulers = self._staff.filterList(pulse=self._play_pulse)[0]['actions']['enabled']

                if self._staff.pulseRemainders(self._play_pulse)['beat'] == 0 and tick['player'] == self._player:
                    self._staff.printSinglePulse(self._play_pulse, "beat", extra_string=f" ticks: {tick['tick_pulse']}")

                if (enabled_arguments_rulers > 0):
                    
                    pulse_arguments_rulers = self._rulers.filter(type='arguments', positions=[position], enabled=True)
                    self._internal_arguments_rulers = (pulse_arguments_rulers + self._internal_arguments_rulers).merge()

                if (enabled_actions_rulers > 0):
                    
                    pulse_actions_rulers = self._rulers.filter(type='actions', positions=[position], enabled=True)
                    merged_staff_arguments = (self._external_arguments_rulers + self._internal_arguments_rulers).merge()

                    for triggered_action in pulse_actions_rulers.list(): # single ruler actions
                        for action_line in range(len(triggered_action['lines'])):
                            if (triggered_action['lines'][action_line] != None):
                                triggered_action['line'] = action_line
                                for arguments_ruler in merged_staff_arguments.list():
                                    arguments_ruler['line'] = action_line + triggered_action['offset'] - arguments_ruler['offset']
                                    if (arguments_ruler['line'] < 0 or not (arguments_ruler['line'] < len(arguments_ruler['lines']))):
                                        arguments_ruler['line'] = None # in case key line is out of range of the triggered action line

                                action_object = triggered_action['lines'][action_line]
                                action_object.actionTrigger(triggered_action, merged_staff_arguments, self._staff, tick) # WHERE ACTION IS TRIGGERED

                self._play_pulse += 1

            elif len(self.clocked_actions) == 0:
                self._play_mode = False
                self._play_pulse = self._start_pulse

            return self
        
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
            self._external_arguments_rulers = self._rulers.empty()

        ### ACTION ACTIONS ###

        def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
                pass

    class Clock():
        def __init__(self, player, beats_per_minute=120, pulses_per_quarter_note = 24, steps_per_beat=4):
            """create an empty observer list"""
            self._player = player
            self.setClock(beats_per_minute, pulses_per_quarter_note, steps_per_beat)

        def getClockTempo(self):
            return self._tempo

        def getPulseDuration(self, beats_per_minute, pulses_per_beat): # in seconds
            return 60.0 / (pulses_per_beat * beats_per_minute)
        
        def setClock(self, beats_per_minute=120, pulses_per_quarter_note = 24, steps_per_beat=4):
            pulses_per_beat = steps_per_beat * round(converter_PPQN_PPB(pulses_per_quarter_note) / steps_per_beat)

            self._tempo = {'beats_per_minute': beats_per_minute, 'steps_per_beat': steps_per_beat, 'pulses_per_quarter_note': pulses_per_quarter_note, \
                        'pulses_per_beat': pulses_per_beat}
            self._pulse_duration = self.getPulseDuration(beats_per_minute, pulses_per_beat) # in seconds

        def start(self, non_fast_forward_range_pulses = []): # Where a non fast forward range is set

            self._non_fast_forward_range_pulses = None
            if non_fast_forward_range_pulses != None and non_fast_forward_range_pulses != [] and len(non_fast_forward_range_pulses) == 2:
                self._non_fast_forward_range_pulses = non_fast_forward_range_pulses

            self._tick_pulse = 0
            self._next_pulse = 0
            self._next_pulse_time = time.time()

            self._tick = {'tempo': self._tempo, 'pulse': None, 'clock': self, 'player': self._player, 'fast_forward': False, 'tick_pulse': 0}
            
        def stop(self, FORCE_STOP = False):
            ...

        def tick(self):

            self._tick['tick_pulse'] = self._tick_pulse
            self._tick_pulse += 1

            if not self._next_pulse_time > time.time():

                self._tick['pulse'] = self._next_pulse
                self._tick['fast_forward'] = self._non_fast_forward_range_pulses != None \
                    and (self._non_fast_forward_range_pulses[0] != None and self._next_pulse < self._non_fast_forward_range_pulses[0] \
                    or self._non_fast_forward_range_pulses[1] != None and not self._next_pulse < self._non_fast_forward_range_pulses[1])
            
                if not self._tick['fast_forward']:
                    self._next_pulse_time += self._pulse_duration
                else:
                    self._next_pulse_time = time.time()
                    
                self._tick_pulse = 0
                self._next_pulse += 1

            else:
                self._tick['pulse'] = None

            return self._tick

# Player METHODS ###############################################################################################################################

    def finish(self):
        if self._internal_clock:
            self._clock.stop()

    def getClock(self):
        return self._clock

    def getFinishPulse(self):
        return self._finish_pulse

    def getRulers(self):
        return self._rulers

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

    def play(self, start=None, finish=None):

        players = [self]
        players = self._rulers.list_actions(True, players)

        for player in players:
            player.start()
        
        non_fast_forward_range = [None, None]
        if start != None:
            non_fast_forward_range[0] = self._staff.pulses(start)
        if finish != None:
            non_fast_forward_range[1] = self._staff.pulses(finish)

        # At least one Action needs to be externally triggered
        self._clock.start(non_fast_forward_range)
        tick = self._clock.tick()
        self.actionTrigger(None, self._rulers.empty(), self._staff, tick)

        self._clock.start(non_fast_forward_range)

        still_playing = True
        while still_playing:
            tick = self._clock.tick()
            still_playing = False
            for player in players:
                player.tick(tick)
                if player.isPlaying():
                    still_playing = True
        
        self._clock.stop()
        for player in players:
            player.finish()
        self._play_mode = False

        return self

    def rangePulses(self):
        range_pulses = self._staff.playRange()
        start_pulses = self._staff.pulses(range_pulses[0])
        finish_pulses = self._staff.pulses(range_pulses[1])
        return {'start': start_pulses, 'finish': finish_pulses}

    def rulers(self):
        return self._rulers

    def staff(self):
        return self._staff
    
    def start(self):
        if self._internal_clock:
            self._clock.start()
        return self

    def tick(self, tick):
        if self._internal_clock:
            tick = self._clock.tick()
        if tick['pulse'] != None:
            for action in self._actions:
                action.pulse(tick)

        return self        

    def useInternalClock(self, internal_clock=False):
        self._internal_clock = internal_clock

        return self

    ### PLAYER ACTIONS ###

    def actionFactoryMethod(self):
        return self.Action(self)

    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick): # Factory Method Pattern
        if staff != self._staff or triggered_action == None: # avoids self triggering
            player_action = self.actionFactoryMethod()
            self._actions.append(player_action)
            player_action.external_arguments_rulers = merged_staff_arguments
            player_action.actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
            if triggered_action != None:
                player_action.pulse(tick)

    ### CLASS ###
    
    def __str__(self):
        # return self.__class__.__name__
        return self._name

class Trigger(Player):
    
    def __init__(self, name):
        super().__init__(name, beats_per_minute=120, size_measures=4) # not self init
        
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

def converter_PPQN_PPB(pulses_per_quarter_note=24, steps_per_beat=4): # 4 steps per beat is a constant
    '''Converts Pulses Per Quarter Note into Pulses Per Beat'''
    STEPS_PER_QUARTER_NOTE = 4
    pulses_per_beat = pulses_per_quarter_note * (steps_per_beat / STEPS_PER_QUARTER_NOTE)
    return int(pulses_per_beat)
