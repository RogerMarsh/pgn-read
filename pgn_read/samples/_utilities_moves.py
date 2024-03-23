# _utilities_moves.py
# Copyright 2023 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Utilities to run a sample module for PGNMoveText parser."""

import tkinter
import tkinter.ttk
import tkinter.filedialog
import tkinter.messagebox
import os
import time

from ..core.movetext_parser import PGNMoveText


def read_pgn_count_tag_pairs(filename, game_class=None, size=10000000):
    """Return ok and error counts, and PGN text in error."""
    game_count = 0
    tag_pair_count = 0
    for y in PGNMoveText(game_class=game_class).read_games(
        open(filename, encoding="iso-8859-1"), size=size
    ):
        game_count += 1
        tag_pair_count += len(y.pgn_tags)
    return (
        game_count,
        tag_pair_count,
    )


class _Bindings:
    """A short version of solentware_bind.gui.bindings.Bindings.

    This avoids pgn_read depending on solentware_bind.
    """

    def __init__(self):
        """Initialize the bindings register."""
        self._bindings = {}

    def __del__(self):
        """Destroy any bindings in _bindings."""
        for key, funcid in self._bindings.items():
            try:
                key[0].unbind(key[1], funcid=funcid)
            except tkinter.TclError as exc:
                if str(exc).startswith("bad window path name "):
                    continue
                if str(exc).startswith('can\'t invoke "bind" command: '):
                    continue
                raise
        self._bindings.clear()

    def bind(self, widget, sequence, function=None, add=None):
        """Bind sequence to function for widget and note binding identity.

        If a binding exists for widget for sequence it is destroyed.

        If function is not None a new binding is created and noted.

        """
        key = (widget, sequence)
        if key in self._bindings and add is None:
            widget.unbind(sequence, funcid=self._bindings[key])
            del self._bindings[key]
        if function is not None:
            self._bindings[key] = widget.bind(
                sequence=sequence, func=function, add=add
            )


class Main:
    """Select PGN file to process."""

    _START_TEXT = "".join(("Right-click for menu.\n",))

    def __init__(
        self,
        game_class=None,
        read_function=None,
        labels=None,
        size=10000000,
        samples_title="",
    ):
        """Build the user interface."""
        self._bindings = _Bindings()
        self.game_class = game_class
        self.read_function = read_function
        self.labels = labels
        self.size = size
        root = tkinter.Tk()
        root.wm_title(string=samples_title)
        root.wm_resizable(width=tkinter.FALSE, height=tkinter.TRUE)
        tkinter.ttk.Label(master=root, text="PGN file").grid(row=0, column=0)
        tkinter.ttk.Label(master=root, text="Log").grid(
            row=1, column=1, pady=5
        )
        entry = tkinter.ttk.Entry(master=root)
        entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=5)
        pgn_file = tkinter.StringVar(root, "")
        entry["textvariable"] = pgn_file
        frame = tkinter.ttk.Frame(master=root)
        frame.grid(row=2, column=0, columnspan=4, sticky="nsew")
        root.rowconfigure(2, weight=1)
        text = tkinter.Text(master=frame, wrap=tkinter.WORD)
        scrollbar = tkinter.ttk.Scrollbar(
            master=frame, orient=tkinter.VERTICAL, command=text.yview
        )
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
        self._bindings.bind(entry, "<ButtonPress-3>", function=self.show_menu)
        self._bindings.bind(text, "<ButtonPress-3>", function=self.show_menu)
        self.insert_text(self._START_TEXT)
        entry.focus_set()

    def insert_text(self, text):
        """Wrap Text widget insert with Enable and Disable state configure."""
        self.text.insert(tkinter.END, text)

    def report_action(self, msg):
        """Show dialogue to report an action."""
        self.insert_text("\n")
        self.insert_text(" ".join(msg))
        tkinter.messagebox.showinfo(master=self.root, message="\n".join(msg))

    def report_error(self, msg):
        """Show dialogue to report an error."""
        self.insert_text("\n")
        self.insert_text(" ".join(msg))
        tkinter.messagebox.showerror(master=self.root, message="\n".join(msg))

    def show_menu(self, event=None):
        """Show the popup menu for widget."""
        self.__menu.tk_popup(*event.widget.winfo_pointerxy())
        self.__xy = event.x, event.y
        self.__menu = self.menu

    def select_pgn_file(self, event=None):
        """Select a PGN file."""
        filename = tkinter.filedialog.askopenfilename(
            title="PGN file of Games",
            defaultextension=".pgn",
            filetypes=(("PGN Chess Games", "*.pgn"),),
        )
        if filename:
            self.pgn_file.set(filename)

    def process_pgn_file(self, event=None):
        """Process PGN file."""
        if self.pgn_file.get() == "":
            tkinter.messagebox.showerror(
                master=self.root, message="Please select a PGN file."
            )
            return
        path = self.pgn_file.get()
        if not os.path.exists(path):
            msg = (
                "Cannot process\n",
                self.pgn_file.get(),
                "\nwhich does not exist.",
            )
            self.report_error(msg)
            return
        if not os.path.isfile(path):
            msg = (
                "Cannot process\n",
                self.pgn_file.get(),
                "\nbecause it is not a file.",
            )
            self.report_error(msg)
            return
        start = time.process_time()
        report_items = self.read_function(
            path, game_class=self.game_class, size=self.size
        )
        end = time.process_time()
        m, s = divmod(round(end - start), 60)
        t = ":".join((str(m).zfill(2), str(s).zfill(2)))
        self.insert_text("\n")
        self.insert_text(" ".join(("PGN file", os.path.basename(path))))
        self.insert_text("\n")
        self.report_summary(start, end, t, report_items)
        self.insert_text("\n")
        self.report_action(
            (
                "PGN file",
                os.path.basename(path),
                "done at",
                time.ctime(),
            )
        )
        self.insert_text("\n")
        self.pgn_file.set("")

    def report_summary(self, start, end, t, report_items):
        """Add report summary to application report widget."""
        self.insert_text("\n")
        self.insert_text(" ".join((t, "time to process file")))
        if end - start < 10:
            self.insert_text("\n")
            self.insert_text(
                " ".join((str(end - start), "exact process time in seconds"))
            )
        self.insert_text("\n")
        for label, report in zip(self.labels, report_items):
            self.insert_text("\n")
            self.insert_text(" ".join((label, str(report))))

    def set_menu_and_entry_events(self, active):
        """Turn events for opening a URL on if active is True otherwise off."""
        menu = self.menu
        if active:
            menu.add_separator()
            menu.add_command(
                label="Process PGN File",
                command=self.process_pgn_file,
                accelerator="Alt F4",
            )
            menu.add_separator()
            menu.add_command(
                label="Select PGN File",
                command=self.select_pgn_file,
                accelerator="Alt F5",
            )
            menu.add_separator()
        else:
            menu.delete(0, tkinter.END)
        for entry in (self.text,):
            self._bind_for_scrolling_only(entry)
        for entry in self.entry, self.text:
            self._bindings.bind(
                entry,
                "<Alt-KeyPress-F5>",
                function="" if not active else self.select_pgn_file,
            )
            self._bindings.bind(
                entry,
                "<Alt-KeyPress-F4>",
                function="" if not active else self.process_pgn_file,
            )
            self._bindings.bind(
                entry,
                "<KeyPress-Return>",
                function="" if not active else self.process_pgn_file,
            )

    def _bind_for_scrolling_only(self, widget):
        self._bindings.bind(widget, "<KeyPress>", function=lambda e: "break")
        self._bindings.bind(widget, "<Home>", function=lambda e: None)
        self._bindings.bind(widget, "<Left>", function=lambda e: None)
        self._bindings.bind(widget, "<Up>", function=lambda e: None)
        self._bindings.bind(widget, "<Right>", function=lambda e: None)
        self._bindings.bind(widget, "<Down>", function=lambda e: None)
        self._bindings.bind(widget, "<Prior>", function=lambda e: None)
        self._bindings.bind(widget, "<Next>", function=lambda e: None)
        self._bindings.bind(widget, "<End>", function=lambda e: None)


def main(
    game_class=None,
    read_function=None,
    labels=None,
    size=10000000,
    samples_title="",
):
    """Run sample application."""
    Main(
        game_class=game_class,
        read_function=read_function,
        labels=labels,
        size=size,
        samples_title=samples_title,
    ).root.mainloop()
