import contextlib
import logging
import re
import signal
import unicodedata

import blessed
from uniseg.wrap import tt_wrap

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

        # Remember terminal size
        terminal_width = terminal.width
        terminal_height = terminal.height - 1

        # Fill buffer with content if empty
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


class Page:
    """Base class for how items are to be displayed and selected."""

    def __init__(self, items, indent=2):
        self.items = items                    # Items to be displayed on page, such as Submission and Comment objects
        self.item_displays = []               # Actual text to be displayed
        self._item_displays_wrapped = []      # Wrapped version of above
        self.item_displays_wrapped_locs = []  # Index of locations of items in the buffer
        self._item_selected = 0               # Currently selected item
        self.item_indentations = []           # Index of indentation level of items

        self.indent = indent  # Indent page by this value

    @property
    def item_displays_wrapped(self):
        """Process items to display to be wrapped according to current terminal size."""

        # Reset current wrapped item info
        self._item_displays_wrapped = []
        self.item_displays_wrapped_locs = []

        # Remember terminal width
        terminal_width = terminal.width

        # Take each item to display by line, and break it into multiple lines based of current terminal width
        line_no = 0
        for item_no, item_display in enumerate(self.item_displays):
            # Confirm indentation level for each item
            try:
                item_indentation = self.item_indentations[item_no] * 4
            except IndexError:
                item_indentation = 0
            finally:
                indentation = self.indent + item_indentation

            # Save location of each new broken down line
            self.item_displays_wrapped_locs.append(line_no)
            for line in tt_wrap(item_display, terminal_width - indentation):
                line = ' ' * indentation + line.rstrip('\n') + ' ' * (terminal_width - self._get_onscreen_length(line) - indentation)
                self._item_displays_wrapped.append(line)
                line_no += 1

        return self._item_displays_wrapped

    @property
    def item_selected(self):
        """Return currently selected item index."""

        return self._item_selected

    @item_selected.setter
    def item_selected(self, potential_item_selected):
        """Safely update selected item index."""

        if 0 <= potential_item_selected < len(self.items):
            self._item_selected = potential_item_selected

    @staticmethod
    def _get_onscreen_length(string):
        """Returns on-screen length of given string"""

        return len(string) + sum(unicodedata.east_asian_width(char) in {'W', 'F', 'A'} for char in string)


class PageSubreddit(Page):
    """Holds information on how to display subreddit."""

    def __init__(self, items):
        Page.__init__(self, items)

        for item_no, item in enumerate(self.items, 1):
            self.item_displays.append(str(item_no) + '. ' +
                                      str(item.title) + '\n' +
                                      str(item.score) + 'pts ' +
                                      str(item.num_comments) + ' comments by (' +
                                      str(item.author) + ') - /r/' +
                                      str(item.subreddit))


class PageSubmission(Page):
    """Holds information on how to display a submission along with comments."""
    def __init__(self, items):
        Page.__init__(self, items)

        self.item_displays.append(str(items[0].title) + '\n' +
                                  str(items[0].score) + 'pts ' +
                                  str(items[0].num_comments) + ' comments by (' +
                                  str(items[0].author) + '\n\n' +
                                  str(re.sub('\n\s*\n', '\n\n', items[0].selftext)) + '\n' +
                                  '=' * terminal.width)

        self.item_indentations = self._get_comment_depth(items[0], items[1:])

        for item_no, item in enumerate(self.items[1:], start=1):
            try:
                self.item_displays.append(str(item.author) + ' - ' +
                                          str(item.score) + 'pts \n' +
                                          str(item.body))

            except AttributeError:
                self.item_displays.append('More comments...')

    @staticmethod
    def _get_comment_depth(submission, comments):
        comment_depth = [0]
        comment_indentation_depth = 0
        comment_indentation_depth_ids = [submission.id]
        for comment in comments:
            if comment.parent_id[3:] in comment_indentation_depth_ids:
                comment_indentation_depth = comment_indentation_depth_ids.index(comment.parent_id[3:])
                comment_indentation_depth_ids = comment_indentation_depth_ids[0:comment_indentation_depth + 1]
            else:
                comment_indentation_depth += 1
                comment_indentation_depth_ids.append(comment.parent_id[3:])
            comment_depth.append(comment_indentation_depth)
        return comment_depth
