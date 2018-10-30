import curses # curses: python标准库中的一个模块，用来处理命令行中的输入输出
from random import randint, choice
import numpy as np


actions = ["UP", "DOWN", "LEFT", "RIGHT", "RESTART", "EXIT"]
letter_codes = [ord(c) for c in "wsadreWSADRE"] #ord('char') returns the unicode of a char.
actions_dict = dict(zip(letter_codes, actions * 2))

def get_user_action(window):
    char = "N"
    while char not in letter_codes:
        char = window.getch()
    return actions_dict[char]

class GameField(object):
    def __init__(self, width=4, height=4, win=2018):
        self.width = width
        self.height = height
        self.win_value = win
        self.reset()

    def reset(self):
        self.score = 0
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.generate()
        self.generate()

    # randomly generate a 2 or 4 at random place
    def generate(self):
        number = randint(1, 100)
        if number < 80:
            number = 2
        else:
            number = 4

        possible_pos = []
        for row_num in range(self.width):
            for col_num in range(self.height):
                if self.field[row_num][col_num] == 0:
                    possible_pos.append([row_num, col_num])
        print(possible_pos)
        if possible_pos != []:
            pos = choice(possible_pos)
            self.field[ int(pos[0]) ][ int(pos[1]) ] = number


    # draw the chess board whenever it needs to update
    def draw(self, screen):

        intro_string = "Up(W) Down(S) Left(A) Right(D)\n     Restart(R)  Exit(E)"

        def render(string):
            screen.addstr(string) # render a string on the current terminal window

        def draw_horizontal_seperator():
            render("+———————" * self.width + "+" + '\n')


        def draw_vertial_seperator(row_num):
            for num in self.field[row_num]:
                if num == 0:
                    render('|       ')
                else:
                    render('|{: ^7}'.format(num))
            render('|' + '\n')

        screen.clear()

        render("SCORE: " + str(self.score) + '\n')
        for row in range(self.height):
            draw_horizontal_seperator()
            draw_vertial_seperator(row)
        draw_horizontal_seperator()
        render(intro_string)

        screen.refresh()


    def move(self, action):

        def field_rotate_anticlockwise(field, time=1):
            new_field = np.array(field, dtype=np.int32)
            new_field = np.rot90(new_field, time)
            return new_field.tolist()

        def field_reverse(field):
            for row_num in range(len(field)):
                field[row_num] = list(reversed(field[row_num]))
            return field

        def move_one_direction(): # merge to the left by default

            def merge():

                for row_index in range(len(self.field)): # the process of each row
                    merged_row = []
                    index = 0

                    while(index < self.width - 1): # merge everything into merged_row
                        if self.field[row_index][index] == self.field[row_index][index + 1]:
                            merged_row.append(2 * self.field[row_index][index])
                            self.score += 2 * self.field[row_index][index]
                            self.field[row_index][index + 1] = 0
                            index += 1
                        else:
                            merged_row.append(self.field[row_index][index])
                        index += 1

                    merged_row.append(self.field[row_index][self.width - 1])

                    while(len(merged_row) < self.width): # complete merged_row and replace the old row with merged_row
                        merged_row.append(0)
                    self.field[row_index] = merged_row

            def stack(): # stack all the numbers except 0 to one side
                for row_index in range(len(self.field)):
                    stacked_row = []

                    for element in self.field[row_index]:
                        if int(element) != 0:
                            stacked_row.append(element)

                    while(len(stacked_row) < self.width):
                        stacked_row.append(0)

                    self.field[row_index] = stacked_row

            stack()
            merge()


        if action == 'LEFT':
            move_one_direction()

        if action == 'RIGHT':
            self.field = field_reverse(self.field) # reverse
            move_one_direction() # merge and stack
            self.field = field_reverse(self.field) # reverse back

        if action == 'UP':
            self.field = field_rotate_anticlockwise(self.field, 1)
            move_one_direction()
            self.field = field_rotate_anticlockwise(self.field, 3)

        if action == 'DOWN':
            self.field = field_rotate_anticlockwise(self.field, 3)
            move_one_direction()
            self.field = field_rotate_anticlockwise(self.field, 1)



# 状态机：state 存储当前状态，state_actions 这个词典变量作为状态转换的规则，它的 key 是状态，value 是返回下一个状态的函数
def main(stdscr):

    screen = stdscr
    game_field = GameField()

    def init():
        game_field.reset()
        return 'Game'

    def game():
        game_field.draw(screen)
        action = get_user_action(screen)

        def possible_to_move(field):
            def is_full(field):
                full = True
                for row in field:
                    for element in row:
                        if element == 0:
                            full = False
                            break
                return full

            def is_movable(field):
                def horizontal_is_movable(field):
                    movable = False
                    for row_num in range(game_field.height):
                        for col_num in range(game_field.width - 1):
                            if field[row_num][col_num] == field[row_num][col_num + 1]:
                                movable = True
                    return movable

                def field_rotate_anticlockwise(field, time=1):
                    new_field = np.array(field, dtype=np.int32)
                    new_field = np.rot90(new_field, time)
                    return new_field.tolist()

                horizontal_movable = horizontal_is_movable(field)
                field = field_rotate_anticlockwise(field, 1)
                vertical_movable = horizontal_is_movable(field)
                field = field_rotate_anticlockwise(field, 3)

                return horizontal_movable or vertical_movable

            movable = is_movable(field)
            full = is_full(field)
            if full and not movable:
                return False
            else:
                return True

        possible_move = possible_to_move(game_field.field)

        if not possible_move:
            return 'Gameover'

        if action == "RESTART":
            return 'Init'
        elif action == "EXIT":
            return 'Exit'
        else:
            game_field.move(action)
            game_field.generate()
        return 'Game'

    def gameover():
        screen.addstr("\n       You lose.")
        screen.refresh()
        action = get_user_action(screen)
        if action == "RESTART":
            return 'Init'
        elif action == "EXIT":
            return 'Exit'
        else:
            return 'Pause'

    def win():
        pass

    def pause():
        action = get_user_action(screen)
        if action == "RESTART":
            return 'Init'
        elif action == "EXIT":
            return 'Exit'
        else:
            return 'Pause'

    state_actions = {
        'Init': init,
        'Game': game,
        'Gameover': gameover,
        'Win': win,
        'Pause': pause
    }

    state = 'Init'

    while state != 'Exit':
        state = state_actions[state]()

if __name__ == "__main__":
    curses.wrapper(main)
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i, i, -1);


# TODO: redo the move
