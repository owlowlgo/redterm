import blessed


class IO:
    """Wrapper for Blessed to render Reddit"""
    def __init__(self):
        self.terminal = blessed.Terminal()
        print(self.terminal.enter_fullscreen)
        print(self.terminal.clear)

        self.submissions = []
        self.submission_infos = []
        self.comments = []

        self.selected_menu = 0
        self.render_offset = 0

    def set_submissions(self, submissions):
        self.submissions = submissions

        for submission_no, submission in enumerate(self.submissions, 1):
            self.submission_infos.append(str(submission_no) + '. ' + str(submission.score) + ':' + str(submission.author) + ':' + submission.title)

    def render_subreddit(self):
        for i, submission_info in enumerate(self.submission_infos[self.render_offset:self.render_offset + self.terminal.height - 1]):
            print(self.terminal.move(i, 0) + ' ' + submission_info)
        print(self.terminal.move(self.selected_menu, 0) + '>')

    def get_key(self, timeout=1):
        return self.terminal.inkey(timeout=timeout)

    def cleanup(self):
        print(self.terminal.clear)
        print(self.terminal.exit_fullscreen)
