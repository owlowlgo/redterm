import praw


class IO:
    """Wrapper for PRAW to provide functionality to help rendering on console easier"""
    def __init__(self):
        self.reddit = praw.Reddit(user_agent='User-Agent: python:redterm:v0.0.1')

    # Retrieve submissions and return list
    def get_submissions(self, name_subreddit, limit=50):
        submissions = []
        for submission in self.reddit.get_subreddit(name_subreddit).get_hot(limit=limit):
            submissions.append(submission)

        return submissions

    # Retrieve comments of submission and return list
    def get_comments(self, submission):
        comments = []
        for comment in praw.helpers.flatten_tree(submission.comments):
            comments.append(comment)

        return comments

    def is_page_subreddit(self, page):
        return type(page[0]) is praw.objects.Submission

    def is_page_submission(self, page):
        return type(page[0]) is praw.objects.Comment


if __name__ == '__main__':
    reddit_io = IO()

    subreddit_title = 'newsokur'
    submissions = reddit_io.get_submissions(subreddit_title, 100)
    for submission in submissions:
        print(dir(submission))
