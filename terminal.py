import contextlib
import logging

import blessed
from uniseg.wrap import tt_wrap


class IO:
    """Wrapper for Blessed to render Reddit"""
    def __init__(self):
        self.terminal = blessed.Terminal()
        print(self.terminal.enter_fullscreen)
        print(self.terminal.clear)

        self.submissions = []         # Raw list of Submission objects
        self.submission_display = []  # Submission information to display(Entire page)

        self.render_buffer = []                    # Content to display on terminal
        self.render_offset = 0                     # Offset to keep track of where in submission_display to render from
        self.render_width = self.terminal.width    # Terminal width
        self.render_height = self.terminal.height  # Terminal height
        self.render_menu_y = []                    # Location of each submission item within submission_display

        self._menu_selected = 0                    # Currently selected menu item

    def set_submissions(self, submissions):
        """Receive submission data and prepare it for rendering."""

        self.submissions = submissions

        for submission_no, submission in enumerate(self.submissions, 1):
            self.submission_display.append(str(submission_no) + '. ' +
                                         str(submission.title) + '\n' +
                                         str(submission.score) + 'pts ' +
                                         str(submission.num_comments) + ' comments by (' +
                                         str(submission.author) + ') - /r/' +
                                         str(submission.subreddit))

        self.__wrap_submissions(2)

    def render_submissions(self):
        """Render subreddit while maintaining key press updates and resizing."""

        # Redo submission display info wrapping if resize is detected.
        if self.render_height != self.terminal.height or self.render_width != self.terminal.width:
            self.render_width = self.terminal.width
            self.render_height = self.terminal.height
            self.__wrap_submissions(2)

        # Adjust the rendering offset if selected menu item is out of bounds of current terminal.
        if self.render_menu_y[self._menu_selected] >= self.render_offset + self.render_height - 1:
            self.render_offset += self.render_height - 1
        elif self.render_menu_y[self._menu_selected] < self.render_offset:
            self.render_offset -= self.render_height - 1
            if self.render_offset < 0:
                self.render_offset = 0

        # Clear terminal
        print(self.terminal.clear)

        # Render buffer content to terminal
        for buffer_no, buffer_line in enumerate(self.render_buffer[self.render_offset:self.render_offset + self.render_height - 1]):
            print(self.terminal.move(buffer_no, 2) + buffer_line)

        # Render cursor.
        print(self.terminal.move(self.render_menu_y[self._menu_selected] - self.render_offset, 0) + '>')

    def __wrap_submissions(self, tab=0):
        """Wrap all strings to fit in current terminal screen size."""
        self.render_menu_y = []
        self.render_buffer = []

        line_no = 0
        for submission_info in self.submission_display:
            self.render_menu_y.append(line_no)
            for line in tt_wrap(submission_info, self.terminal.width - tab):
                self.render_buffer.append(line.rstrip('\n'))
                line_no += 1

    @property
    def selected_menu(self):
        return self._menu_selected

    @selected_menu.setter
    def selected_menu(self, potential_selected_menu):
        if 0 <= potential_selected_menu < len(self.submissions):
            self._menu_selected = potential_selected_menu

    @contextlib.contextmanager
    def setup(self):
        with self.terminal.cbreak(), self.terminal.hidden_cursor():
            yield

    def get_key(self, timeout=1):
        return self.terminal.inkey(timeout=timeout)

    def cleanup(self):
        print(self.terminal.clear)
        print(self.terminal.exit_fullscreen)
