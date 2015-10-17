import logging
import re
import unicodedata

import praw
from uniseg.wrap import tt_wrap

reddit_api = praw.Reddit(user_agent='User-Agent: python:redterm:v0.0.1')


class PageBase:
    """Base class for how items are to be displayed and selected."""

    def __init__(self, width, indent=2):
        self.items = []                       # Items to be displayed on page, such as Submission and Comment objects
        self.item_displays = []               # Actual text to be displayed
        self._item_displays_wrapped = []      # Wrapped version of above
        self.item_displays_wrapped_locs = []  # Index of locations of items in the buffer
        self._item_selected = 0               # Currently selected item
        self.item_indentations = []           # Index of indentation level of items

        self.width = width    # Indent page by this value
        self.indent = indent  # Indent page by this value

    @property
    def item_displays_wrapped(self):
        """Process items to display to be wrapped according to current terminal size."""
        logging.debug('width: ' + str(self.width))
        # Reset current wrapped item info
        self._item_displays_wrapped = []
        self.item_displays_wrapped_locs = []

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
            for line in tt_wrap(item_display, self.width - indentation):
                line = ' ' * indentation + line.rstrip('\n') + ' ' * (self.width - self._get_onscreen_length(line) - indentation)
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


class PageSubreddit(PageBase):
    """Holds information on how to display subreddit."""

    def __init__(self, subreddit_title, width, indent=2):
        PageBase.__init__(self, width, indent=2)

        for submission in reddit_api.get_subreddit(subreddit_title).get_hot(limit=100):
            self.items.append(submission)

        for item_no, item in enumerate(self.items, 1):
            self.item_displays.append(str(item_no) + '. ' +
                                      str(item.title) + '\n' +
                                      str(item.score) + 'pts ' +
                                      str(item.num_comments) + ' comments by (' +
                                      str(item.author) + ') - /r/' +
                                      str(item.subreddit))


class PageSubmission(PageBase):
    """Holds information on how to display a submission along with comments."""
    def __init__(self, submission, width, indent=2):
        PageBase.__init__(self, width, indent=2)

        self.submission = submission

        self.item_displays.append(str(self.submission.title) + '\n' +
                                  str(self.submission.score) + 'pts ' +
                                  str(self.submission.num_comments) + ' comments by (' +
                                  str(self.submission.author) + '\n\n' +
                                  str(re.sub('\n\s*\n', '\n\n', self.submission.selftext)) + '\n' +
                                  '=')

        for comment in praw.helpers.flatten_tree(submission.comments):
            self.items.append(comment)

        self.item_indentations = self._get_comment_depth(self.submission, self.items)

        for item_no, item in enumerate(self.items):
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

