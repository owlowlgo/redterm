import logging
import re
from urllib.parse import urlparse

import blessed
import praw
from uniseg.wrap import tt_wrap

terminal = blessed.Terminal()
reddit_api = praw.Reddit(user_agent='desktop:https://github.com/owlowlgo/redterm:0.0.0')  # TODO Add version


class PageBase:
    """Base class for how items are to be displayed and selected."""

    def __init__(self, name, width, indent=2):
        self.name = name
        self.items = []                    # Items to be displayed on page, such as Submission and Comment objects
        self.item_strings = []             # Actual text to be displayed
        self._item_strings_formatted = []  # Formatted version of above
        self.item_onscreenlocs = []        # Index of locations of items in the buffer
        self._item_selected = 0            # Currently selected item
        self.item_indentations = []        # Index of indentation level of items

        self.width = width                 # Indent page by this value
        self.indent = indent               # Indent page by this value

    @property
    def item_strings_formatted(self):
        """Process items to display to be wrapped according to current terminal size."""

        # Reset current wrapped item info
        self._item_strings_formatted = []
        self.item_onscreenlocs = []

        # Prepare tags
        tags = {'[SEP1]': '-' * (self.width - 5),
                '[SEP2]': '=' * (self.width - 5)}

        # Take each item to display by line, and break it into multiple lines based of current terminal width
        line_no = 0
        for item_no, item_display in enumerate(self.item_strings):
            # Confirm indentation level for each item
            try:
                item_indentation = self.item_indentations[item_no] * 4
            except IndexError:
                item_indentation = 0
            finally:
                indentation = self.indent + item_indentation

            # Save location of each new broken down line
            self.item_onscreenlocs.append(line_no)
            for line in tt_wrap(item_display, self.width - indentation):

                if line == '[SEP1]':
                    line = tags['[SEP1]']
                elif line == '[SEP2]':
                    line = tags['[SEP2]']

                line = terminal.bold_white_on_black(' ' * indentation + line.rstrip('\n'))
                self._item_strings_formatted.append(line)
                line_no += 1

        return self._item_strings_formatted

    @property
    def item_selected(self):
        """Return currently selected item index."""

        return self._item_selected

    @item_selected.setter
    def item_selected(self, potential_item_selected):
        """Safely update selected item index."""

        if 0 <= potential_item_selected < len(self.items):
            self._item_selected = potential_item_selected


class PageSubreddit(PageBase):
    """Holds information on how to display subreddit."""

    def __init__(self, subreddit_title, width, indent=2):
        PageBase.__init__(self, '/r/' + subreddit_title, width, indent=2)

        for submission in reddit_api.get_subreddit(subreddit_title).get_hot(limit=100):
            self.items.append(submission)

        for item_no, item in enumerate(self.items, 1):
            self.item_strings.append(terminal.bold_white_on_black(str(item_no) + '. ') +
                                     terminal.bold_white_on_black(str(item.title) + ' (') +
                                     terminal.blue_on_black('{uri.netloc}'.format(uri=urlparse(item.url))) + terminal.bold_white_on_black(')') + '\n' +
                                     terminal.bold_white_on_black(str(item.score) + 'pts ') +
                                     terminal.bold_white_on_black(str(item.num_comments) + ' comments by ') +
                                     terminal.cyan_on_black(str(item.author)) + terminal.bold_white_on_black(' - ') +
                                     terminal.cyan_on_black('/r/' + str(item.subreddit)) + '\n' +
                                     str('\n'))



    #derivatives = ('on', 'bright', 'on_bright',)
    #colors = set('black red green yellow blue magenta cyan white'.split())

class PageSubmission(PageBase):
    """Holds information on how to display a submission along with comments."""

    def __init__(self, submission, width, indent=2):
        PageBase.__init__(self, '/r/' + str(submission.subreddit) + '/' + submission.title, width, indent=2)

        self.submission = submission

        self.item_strings.append(terminal.bold(str(self.submission.title)) + '(' +
                                 terminal.underline_blue('{uri.netloc}'.format(uri=urlparse(self.submission.url))) + ')\n' +
                                 str(self.submission.score) + 'pts ' +
                                 str(self.submission.num_comments) + ' comments by (' +
                                 terminal.underline_cyan(str(self.submission.author)) + ')' +
                                 str(re.sub('\n\s*\n', '\n\n', self.submission.selftext)) + '\n' +
                                 '[SEP1]')

        for comment in praw.helpers.flatten_tree(submission.comments):
            self.items.append(comment)

        self.item_indentations = self._get_comment_depth(self.submission, self.items)

        for item_no, item in enumerate(self.items):
            try:
                self.item_strings.append(terminal.white_on_black('* ') + terminal.cyan_on_black(str(item.author)) + ' - ' +
                                         str(item.score) + 'pts \n' +
                                         str(item.body) + '\n'
                                         '\n')

            except AttributeError:
                self.item_strings.append(terminal.underline_blue('More comments...') + '\n'
                                         '\n')

        self.items = [self.submission] + self.items  # TODO This is ugly. Need refactor.

    @staticmethod
    def _get_comment_depth(submission, comments):
        """pass"""

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

