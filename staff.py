class Staff:

    def __init__(self, steps = 0, frames_step = 0, play_range=[]):

        self.ruler_types = ['keys', 'actions']
        self.steps = max(1, steps)
        self.frames_step = max(1, frames_step)
        self.total_sequences = self.steps*self.frames_step # total amount like the len()
        self.play_range = [
            self.position(0), self.position(self.total_sequences)
        ]
        if len(play_range) == 2:
            if self.position_lt(play_range[0], self.play_range[1]):
                self.play_range[0] = play_range[0]
            if self.position_lt(play_range[1], self.play_range[1]) and not self.position_lt(play_range[1], self.play_range[0]):
                self.play_range[1] = play_range[1]

        self.staff_grid = []
        self.generate()

    def generate(self):
        self.staff_grid = []
        for sequence in range(self.total_sequences):
            staff_position = {
                'sequence': sequence,
                'position': self.position(sequence),
                'keys': {'enabled': 0, 'total': 0},
                'actions': {'enabled': 0, 'total': 0}
            }
            self.staff_grid.append(staff_position)
        return self
    
    def signature(self):
        return {'steps': self.steps, 'frames_step': self.frames_step}

    def grid(self, sequence):
        if (len(self.staff_grid) > 0):
            return self.staff_grid[sequence]
        
    def add(self, rulers, enabled_one=1, total_one=1):
        for ruler in rulers:
            sequence = self.sequence(ruler['position'])
            if sequence < self.total_sequences:
                if ruler['on_staff']:
                    if ruler['enabled']:
                        self.staff_grid[sequence][ruler['type']]['enabled'] += enabled_one
                    self.staff_grid[sequence][ruler['type']]['total'] += total_one
        return self

    def remove(self, rulers, enabled_one=-1, total_one=-1):
        return self.add(rulers, enabled_one, total_one)
    
    def enable(self, rulers):
        return self.add(rulers, total_one=0)

    def disable(self, rulers):
        return self.remove(rulers, total_one=0)
    
    def keys(self):
        total_keys = {'enabled': 0, 'total': 0}
        for staff_sequence in self.staff_grid:
            total_keys['enabled'] += staff_sequence['keys']['enabled']
            total_keys['total'] += staff_sequence['keys']['total']
        return total_keys

    def actions(self):
        total_actions = {'enabled': 0, 'total': 0}
        for staff_sequence in self.staff_grid:
            total_actions['enabled'] += staff_sequence['actions']['enabled']
            total_actions['total'] += staff_sequence['actions']['total']
        return total_actions

    def position(self, sequence):
        steps = int(sequence / self.frames_step)
        frames = sequence % self.frames_step
        if sequence < 0:
            frames = -(-sequence % self.frames_step)
        return [steps, frames]
    
    def sequence(self, position):
        return position[0] * self.frames_step + position[1]
    
    def len(self):
        return self.total_sequences
    
    def range(self):
        return self.play_range

    def clear(self):
        for staff_position in self.staff_grid:
            staff_position['keys'] = 0
            staff_position['actions'] = 0
        return self

    def print(self):
        if len(self.staff_grid) > 0:
            for staff_position in self.staff_grid:
                print(staff_position)
        else:
            print("[EMPTY]")
        print("\n")
        
    def position_gt(self, left_position, right_position):
        if len(left_position) == 2 and len(right_position) == 2:
            if (left_position[0] > right_position[0]):
                return True
            if (left_position[0] == right_position[0]):
                if (left_position[1] > right_position[1]):
                    return True
        return False

    def position_lt(self, left_position, right_position):
        if len(left_position) == 2 and len(right_position) == 2:
            if (left_position[0] < right_position[0]):
                return True
            if (left_position[0] == right_position[0]):
                if (left_position[1] < right_position[1]):
                    return True
        return False

    def str_position(self, position):
        return str(position[0]) + "." + str(position[1])