import collections

# define all 46 lines
lines = [ # (start, end, (len, dx, dy))
    ((0,0), (7,0), (8, 1, 0)), # horizontal
    ((0,1), (7,1), (8, 1, 0)),
    ((0,2), (7,2), (8, 1, 0)),
    ((0,3), (7,3), (8, 1, 0)),
    ((0,4), (7,4), (8, 1, 0)),
    ((0,5), (7,5), (8, 1, 0)),
    ((0,6), (7,6), (8, 1, 0)),
    ((0,7), (7,7), (8, 1, 0)),

    ((0,0), (0,7), (8, 0, 1)), # vertical
    ((1,0), (1,7), (8, 0, 1)),
    ((2,0), (2,7), (8, 0, 1)),
    ((3,0), (3,7), (8, 0, 1)),
    ((4,0), (4,7), (8, 0, 1)),
    ((5,0), (5,7), (8, 0, 1)),
    ((6,0), (6,7), (8, 0, 1)),
    ((7,0), (7,7), (8, 0, 1)),

    ((0,0), (0,0), (1, 1, -1)), # diagonal asc
    ((0,1), (1,0), (2, 1, -1)),
    ((0,2), (2,0), (3, 1, -1)),
    ((0,3), (3,0), (4, 1, -1)),
    ((0,4), (4,0), (5, 1, -1)),
    ((0,5), (5,0), (6, 1, -1)),
    ((0,6), (6,0), (7, 1, -1)),
    ((0,7), (7,0), (8, 1, -1)),
    ((1,7), (7,1), (7, 1, -1)),
    ((2,7), (7,2), (6, 1, -1)),
    ((3,7), (7,3), (5, 1, -1)),
    ((4,7), (7,4), (4, 1, -1)),
    ((5,7), (7,5), (3, 1, -1)),
    ((6,7), (7,6), (2, 1, -1)),
    ((7,7), (7,7), (1, 1, -1)),

    ((0,7), (0,7), (1, 1, 1)), # diagonal desc
    ((0,6), (1,7), (2, 1, 1)),
    ((0,5), (2,7), (3, 1, 1)),
    ((0,4), (3,7), (4, 1, 1)),
    ((0,3), (4,7), (5, 1, 1)),
    ((0,2), (5,7), (6, 1, 1)),
    ((0,1), (6,7), (7, 1, 1)),
    ((0,0), (7,7), (8, 1, 1)),
    ((1,0), (7,6), (7, 1, 1)),
    ((2,0), (7,5), (6, 1, 1)),
    ((3,0), (7,4), (5, 1, 1)),
    ((4,0), (7,3), (4, 1, 1)),
    ((5,0), (7,2), (3, 1, 1)),
    ((6,0), (7,1), (2, 1, 1)),
    ((7,0), (7,0), (1, 1, 1)),
]

# initial state
state = [['.' for _ in range(line[2][0])] for line in lines]

# topology
topology = collections.defaultdict(list)
for l, (start, end, lendxdy) in enumerate(lines):
    length, dx, dy = lendxdy
    pos = start
    for idx in range(length):
        topology[pos].append((l, idx))
        pos = (pos[0]+dx, pos[1]+dy)

def place(pos, turn):
    for line, idx in topology[pos]:
        state[line][idx] = turn

place((3,3), 'o')
place((3,4), 'x')
place((4,4), 'o')
place((4,3), 'x')

def get_board(line_from, line_to):
    board = [['.' for i in range(8)] for j in range(8)]
    for i in range(8):
        for j in range(8):
            for (l, idx) in topology[i, j]:
                if line_from <= l < line_to:
                    board[j][i] = state[l][idx]
    return '\n'.join([''.join(row) for row in board])

def calc_pos(l, j):
    start, end, lendxdy = lines[l]
    _, dx, dy = lendxdy
    return (start[0]+j*dx, start[1]+j*dy)


flippers_x = {
    ('...xo...', 5): [4, 5],
}

flippers_o = {
    ('...ox...', 5): [4, 5],

}

def move(pos, turn):
    for l, idx in topology[pos]:
        if turn == 'x':
            flips = flippers_x.get((''.join(state[l]), idx), [])
        else:
            flips = flippers_o.get((''.join(state[l]), idx), [])

        for j in flips:
            state[l][j] = turn

            pos2 = calc_pos(l, j)
            for l2, idx2 in topology[pos2]:
                state[l2][idx2] = turn

def check_board():
    a = get_board(0, 8)
    print(a)
    print()
    b = get_board(8, 16)
    c = get_board(16, 31)
    d = get_board(35, 46)
    assert a == b == c == d
    return a


check_board()
move((5, 4), 'x')
check_board()
move((3, 5), 'o')
check_board()
