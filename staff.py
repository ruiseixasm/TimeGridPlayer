class Staff:

    def __init__(self, steps, frames_step, play_range=[]):

        self.ruler_types = ['keys', 'actions']
        self.steps = max(1, steps)
        self.frames_step = max(1, frames_step)
        self.sequences = self.steps*self.frames_step # total amount
        self.play_range = [
            self.position(0), self.position(self.sequences)
        ]
        if len(play_range) == 2:
            if self.position_lt(play_range[0], self.play_range[1]):
                self.play_range[0] = play_range[0]
            if self.position_lt(play_range[1], self.play_range[1]) and not self.position_lt(play_range[1], self.play_range[0]):
                self.play_range[1] = play_range[1]

        self.staff_grid = []
        self.generate()


    def position(self, sequence):
        steps = int(sequence / self.frames_step)
        frames = sequence % self.frames_step
        return [steps, frames]
    
    def sequence(self, position):
        return position[0] * self.frames_step + position[1]
    
    def range(self):
        return self.play_range


    def generate(self):
        self.staff_grid = []
        for sequence in range(self.sequences):
            staff_position = {
                'sequence': sequence,
                'position': self.position(sequence),
                'keys': 0,
                'actions': 0
            }
            self.staff_grid.append(staff_position)
        return self
    
    def clear(self):
        for staff_position in self.staff_grid:
            staff_position['keys'] = 0
            staff_position['actions'] = 0
        return self


    def add(self, rulers):
        for ruler in rulers:
            sequence = self.sequence(ruler['position'])
            if not self.sequences < sequence:
                self.staff_grid[sequence][ruler['type']] += 1
        return self

    def remove(self, rulers):
        for ruler in rulers:
            sequence = self.sequence(ruler['position'])
            if not self.sequences < sequence:
                self.staff_grid[sequence][ruler['type']] -= 1
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

    def position_eq(self, left_position, right_position):
        if len(left_position) == 2 and len(right_position) == 2:
            if (left_position[0] == right_position[0] and left_position[1] == right_position[1]):
                return True
        return False
    