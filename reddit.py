import praw


class IO:
    """Wrapper for PRAW to provide functionality to help rendering on console easier"""
    def __init__(self):
        self.reddit = praw.Reddit(user_agent='redterm')

    def get_submissions(self, name_subreddit, limit=50):
        submissions = []
        for submission in self.reddit.get_subreddit(name_subreddit).get_hot(limit=limit):
            submissions.append(submission)

        return submissions

    def get_comments(self, submission):
        comments = []
        for comment in praw.helpers.flatten_tree(submission.comments):
            comments.append(comment)

        return comments

    def get_comment_depth(self, submission):
        comment_depth = []
        comment_indentation_depth = 0
        comment_indentation_depth_ids = [submission.id]
        comments = praw.helpers.flatten_tree(submission.comments)
        for comment in comments:
            if comment.parent_id[3:] in comment_indentation_depth_ids:
                comment_indentation_depth = comment_indentation_depth_ids.index(comment.parent_id[3:])
                comment_indentation_depth_ids = comment_indentation_depth_ids[0:comment_indentation_depth + 1]
            else:
                comment_indentation_depth += 1
                comment_indentation_depth_ids.append(comment.parent_id[3:])
            comment_depth.append(comment_indentation_depth)
        return comment_depth

