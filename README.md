# redterm
A console based Reddit reader with plans to implement features to enhance the reddit experience while browsing reddit signed out.

One main feature currently being worked on, are functions to enable bookmarking of subreddits and saving of submissions and comments, *locally*.
This will be accompanied by a psuedo front page generated based on local bookmarks(Probably by utilizing the multi reddit feature). 

The benefit of this is that your privacy will be intact in the case there is an Ashley Madison type incident on reddit.

If you think you would value these features, please stick around while development continues.  

## Current Features
* Viewing of specified subreddit.
* Viewing of submission, and comments.
* Full support for mixed narrow/wide text(CJK).

## Features planned
* Support for loading 'More comments' when specified.
* Support for saving submissions and comments *locally*.
* Support for bookmarking favorite subreddits and having your personal frontpage, login not required.

## Features *not* planned 
* Account log in.
* Any features requiring an account such as posting comments.

(May consider implementing above if there is enough interest from users.) 

## Installation

Install from pip.

```
pip install redterm
```

Clone from GitHub.

```
$ git clone https://github.com/owlowlgo/redterm.git
$ cd redterm
$ sudo python setup.py install
```

## Usage

```
$ redterm -s subreddit
```

## Controls
* Up(j)/Down(k): Move cursor
* Enter: Choose Submission/Comment
* o: Open url in browser specified in config file(~/.redterm/config.yaml)
* Esc: Quit

## License
MIT

## Thanks
This project would not have been possible without the following projects.

* blessed
https://github.com/jquast/blessed

* PRAW
https://github.com/praw-dev/praw
