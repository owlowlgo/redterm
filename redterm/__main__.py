import argparse
import logging
import os

import yaml

import redterm.browser
import redterm.pages
import redterm.terminal

logging.basicConfig(filename="./redterm.debug.log", level=logging.DEBUG, filemode="w")
logging.basicConfig(filename="./redterm.info.log", level=logging.INFO, filemode="w")


argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('-s', '--subreddit', nargs=1, help='Go to specified subreddit')
arguments = argument_parser.parse_args()

# Load settings
dir_config = os.environ['HOME'] + '/.redterm/'
file_config = dir_config + 'config.yml'

try:
    with open(file_config, 'r') as file:
        config = yaml.load(file)
except OSError:
    if not os.path.exists(dir_config):
        os.makedirs(dir_config)
    yaml.dump({'browser': 'lynx', 'subreddits': ['letsnotmeet', 'python']}, open(file_config, 'w'))
    with open(file_config, 'r') as file:
        config = yaml.load(file)

logging.debug(config['browser'])
logging.debug(config['subreddits'])


def main():
    """First entry point."""

    terminal_io = redterm.terminal.IO()

    if arguments.subreddit:
        subreddit_title = arguments.subreddit[0]
    else:
        subreddit_title = 'frontpage'

    with terminal_io.setup():
        page = redterm.pages.PageSubreddit(subreddit_title, redterm.terminal.terminal.width)
        terminal_io.pages.append(page)

        while True:
            page_current = terminal_io.pages[-1]
            item_selected = page_current.items[page_current.item_selected]

            terminal_io.render()

            # Controls
            key_pressed = terminal_io.get_key(1)

            if key_pressed.code == redterm.terminal.KEY_UP or key_pressed == 'k':
                terminal_io.select_item_prev()

            elif key_pressed.code == redterm.terminal.KEY_DOWN or key_pressed == 'j':
                terminal_io.select_item_next()

            elif key_pressed.code == redterm.terminal.KEY_PGUP:
                terminal_io.select_item_prevscreen()

            elif key_pressed.code == redterm.terminal.KEY_PGDN:
                terminal_io.select_item_nextscreen()

            elif key_pressed.code == redterm.terminal.KEY_ENTER:

                new_page = redterm.pages.PageSubmission(item_selected, terminal_io.terminal_width)

                terminal_io.pages.append(new_page)
                terminal_io.reset()

            elif key_pressed == 'o':
                try:
                    url = item_selected.url
                    redterm.browser.open_browser(config['browser'], url)
                except AttributeError:
                    # Items such as comments have no url, so do nothing
                    pass

            elif key_pressed.code == redterm.terminal.KEY_BACKSPACE:
                if len(terminal_io.pages) > 1:
                    del terminal_io.pages[-1]
                    terminal_io.reset()

            elif key_pressed.code == redterm.terminal.KEY_ESCAPE:
                break

            elif not key_pressed:
                pass

            #logging.debug(key_pressed.code)

if __name__ == '__main__':
    main()
