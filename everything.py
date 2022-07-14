import os
import random
import json

# Contains the row and column of player selection
val = [0, 0]

# Contains row, column information of visited cells
vis = []

# Redefined to that cell last selected by player
player_input = None

# Redefined to a Menu object
main_menu = None

# Redefined to an object of type MenuArea
menu_kids = None

difficulty_level = 'easy'

# List of all objects of type Cell
list_of_cells = list()

# Shown in the live stats area
live_stats = 'Mines selected %s'

# Number of mines selected
nselect = 0

# Number of rows and columns
nrows = 8
ncols = 8

# Size of grid, assuming they're equal
n = max(nrows, ncols)

# Number of mines
mines_no = int()

# The actual values of the grid
numbers = []

# The apparent values of the grid
mine_values = []

# The positions that have been flagged
flags = []

# Variable for maintaining Game Loop
over = False

# Used to decide whether program should restart or terminate
program_exit = True

# File path to game data.
game_data_file = "C:/Users/Florence/Documents/minesweeper.dat"

# Contains all data before being serialized
game_data = dict()

# Reassigned by Menu widget
user_input_row = str()
user_input_col = str()

# Tkinter/UI objects defined in launch_gui()
button_area = None
stats_area = None
menu_area = None
user_alert_area = None

# Main GUI window
tkinter_loop = None


def load_game_data():
    pass


def show_mines():
    """ Make all mines visible
    """
    global mine_values, numbers
    global n, cells, nrows, ncols

    for r in range(nrows):
        for col in range(ncols):
            if numbers[r][col] == -1:
                mine_values[r][col] = 'M'
                list_of_cells[col][r].configure(text='M')


def neighbours(r, col):
    """ Recursive function to display all zero-valued neighbours
    """
    global mine_values
    global numbers
    global vis, nrows, ncols

    # If the cell already not visited
    if [r, col] not in vis:

        # Mark the cell visited
        vis.append([r, col])

        # If the cell is zero-valued
        if numbers[r][col] == 0:

            # Display it to the user
            mine_values[r][col] = numbers[r][col]
            player_input.configure(text=str(numbers[r][col]))

            # Recursive calls for the neighbouring cells
            if r > 0:
                neighbours(r - 1, col)
            if r < nrows - 1:
                neighbours(r + 1, col)
            if col > 0:
                neighbours(r, col - 1)
            if col < n - 1:
                neighbours(r, col + 1)
            if r > 0 and col > 0:
                neighbours(r - 1, col - 1)
            if r > 0 and col < ncols - 1:
                neighbours(r - 1, col + 1)
            if r < nrows - 1 and col > 0:
                neighbours(r + 1, col - 1)
            if r < nrows - 1 and col < ncols - 1:
                neighbours(r + 1, col + 1)

                # If the cell is not zero-valued
        if numbers[r][col] != 0:
            mine_values[r][col] = numbers[r][col]
            player_input.configure(text=str(numbers[r][col]))


def set_mines():
    """ Function for setting up mines
    """
    global numbers
    global mines_no
    global n

    # Track of number of mines already set up
    count = 0
    while count < mines_no:

        # Random number from all possible grid positions
        val = random.randint(0, n * n - 1)

        # Generating row and column from the number
        r = val // n
        col = val % n

        # Place the mine, if it doesn't already have one
        if numbers[r][col] != -1:
            count = count + 1
            numbers[r][col] = -1


#
def set_values():
    """ Function for setting up the other grid values
    """
    global numbers
    global n

    # Loop for counting each cell value
    for r in range(n):
        for col in range(n):

            # Skip, if it contains a mine
            if numbers[r][col] == -1:
                continue

            # Check up
            if r > 0 and numbers[r - 1][col] == -1:
                numbers[r][col] = numbers[r][col] + 1
            # Check down
            if r < n - 1 and numbers[r + 1][col] == -1:
                numbers[r][col] = numbers[r][col] + 1
            # Check left
            if col > 0 and numbers[r][col - 1] == -1:
                numbers[r][col] = numbers[r][col] + 1
            # Check right
            if col < n - 1 and numbers[r][col + 1] == -1:
                numbers[r][col] = numbers[r][col] + 1
            # Check top-left
            if r > 0 and col > 0 and numbers[r - 1][col - 1] == -1:
                numbers[r][col] = numbers[r][col] + 1
            # Check top-right
            if r > 0 and col < n - 1 and numbers[r - 1][col + 1] == -1:
                numbers[r][col] = numbers[r][col] + 1
            # Check below-left
            if r < n - 1 and col > 0 and numbers[r + 1][col - 1] == -1:
                numbers[r][col] = numbers[r][col] + 1
            # Check below-right
            if r < n - 1 and col < n - 1 and numbers[r + 1][col + 1] == -1:
                numbers[r][col] = numbers[r][col] + 1


def set_menu_selection(selection):
    """ Callback when menu items that require reset is selected
    """
    global difficulty_level
    global nrows, ncols
    global program_exit

    # print("sel:", selection)

    program_exit = False

    selection = selection.split(':')
    if selection[0] == 'l':
        difficulty_level = selection[1]
    if selection[0] == 's':
        ncols = int(selection[1])
        nrows = int(selection[1])

    clean_game_data()


def check_over():
    """ Function to check for completion of the game
    """
    global mine_values
    global n
    global mines_no

    # Count of all numbered values
    count = 0

    # Loop for checking each cell in the grid
    for r in range(n):
        for col in range(n):

            # If cell not empty or flagged
            if mine_values[r][col] != ' ' and mine_values[r][col] != 'F':
                count = count + 1

    # Count comparison
    if count == n * n - mines_no:
        return True
    else:
        return False


def generate_mines_no():
    """ Returns number of mines that should be present in the game
    """

    # TODO: Define difficulty level for medium and hard
    if difficulty_level == 'easy':
        return max(nrows, ncols)
    elif difficulty_level == 'medium':
        return 10
    elif difficulty_level == 'hard':
        return 15
    else:
        return 9    # 8 by 8 grid


def clean_game_data():
    """ Delete/clear game data
    """
    global val, vis, list_of_cells, numbers, mine_values, flags
    global n, mines_no, over, live_stats
    global tkinter_loop
    global player_input
    global program_exit

    if numbers or mine_values or flags or vis:
        tkinter_loop.destroy()
        tkinter_loop = None
        program_exit = False

    val = []
    vis = []
    player_input = None
    list_of_cells = []
    live_stats = 'Mines selected %s'
    n = max(nrows, ncols)
    mines_no = generate_mines_no()
    numbers = []
    mine_values = []
    flags = []
    over = False


def initialise_game_data():
    """ Set game data to initial state
    """
    global val, vis, list_of_cells, numbers, mine_values, flags
    global nselect, nrows, ncols, n, mines_no
    global tkinter_loop
    global player_input
    global live_stats
    global over

    val = [0, 0]
    vis = []
    player_input = None
    list_of_cells = list()
    live_stats = 'Mines selected %s'
    nselect = 0
    # nrows = 8
    # ncols = 8
    n = max(nrows, ncols)
    mines_no = generate_mines_no()
    numbers = [[0 for y in range(nrows)] for x in range(ncols)]
    mine_values = [[' ' for y in range(nrows)] for x in range(ncols)]
    flags = []
    set_mines()
    set_values()
    over = False


