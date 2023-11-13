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

import staff as Staff
import clock as Clock

class Player:

    def __init__(self, name, beats_per_minute=120, size_measures=8, beats_per_measure=4, steps_per_beat=4, pulses_per_quarter_note=24,
                 play_range=[[], []], staff=None):

        self._name = name
        self._staff = staff
        if self._staff == None:
            self._staff = Staff.Staff(size_measures, beats_per_measure, steps_per_beat, pulses_per_quarter_note, play_range)
        self._rulers = self._staff.getRulers()

        self._clock = Clock.Clock(self, beats_per_minute, pulses_per_quarter_note, steps_per_beat)
        self._internal_clock = False

        self._actions = []

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

        # At least one Action needs to be triggered
        self._clock.start(non_fast_forward_range)
        tick = self._clock.tick()
        self.actionTrigger(None, None, self._staff, tick)

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

    ### ACTIONS ###

    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick): # Factory Method Pattern
        if staff != self._staff or triggered_action == None:
            player_action = Action(self)
            self._actions.append(player_action)
            player_action.actionTrigger(triggered_action, merged_staff_arguments, staff, tick)

    ### CLASS ###
    
    def __str__(self):
        # return self.__class__.__name__
        return self._name

class Action():

    def __init__(self, player):

        self._player = player
        if self._player == None:
            self._player = Player()
        self._staff = self._player.getStaff()

        self._rulers = self._player.getRulers()
        self.internal_key_rulers = self._rulers.empty()
        self.external_key_rulers = self._rulers.empty()

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
                    
            for clockedAction in clockedActions:
                del(self.clocked_actions[clockedAction['stack_id']]) # Where the self.clocked_actions are deleted!
            if (len(self.clocked_actions) > 0):
                self.next_clocked_pulse = self.clocked_actions[0]['pulse']
                for clocked_action in self.clocked_actions:
                    self.next_clocked_pulse = min(self.next_clocked_pulse, clocked_action['pulse'])

        if (self._play_pulse < self._finish_pulse): # plays staff range from start to finish

            position = self._staff.position(pulses=self._play_pulse)
            enabled_key_rulers = self._staff.filterList(pulse=self._play_pulse)[0]['arguments']['enabled']
            enabled_action_rulers = self._staff.filterList(pulse=self._play_pulse)[0]['actions']['enabled']

            if self._staff.pulseRemainders(self._play_pulse)['beat'] == 0 and tick['player'] == self._player:
                self._staff.printSinglePulse(self._play_pulse, "beat", extra_string=f" ticks: {tick['tick_pulse']}")

            if (enabled_key_rulers > 0):
                
                pulse_key_rulers = self._rulers.filter(type='arguments', positions=[position], enabled=True)
                self.internal_key_rulers = (pulse_key_rulers + self.internal_key_rulers).merge()

            if (enabled_action_rulers > 0):
                
                pulse_action_rulers = self._rulers.filter(type='actions', positions=[position], enabled=True)
                merged_staff_arguments = (self.external_key_rulers + self.internal_key_rulers).merge()

                for triggered_action in pulse_action_rulers.list(): # single ruler actions
                    for action_line in range(len(triggered_action['lines'])):
                        if (triggered_action['lines'][action_line] != None):
                            triggered_action['line'] = action_line
                            for key_ruler in merged_staff_arguments.list():
                                key_ruler['line'] = action_line + triggered_action['offset'] - key_ruler['offset']
                                if (key_ruler['line'] < 0 or not (key_ruler['line'] < len(key_ruler['lines']))):
                                    key_ruler['line'] = None # in case key line is out of range of the triggered action line

                            action_object = triggered_action['lines'][action_line]
                            action_object.actionTrigger(triggered_action, merged_staff_arguments, self._staff, tick) # WHERE ACTION IS TRIGGERED

            self._play_pulse += 1

        elif self._play_mode:
            future_clocked_actions = False
            for clockedAction in self.clocked_actions:
                if clockedAction['pulse'] > tick['pulse']:
                    future_clocked_actions = True
                    break
            if not future_clocked_actions:
                self._play_mode = False
                self._play_pulse = self._start_pulse

        return self

    ### ACTIONS ###

    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick):
        if staff == None: # CLOCKED TRIGGER 
            ...
        else: # EXTERNAL TRIGGER
            self.external_staff_arguments = merged_staff_arguments # becomes read only, no need to copy

class Trigger(Player):
    
    def __init__(self, name):
        super().__init__(name, beats_per_minute=120, size_measures=4) # not self init
        
    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick): # Factory Method Pattern
        if staff != self._staff or triggered_action == None:
            player_action = Triggered(self)
            self._actions.append(player_action)
            player_action.actionTrigger(triggered_action, merged_staff_arguments, staff, tick)

class Triggered(Action):
    
    def __init__(self, player):
        super().__init__(player) # not self init

    ### ACTIONS ###

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
