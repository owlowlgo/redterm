# redterm
A console based Reddit reader with plans to implement features to enhance the reddit experience while browsing reddit signed out.

One main feature currently being worked on, are functions to enable bookmarking of subreddits and saving of submissions and comments, *locally*.
This will be accompanied by a psuedo front page generated based on local bookmarks(Probably by utilizing the multi reddit feature). 

The benefit of this is that your privacy will be intact in the case there is a Ashley Madison type incident on reddit.

If you think you would value this feature, please stick around while development continues.  

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
* Any features requiring logging in such as posting comments.

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


## License
MIT
