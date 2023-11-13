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
import action as Action

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
            player_action = Action.Action(self)
            self._actions.append(player_action)
            player_action.actionTrigger(triggered_action, merged_staff_arguments, staff, tick)

    ### CLASS ###
    
    def __str__(self):
        # return self.__class__.__name__
        return self._name


class Trigger(Player):
    
    def __init__(self, name):
        super().__init__(name, beats_per_minute=120, size_measures=4) # not self init
        
    def actionTrigger(self, triggered_action, merged_staff_arguments, staff, tick): # Factory Method Pattern
        if staff != self._staff or triggered_action == None:
            player_action = Action.Triggered(self)
            self._actions.append(player_action)
            player_action.actionTrigger(triggered_action, merged_staff_arguments, staff, tick)
