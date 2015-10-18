import contextlib
import logging
import signal
import sys

import blessed

terminal = blessed.Terminal()

# Key codes used in application.
KEY_DOWN = 258
KEY_UP = 259
KEY_LEFT = 260
KEY_RIGHT = 261
KEY_BACKSPACE = 330
KEY_PGDN = 338
KEY_PGUP = 339
KEY_ENTER = 343
KEY_ESCAPE = 361


class IO:
    """Handles rendering of Page objects."""

    def __init__(self):
        self.pages = []              # List of all Page-related objects generated for session.
        self.page_current = 0        # Keep track of current(last) page.

        self.render_buffer = []      # Render buffer. Holds entire page to display.
        self.render_offset = 0       # Offset to keep track of where in render buffer to render from.
        self.render_offset_item = 0  # Extra offset to put in account of items which do not fit terminal size.

        self.terminal_width = 0      # Remember terminal width.
        self.terminal_height = 0     # Remember terminal height.

        # Initialize terminal
        print(terminal.enter_fullscreen)
        print(terminal.clear)

        # Init signal for terminal resize event.
        signal.signal(signal.SIGWINCH, self.on_resize)

    def render(self):
        """Render last page while keeping in account of key press updates and resizing."""

        self.page_current = self.pages[-1]

        # Remember terminal size.
        self.terminal_width = terminal.width
        self.terminal_height = terminal.height

        # Do not render if no items exist in page yet.
        if not self.page_current.items:
            return

        # Fill buffer with content if empty.
        if not self.render_buffer:
            sys.stdout.write("\x1b]2;{0}\x07".format(self.page_current.name))

            for line in self.page_current.item_strings_formatted:
                line += terminal.on_black(' ' * (self.terminal_width - terminal.length(line)))
                self.render_buffer.append(line)

        # Adjust the rendering offset if selected menu item is out of bounds of current terminal.
        if self.page_current.item_onscreenlocs[self.page_current.item_selected] >= self.render_offset + self.terminal_height:
            self.render_offset += self.terminal_height
        elif self.page_current.item_onscreenlocs[self.page_current.item_selected] < self.render_offset:
            self.render_offset -= self.terminal_height
            if self.render_offset < 0:
                self.render_offset = 0

        # Render buffer content to terminal
        for buffer_line_no in range(self.terminal_height):
            try:
                buffer_line = self.render_buffer[self.render_offset + self.render_offset_item + buffer_line_no]
                print(terminal.move(buffer_line_no, 0) + buffer_line, end='')
            except IndexError:
                # Print blank line in case buffer is empty
                print(terminal.move(buffer_line_no, 0) + (terminal.on_black(' ' * self.terminal_width)), end='')

        # Render cursor.
        cursor = terminal.white_on_black('>')
        try:
            cursor += terminal.white_on_black('-' * (self.page_current.item_indentations[self.page_current.item_selected] * 4))
        except IndexError:
            pass

        if self.render_offset_item == 0:
            print(terminal.move(self.page_current.item_onscreenlocs[self.page_current.item_selected] - self.render_offset, 0) + cursor)

    def on_resize(self, *args):
        """Re-perform wrapping of text to accommodate new terminal size."""

        self.page_current.width = terminal.width                       # Give page new terminal width
        self.render_buffer = []

        self.render()                                                  # Re-render buffer

    def reset(self):
        """Empty render buffer and repopulate it with current page."""

        self.page_current = self.pages[-1]
        self.page_current.width = terminal.width                       # Give page new terminal width

        self.render_buffer = []
        self.render_offset = 0
        self.render_offset_item = 0

        self.render()

    def _get_distance_betweenitems(self, item_no1, item_no2):
        """Determine distance between 2 items does not fit terminal height"""

        try:
            if item_no1 >= 0 and item_no2 >= 0:
                loc_current = self.page_current.item_onscreenlocs[item_no1]
                loc_potential = self.page_current.item_onscreenlocs[item_no2]
                distance = abs(loc_potential - loc_current)
            else:
                distance = 0

        except IndexError:
            distance = 0

        return distance

    def select_item_next(self):
        """Determine whether to render the next item, or just adjust self.render_offset_item."""

        # If current item fits terminal height choose next item,
        # if not, adjust render_offset_item without selecting new item(Edge case)
        loc_diff = self._get_distance_betweenitems(self.page_current.item_selected, self.page_current.item_selected + 1)
        if loc_diff - self.render_offset_item < self.terminal_height:
            self.page_current.item_selected += 1
            self.render_offset_item = 0
        else:
            self.render_offset_item += self.terminal_height

        self.render()  # TODO Why the render function needs to be called for instant update unknown. Need to look into.

    def select_item_prev(self):
        """Determine whether to render the previous item, or just adjust self.render_offset_item."""

        loc_diff = self._get_distance_betweenitems(self.page_current.item_selected, self.page_current.item_selected - 1)
        if loc_diff + self.render_offset_item < self.terminal_height:
            self.page_current.item_selected -= 1
            self.render_offset_item = 0
        else:
            self.render_offset_item -= self.terminal_height

        self.render()  # TODO Why the render function needs to be called for instant update unknown. Need to look into.

    def select_item_nextscreen(self):
        """pass"""

        self.page_current.item_selected = self._get_out_of_screen_item_loc_next()

    def select_item_prevscreen(self):
        """pass"""

        self.page_current.item_selected = self._get_out_of_screen_item_loc_prev()

    def _get_out_of_screen_item_loc_next(self):
        """Returns closest item index on next page."""

        new_loc = self.page_current.item_onscreenlocs[self.page_current.item_selected] + terminal.height
        closest_item_index = self._get_index_closest_val(self.page_current.item_onscreenlocs, new_loc)

        return closest_item_index

    def _get_out_of_screen_item_loc_prev(self):
        """Returns closest item index on previous page."""

        new_loc = self.page_current.item_onscreenlocs[self.page_current.item_selected] - terminal.height
        closest_item_index = self._get_index_closest_val(self.page_current.item_onscreenlocs, new_loc)

        return closest_item_index

    @staticmethod
    def _get_index_closest_val(list, val):
        """Return index of closest value within list."""

        return min(range(len(list)), key=lambda i: abs(list[i]-val))

    @contextlib.contextmanager
    def setup(self):
        """Set up required terminal modes."""

        try:
            with terminal.cbreak(), terminal.hidden_cursor():
                yield
        finally:
            print(terminal.clear)
            print(terminal.exit_fullscreen)

    @staticmethod
    def get_key(timeout=0):
        """Returns input object."""

        return terminal.inkey(timeout=timeout)
