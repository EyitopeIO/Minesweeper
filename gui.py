"""
Today:      27-APR-2022
"""

import tkinter
import json
import tkinter.messagebox
from tkinter import ttk
import everything


class Cell(ttk.Button):
    """ Represents the location of a mine or player input
    """
    def __init__(self, parent,  row, col, text, command=None, style=None):
        super().__init__(parent, text=text, command=command, style=style)
        self.row = row
        self.col = col
        self.is_visited = False
        self.is_flagged = False

    def flag_cell(self, event):
        if event.num == 3:      # ttk number for right-click
            self.is_flagged = not self.is_flagged
            # print(f"({self.row},{self.col}) flagged")
            if self.is_flagged:
                self.configure(style="yellow.TButton")
            else:
                self.configure(style=f"white.TButton")


class StatsArea(ttk.Frame):

    def __init__(self, tkinter_root, padding):

        super().__init__(tkinter_root, padding=padding)

        self.mines_selected = ttk.Label(self, padding=padding, text=' ')
        self.difficulty_info = ttk.Label(self, padding=padding, text=' ')

        self.mines_selected.configure(justify=tkinter.CENTER)
        self.difficulty_info.configure(justify=tkinter.CENTER)

    def update_stats(self, info, text):
        if info == 'difficulty':
            self.difficulty_info.configure(text=f'Difficulty: {text}')
        elif info == 'selected':
            self.mines_selected.configure(text=f'Cells clicked: {text}')

    def grid(self, row, col):
        super().grid(row=row, column=col)
        self.mines_selected.pack(side='top')
        self.difficulty_info.pack(side='bottom')


class ButtonArea(ttk.Frame):

    def __init__(self, tkinter_root_frame, padding):
        super().__init__(tkinter_root_frame, padding=padding)


class MenuArea:

    def __init__(self, root_menu):

        self.boardsizeMenu = tkinter.Menu(root_menu)
        self.levelMenu = tkinter.Menu(root_menu)
        self.gamedata = tkinter.Menu(root_menu)

        # Configure difficulty menu
        self.levelMenu.add_command(label="Easy", command=lambda: everything.set_menu_selection('l:easy'))
        self.levelMenu.add_command(label="Medium", command=lambda: everything.set_menu_selection('l:medium'))
        self.levelMenu.add_command(label="Pro", command=lambda: everything.set_menu_selection('l:hard'))

        # Configure board size menu
        self.boardsizeMenu.add_command(label="9 by 9", command=lambda: everything.set_menu_selection("s:9"))
        self.boardsizeMenu.add_command(label="12 by 12", command=lambda: everything.set_menu_selection("s:12"))
        self.boardsizeMenu.add_command(label="15 by 15", command=lambda: everything.set_menu_selection("s:15"))

        # Display the menu
        root_menu.add_command(label="New game", command=everything.clean_game_data)
        root_menu.add_cascade(label="Difficulty", menu=self.levelMenu)
        root_menu.add_cascade(label="Board size", menu=self.boardsizeMenu)

        # Menu to save and load game data
        self.gamedata.add_command(label="Save", command=save_game_data)
        self.gamedata.add_command(label="Load", command=everything.load_game_data)
        root_menu.add_cascade(label="Game", menu=self.gamedata)


def create_all_buttons():
    style = ttk.Style()
    style.configure(f"yellow.TButton", background='yellow')     # Create style for yellow background
    style.configure(f"white.TButton", background='white')
    everything.list_of_cells.extend([[None for _ in range(everything.nrows)] for _ in range(everything.ncols)])
    for r in range(everything.nrows):
        for c in range(everything.ncols):
            t = Cell(everything.button_area, r, c, ' ')
            everything.list_of_cells[r][c] = t
            t.grid_configure(row=r, column=c)
            t.configure(command=game_main_logic, width=4, style="white.TButton")    # Set initial
            t.bind('<Button-3>', t.flag_cell)   # right click


def game_main_logic():

    everything.player_input = everything.button_area.focus_get()
    everything.val[0] = everything.player_input.row
    everything.val[1] = everything.player_input.col

    if not everything.list_of_cells[everything.player_input.row][everything.player_input.col].is_visited:
        everything.list_of_cells[everything.player_input.row][everything.player_input.col].is_visited = True
        everything.nselect += 1

    everything.stats_area.update_stats('difficulty', everything.difficulty_level)
    everything.stats_area.update_stats('selected', everything.nselect)

    # Get row and column number
    r = everything.val[0] - 1
    col = everything.val[1] - 1

    # Unflag the cell if already flagged
    if [r, col] in everything.flags:
        everything.flags.remove([r, col])

    # If landing on a mine --- GAME OVER
    if everything.numbers[r][col] == -1:
        everything.mine_values[r][col] = 'M'
        everything.player_input.configure(text='M')
        everything.show_mines()
        tkinter.messagebox.showinfo("MINESWEEPER", "Landed on a mine. GAME OVER!!!")
        everything.clean_game_data()
        everything.over = True
        return

    # If landing on a cell with 0 mines in neighboring cells
    elif everything.numbers[r][col] == 0:
        vis = []
        everything.mine_values[r][col] = '0'
        everything.player_input.configure(text=everything.mine_values[r][col])
        everything.neighbours(r, col)

    # If selecting a cell with atleast 1 mine in neighboring cells
    else:
        everything.player_input.configure(text=str(everything.numbers[r][col]))
        everything.mine_values[r][col] = everything.numbers[r][col]

    # Check for game completion
    if (everything.check_over()):
        everything.show_mines()
        everything.over = True
        tkinter.messagebox.showinfo("MINESWEEPER", "Congratulations!!! YOU WIN")
        return


def save_game_data():
    if everything.over:
        return
    everything.game_data['val'] = everything.val
    everything.game_data['vis'] = everything.vis
    everything.game_data['flags'] = everything.flags
    everything.game_data['difficuly_level'] = everything.difficulty_level
    everything.game_data['list_of_cells'] = list()
    for row in everything.list_of_cells:
        for cell in row:
            tmp = [cell.row, cell.col, cell.is_visited, cell.is_flagged]
            everything.game_data['list_of_cells'].append(tmp)
    everything.game_data['nselect'] = everything.nselect
    everything.game_data['nrows'] = everything.nrows
    everything.game_data['ncols'] = everything.ncols
    everything.game_data['mines_no'] = everything.mines_no

    with open(everything.game_data_file, "w") as foo:
        foo.write(json.dumps(everything.game_data))

    tkinter.messagebox.showinfo("MINESWEEPER", "Game saved.")


def launch_gui():

    # False elsewhere except in set_menu-whatever

    everything.program_exit = True
    everything.tkinter_loop = tkinter.Tk()
    everything.main_menu = tkinter.Menu(everything.tkinter_loop)
    everything.menu_kids = MenuArea(everything.main_menu)
    everything.tkinter_loop.config(menu=everything.main_menu)
    everything.tkinter_loop.title("MINESWEEPER")
    everything.clean_game_data()
    everything.initialise_game_data()
    everything.button_area = ButtonArea(everything.tkinter_loop, padding=10)
    everything.button_area.grid(row=0, column=0)
    create_all_buttons()
    everything.stats_area = StatsArea(everything.tkinter_loop, 10)
    # everything.stats_info = StatsInfo(everything.stats_area, 10)
    everything.stats_area.update_stats('difficulty', everything.difficulty_level)
    everything.stats_area.update_stats('selected', everything.nselect)
    everything.stats_area.grid(row=1, col=0)
    try:
        everything.tkinter_loop.resizable(0, 0)
        everything.tkinter_loop.mainloop()
    except AttributeError:  # everything.tkinter_loop becomes None on exit
        pass
    print("")
    return everything.program_exit
