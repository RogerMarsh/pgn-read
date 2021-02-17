# _utilities.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Utilities to run a sample module."""

import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import os
import time

from ..core.parser import PGN
from ..core.game import generate_fen_for_position


def read_pgn(filename, game_class=None, size=10000000):
    game_ok_count = 0
    game_not_ok_count = 0
    game_ok_token_count = 0
    game_not_ok_token_count = 0
    games_with_error = []
    last_fen_before_error = []
    error_text = []
    error_game_number = []
    for y in PGN(game_class=game_class
                 ).read_games(open(filename, encoding='iso-8859-1'),
                              size=size):
        if y.state is None:
            game_ok_count += 1
            game_ok_token_count += len(y._text)
        else:
            game_not_ok_count += 1
            game_not_ok_token_count += len(y._text)
            games_with_error.append(y._text[:y.state])
            if y._piece_placement_data:
                last_fen_before_error.append(
                    generate_fen_for_position(
                        y._piece_placement_data.values(),
                        y._active_color,
                        y._castling_availability,
                        y._en_passant_target_square,
                        y._halfmove_clock,
                        y._fullmove_number))
            else:
                last_fen_before_error.append('No FEN')
            error_text.append(y._text[y.state:])
            error_game_number.append(game_ok_count + game_not_ok_count)
    return (game_ok_count,
            game_not_ok_count,
            game_ok_token_count,
            game_not_ok_token_count,
            games_with_error,
            last_fen_before_error,
            error_text,
            error_game_number)


class Main:
    """Select PGN file to process."""

    _START_TEXT = ''.join(
        ('Right-click for menu.\n',
         ))

    def __init__(self, game_class=None, size=10000000, samples_title=''):
        """Build the user interface."""
        self.game_class = game_class
        self.size = size
        root = tkinter.Tk()
        root.wm_title(string=samples_title)
        root.wm_resizable(width=tkinter.FALSE, height=tkinter.TRUE)
        tkinter.ttk.Label(master=root, text='PGN file').grid(row=0, column=0)
        tkinter.ttk.Label(master=root, text='Log').grid(row=1, column=1, pady=5)
        entry = tkinter.ttk.Entry(master=root)
        entry.grid(row=0, column=1, columnspan=2, sticky='ew', pady=5)
        pgn_file = tkinter.StringVar(root, '')
        entry["textvariable"] = pgn_file
        frame = tkinter.ttk.Frame(master=root)
        frame.grid(row=2, column=0, columnspan=4, sticky='nsew')
        root.rowconfigure(2, weight=1)
        text = tkinter.Text(master=frame, wrap=tkinter.WORD)
        scrollbar = tkinter.ttk.Scrollbar(
            master=frame,
            orient=tkinter.VERTICAL,
            command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        text.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.menu = tkinter.Menu(master=frame, tearoff=False)
        self.__menu = self.menu
        self.root = root
        self.text = text
        self.entry = entry
        self.pgn_file = pgn_file
        self.set_menu_and_entry_events(True)
        entry.bind('<ButtonPress-3>', self.show_menu)
        text.bind('<ButtonPress-3>', self.show_menu)
        self.insert_text(self._START_TEXT)
        entry.focus_set()
                
    def insert_text(self, text):
        """Wrap Text widget insert with Enable and Disable state configure."""
        self.text.insert(tkinter.END, text)
                
    def report_action(self, msg):
        self.insert_text('\n')
        self.insert_text(' '.join(msg))
        tkinter.messagebox.showinfo(
            master=self.root,
            message='\n'.join(msg))
                
    def report_error(self, msg):
        self.insert_text('\n')
        self.insert_text(' '.join(msg))
        tkinter.messagebox.showerror(
            master=self.root,
            message='\n'.join(msg))

    def show_menu(self, event=None):
        """Show the popup menu for widget."""
        self.__menu.tk_popup(*event.widget.winfo_pointerxy())
        self.__xy = event.x, event.y
        self.__menu = self.menu

    def select_pgn_file(self, event=None):
        """Select a PGN file."""
        filename = tkinter.filedialog.askopenfilename(
            title='PGN file of Games',
            defaultextension='.pgn',
            filetypes=(('PGN Chess Games', '*.pgn'),))
        if filename:
            self.pgn_file.set(filename)

    def process_pgn_file(self, event=None):
        """Process PGN file."""
        if self.pgn_file.get() == '':
            tkinter.messagebox.showerror(
                master=self.root,
                message='Please select a PGN file.')
            return
        path = self.pgn_file.get()
        if not os.path.exists(path):
            msg = ('Cannot process\n',
                   self.pgn_file.get(),
                   '\nwhich does not exist.',
                   )
            self.report_error(msg)
            return
        if not os.path.isfile(path):
            msg = ('Cannot process\n',
                   self.pgn_file.get(),
                   '\nbecause it is not a file.',
                   )
            self.report_error(msg)
            return
        start = time.process_time()
        goc, gnoc, gotc, gnotc, gwe, lfbe, et, egn = read_pgn(
            path,
            game_class=self.game_class,
            size=self.size)
        end = time.process_time()
        m, s = divmod(round(end - start), 60)
        t = ':'.join((str(m).zfill(2), str(s).zfill(2)))
        self.insert_text('\n')
        self.insert_text(' '.join(('PGN file', os.path.basename(path))))
        self.insert_text('\n')
        self.report_summary(start, end, t, goc, gnoc, gotc, gnotc)
        self.insert_text('\n')
        for c, z in enumerate(zip(gwe, lfbe, et, egn)):
            g, f, e, n = z
            self.insert_text('\n')
            self.insert_text(' '.join(
                ('Game number in file:',
                 str(n),
                 '\t\tNot ok game number:',
                 str(c + 1))))
            self.insert_text('\n')
            self.insert_text(' '.join(g))
            self.insert_text(''.join(('\n', f)))
            self.insert_text('\n')
            self.insert_text(' '.join(e))
            self.insert_text('\n')
        if et:
            self.report_summary(start, end, t, goc, gnoc, gotc, gnotc)
            self.insert_text('\n')
        self.report_action(
            ('PGN file',
             os.path.basename(path),
             'done at',
             time.ctime(),
             ))
        self.insert_text('\n')
        self.pgn_file.set('')

    def report_summary(self, start, end, t, goc, gnoc, gotc, gnotc):
        self.insert_text('\n')
        self.insert_text(' '.join((t, 'time to process file')))
        if end - start < 10:
            self.insert_text('\n')
            self.insert_text(
                ' '.join((str(end - start), 'exact process time in seconds')))
        self.insert_text('\n')
        self.insert_text(' '.join(('Game ok count', str(goc))))
        self.insert_text('\n')
        self.insert_text(' '.join(('Game not ok count', str(gnoc))))
        self.insert_text('\n')
        self.insert_text(' '.join(('Game ok token count', str(gotc))))
        self.insert_text('\n')
        self.insert_text(' '.join(('Game not ok token count', str(gnotc))))

    def set_menu_and_entry_events(self, active):
        """Turn events for opening a URL on if active is True otherwise off."""
        menu = self.menu
        if active:
            menu.add_separator()
            menu.add_command(label='Process PGN File',
                             command=self.process_pgn_file,
                             accelerator='Alt F4')
            menu.add_separator()
            menu.add_command(label='Select PGN File',
                             command=self.select_pgn_file,
                             accelerator='Alt F5')
            menu.add_separator()
        else:
            menu.delete(0, tkinter.END)
        for entry in self.text,:
            self._bind_for_scrolling_only(entry)
        for entry in self.entry, self.text:
            entry.bind('<Alt-KeyPress-F5>',
                       '' if not active else self.select_pgn_file)
            entry.bind('<Alt-KeyPress-F4>',
                       '' if not active else self.process_pgn_file)
            entry.bind('<KeyPress-Return>',
                       '' if not active else self.process_pgn_file)

    def _bind_for_scrolling_only(self, widget):
        widget.bind('<KeyPress>', 'break')
        widget.bind('<Home>', 'return')
        widget.bind('<Left>', 'return')
        widget.bind('<Up>', 'return')
        widget.bind('<Right>', 'return')
        widget.bind('<Down>', 'return')
        widget.bind('<Prior>', 'return')
        widget.bind('<Next>', 'return')
        widget.bind('<End>', 'return')


def main(game_class=None, size=10000000, samples_title=''):
    Main(game_class=game_class,
         size=size,
         samples_title=samples_title).root.mainloop()
