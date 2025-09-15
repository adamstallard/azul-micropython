import random

floor_penalties = [0, 1, 2, 4, 6, 8, 11, 14, 14]
num_displays = [0, 0, 5, 7, 9]
colors_lower = ['u', 'y', 'r', 'b', 'w']
colors_upper = ['U', 'Y', 'R', 'B', 'W']

def empty_wall():
    return [['u', 'y', 'r', 'b', 'w'],
            ['w', 'u', 'y', 'r', 'b'],
            ['b', 'w', 'u', 'y', 'r'],
            ['r', 'b', 'w', 'u', 'y'],
            ['y', 'r', 'b', 'w', 'u']]

def empty_lines():
    return ['-',
            '-' * 2,
            '-' * 3,
            '-' * 4,
            '-' * 5]

def pretty_wall_tile(tile):
    if tile.islower():
        return '.' + tile + '.'
    else:
        return '(' + tile + ')'

def wall_row(row):
    return ''.join(map(pretty_wall_tile, row))

def color_counts_string(tiles):
    s = ''
    for c in colors_upper:
        s += c + str(tiles.count(c)) + ' '
    return s

def error(msg):
    if not ai_levels[turn]:
        print(msg)
        input("-----HIT ENTER-----")

def shuffle(items):
    n = len(items)
    for i in range(n - 1, 0, -1):
        j = random.randint(0, i)
        items[i], items[j] = items[j], items[i]

def rjust(text, width):
    return '  ' * (width - len(text)) + text

quitting = False
first_time = True
center = []

while not quitting:
    if first_time:
        settings_ok = False
    else:
        settings_ok = input('Same settings(y/n)? ')[0].lower() != 'n'
    while not settings_ok:
        names = []
        ai_levels = []  # 0 = human
        num_players = int(input('How many players(2,3,4)? '))
        if num_players < 2 or num_players > 4:
            print('There must be 2,3 or 4 players.')
            continue
        for p in range(num_players):
            if input(f'Is player {p + 1} an AI(y/n)? ')[0].lower() != 'n':
                ai_levels.append(int(input('AI level(1-7)? ')))
            else:
                ai_levels.append(0)  # human

            names.append(input(f"Player {p + 1}'s name? "))

        factory = [[] for _ in range(num_displays[num_players])]

        settings_ok = True

    # Reset game

    scores = []
    walls = []
    lines = []
    floors = []
    bonuses = []
    bag = list('U' * 20 + 'Y' * 20 + 'R' * 20 + 'B' * 20 + 'W' * 20)
    random.seed()
    shuffle(bag)
    lid = []
    first_player = 0
    view = 'factory'

    for _ in range(num_players):
        scores.append(0)
        walls.append(empty_wall())
        lines.append(empty_lines())
        floors.append([])
        bonuses.append([0, 0, 0])

    game_over = False

    while not game_over:

        # Prepare new factory

        center_1P = True
        for display in factory:
            for _ in range(4):
                if len(bag) == 0:
                    bag.extend(lid)
                    shuffle(bag)
                    lid = []
                display.append(bag.pop())
            display.sort()

        # Start a new round

        turn = first_player
        round_over = False

        while not round_over:

            tiles_in_hand = []
            got_from_center = False

            # Snapshot old center and factory in case the turn needs to be rolled back

            old_center = center[:]
            old_factory = []
            for display in factory:
                old_factory.append(display[:])

            # Ai planned line for move
            planned_line = False

            turn_over = False

            while not turn_over:
                command = 'none'

                if ai_levels[turn] > 0:
                    # generate a command for an ai player
                    if tiles_in_hand:
                        if planned_line:
                            command = planned_line
                        else:
                            command = str(random.randint(0, 5))
                        planned_line = False  # reset for next move
                    else:
                        if ai_levels[turn] <= 7:  # weak AI chooses display and color randomly
                            display = str(random.randint(0, num_displays[num_players]))
                            if display == '0':
                                display = 'c'
                            command = random.choice(colors_lower) + display
                else:
                    if view == 'factory':
                        for i, f in enumerate(factory):
                            if i in [0, 2, 4, 6] and i < num_displays[num_players] - 1:
                                end = ' '
                            else:
                                end = '\n'
                            print(f"{i + 1}: {''.join(f)}", end=end)
                        print('Center:', '1P' if center_1P else '', color_counts_string(center))
                        print('Lid:', color_counts_string(lid))
                    else:
                        if tiles_in_hand == [] or view != turn:
                            print(f"{names[view]}'s Board. Score: {scores[view]}")
                        else:
                            print(f"Add {''.join(tiles_in_hand)} to line (0-5)")
                        for row, line in enumerate(lines[view]):
                            print(f"{len(line)}: {rjust(line,5)}", wall_row(walls[view][row]))
                        first_player_string = "1P," if (not center_1P and view == first_player) else ""
                        print('Floor: ' + first_player_string + ','.join(floors[view]))

                    command = input(f"{names[turn]}'s turn (h for help)? ").lower()

                    if command[0] == 'h':
                        print("View board: M = My board")
                        print("N,P = Next, Previous board")
                        print("F = Factory view")
                        print("(B-Y)(C,1-9) take tiles")
                        print("Examples: BC, Y1, U2, W4")
                        print("0-5 add tiles to line/floor")
                        print("X = restart turn Q = quit")
                        command = input('What do you want to do? ').lower()

                if command[0] == 'f':
                    view = 'factory'
                elif command[0] == 'm':
                    view = turn
                elif command[0] == 'n':
                    if view == 'factory':
                        view = 0
                    else:
                        view += 1
                        if view >= num_players:
                            view = 0
                elif command[0] == 'p':
                    if view == 'factory':
                        view = num_players - 1
                    else:
                        view -= 1
                        if view < 0:
                            view = num_players - 1
                elif command[0] in ['0', '1', '2', '3', '4', '5']:
                    line = int(command[0]) - 1
                    allowed = False
                    if tiles_in_hand:
                        color = tiles_in_hand[0]
                        if command[0] == '0':  # putting tiles in the floor line is always allowed
                            allowed = True
                        elif color in walls[turn][line]:
                            error(f"You can't play color '{color}' in line {line + 1} because your wall already has a" +
                                  " tile of that color in that row.")
                        else:
                            other_color = False
                            for tile in lines[turn][line]:
                                if tile not in (color, '-'):
                                    other_color = tile
                                    break
                            if other_color:
                                error(f"You can't play color '{color}' in line {line + 1} because it already" +
                                      f" has color '{other_color}' in it.")
                            else:
                                allowed = True
                    else:
                        error("You must get tiles from the factory before you can place them in a line.")
                    if allowed:
                        if center_1P and got_from_center:
                            center_1P = False
                            first_player = turn
                        if command[0] == '0':  # put tiles straight on floor line
                            breakage = tiles_in_hand
                        else:
                            empty_spaces = lines[turn][line].count('-')
                            breakage = [color] * max(len(tiles_in_hand) - empty_spaces, 0)
                            lines[turn][line] = lines[turn][line].replace('-', color, len(tiles_in_hand))

                        floors[turn].extend(breakage)
                        if not center_1P and first_player == turn:
                            max_floor = 6  # The 1p token takes up one slot
                        else:
                            max_floor = 7
                        # Put any tiles that won't fit in the floor line into the lid
                        lid.extend(floors[turn][max_floor:])
                        del floors[turn][max_floor:]

                        turn_over = True
                        turn += 1
                        if turn >= num_players:
                            turn = 0

                elif command[0] == 'x':
                    tiles_in_hand = []
                    center = old_center[:]
                    factory = []
                    for display in old_factory:
                        factory.append(display[:])
                elif command[0] == 'q':
                    turn_over = True
                    round_over = True
                    game_over = True
                    quitting = True
                elif command[0] in ['u', 'y', 'r', 'b', 'w']:
                    if tiles_in_hand:
                        error("You already have tiles in your hand. You can put them back and restart your turn with " +
                              "the 'X' command.")
                        view = turn
                    else:
                        color = command[0].upper()
                        if len(command) > 1:
                            if command[1] == 'c':
                                got_from_center = True
                                while center.count(color) > 0:
                                    center.remove(color)
                                    tiles_in_hand.append(color)
                            else:
                                got_from_center = False
                                display = factory[int(command[1]) - 1]
                                while display.count(color) > 0:
                                    display.remove(color)
                                    tiles_in_hand.append(color)
                                if len(tiles_in_hand) > 0:
                                    center.extend(display)
                                    display.clear()
                            if len(tiles_in_hand) > 0:
                                view = turn
                            else:
                                display_str = 'the center' if got_from_center else f'display {int(command[1])}'
                                error(f"There are no tiles of color '{color}' in {display_str}.")

            if not any(factory) and center == []:
                round_over = True

        # End round

        # Score completed lines

        for player, player_lines in enumerate(lines):
            for row_number, line in enumerate(player_lines):
                if '-' not in line:  # line is full
                    color = line[0]
                    column_number = walls[player][row_number].index(color.lower())
                    walls[player][row_number][column_number] = color
                    lid.extend(line[1:])
                    lines[player][row_number] = '-' * len(line)  # empty the line

                    # Check for 10 bonus
                    color_count = 0
                    for row in walls[player]:
                        if color in row:
                            color_count += 1
                    if color_count == 5:
                        bonuses[player][0] += 1

                    # Score the newly placed tile and check for bonuses
                    vertical_score = 1
                    horizontal_score = 1
                    # Left
                    column = column_number - 1
                    while column >= 0:
                        if walls[player][row_number][column].isupper():
                            horizontal_score += 1
                        else:
                            break
                        column -= 1
                    # Right
                    column = column_number + 1
                    while column < 5:
                        if walls[player][row_number][column].isupper():
                            horizontal_score += 1
                        else:
                            break
                        column += 1
                    # Up
                    row = row_number - 1
                    while row >= 0:
                        if walls[player][row][column_number].isupper():
                            vertical_score += 1
                        else:
                            break
                        row -= 1
                    # Down
                    row = row_number + 1
                    while row < 5:
                        if walls[player][row][column_number].isupper():
                            vertical_score += 1
                        else:
                            break
                        row += 1

                    added_score = 0
                    if vertical_score >= 2:
                        added_score += vertical_score
                    if horizontal_score >= 2:
                        added_score += horizontal_score
                    scores[player] += max(added_score, 1)

                    if vertical_score == 5:
                        bonuses[player][1] += 1

                    if horizontal_score == 5:
                        bonuses[player][2] += 1
                        game_over = True

        # Put floor tiles in lid and score them

        for player, floor in enumerate(floors):
            lid.extend(floor)
            scores[player] -= floor_penalties[len(floor) + (1 if first_player == player else 0)]
            floors[player] = []

    # Add bonuses to scores

    for player, player_bonuses in enumerate(bonuses):
        scores[player] += player_bonuses[0] * 10 + player_bonuses[1] * 7 + player_bonuses[2] * 2

    done_reviewing = False

    while not (done_reviewing or quitting):
        print('Final Scores:')
        for name, score in zip(names, scores):
            print(f"{name} {score}")
        print('(B)oards view')
        print('(N)ew Game / (Q)uit')
        command = input('What do you want to do? ')[0].lower()
        if command == 'n':
            done_reviewing = True
        elif command == 'q':
            quitting = True
        elif command == 'b':
            viewing_boards = True
            view = 0
            while viewing_boards:
                print(f"{names[view]}'s Final Score: {scores[view]}")
                print(f"Bonuses: 10x{bonuses[view][0]} + 7x{bonuses[view][1]} + 2x{bonuses[view][2]}")
                for row in walls[view]:
                    print(wall_row(row))
                command = input('(N)ext (P)rev (F)inal? ')[0].lower()
                if command == 'n':
                    view += 1
                    if view >= num_players:
                        view = 0
                elif command == 'p':
                    view -= 1
                    if view < 0:
                        view = num_players - 1  # last player
                else:
                    viewing_boards = False

    first_time = False
