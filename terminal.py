import contextlib
import logging
import signal

import blessed

terminal = blessed.Terminal()

# Key codes
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
    """Wrapper for Blessed to render Reddit"""
    def __init__(self):
        self.pages = []          # List of all Page-related objects generated for session

        self.render_buffer = []  # Immediate content to display on terminal
        self.render_offset = 0   # Offset to keep track of where in submission_display to render from

        # Initialize terminal
        print(terminal.enter_fullscreen)
        print(terminal.clear)
        signal.signal(signal.SIGWINCH, self.on_resize)

    def on_resize(self, *args):
        """Re-perform wrapping of text to accommodate new terminal size."""

        self.render_buffer = self.pages[-1].item_displays_wrapped  # Perform wrapping
        self.render(self.pages[-1])                                # Re-render buffer

    def reset(self):
        """Empty render buffer and repopulate it with current page."""

        self.render_buffer = []
        self.render(self.pages[-1])

    def render(self, page):
        """Render subreddit while maintaining key press updates and resizing."""

        # Remember terminal size.
        terminal_width = terminal.width
        terminal_height = terminal.height - 1

        # Do not render if no items exist in page yet.
        if not page.items:
            return

        # Fill buffer with content if empty.
        if not self.render_buffer:
            self.render_buffer = page.item_displays_wrapped

        # Adjust the rendering offset if selected menu item is out of bounds of current terminal.
        if page.item_displays_wrapped_locs[page.item_selected] >= self.render_offset + terminal_height:
            self.render_offset += terminal_height
        elif page.item_displays_wrapped_locs[page.item_selected] < self.render_offset:
            self.render_offset -= terminal_height
            if self.render_offset < 0:
                self.render_offset = 0

        # Render buffer content to terminal
        for buffer_line_no in range(terminal_height):
            try:
                buffer_line = self.render_buffer[self.render_offset + buffer_line_no]
                print(terminal.move(buffer_line_no, 0) + buffer_line)
            except IndexError:
                # Print blank line in case buffer is empty
                print(terminal.move(buffer_line_no, 0) + ' ' * terminal_width)

        # Render cursor.
        cursor = '>'
        try:
            cursor += '-' * (page.item_indentations[page.item_selected] * 4)
        except IndexError:
            pass

        print(terminal.move(page.item_displays_wrapped_locs[page.item_selected] - self.render_offset, 0) + cursor)

    def get_out_of_screen_item_loc_next(self, page):
        """Returns closest item index on next page."""

        new_loc = page.item_displays_wrapped_locs[page.item_selected] + terminal.height
        closest_item_index = self._get_index_closest_val(page.item_displays_wrapped_locs, new_loc)

        return closest_item_index

    def get_out_of_screen_item_loc_prev(self, page):
        """Returns closest item index on previous page."""

        new_loc = page.item_displays_wrapped_locs[page.item_selected] - terminal.height
        closest_item_index = self._get_index_closest_val(page.item_displays_wrapped_locs, new_loc)

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


