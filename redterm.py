import argparse
import logging
import sys

import pages
import terminal

logging.basicConfig(filename="redterm.debug.log", level=logging.DEBUG, filemode="w")

argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('-s', '--subreddit', nargs=1, help='Got to specified subreddit')
arguments = argument_parser.parse_args()


def main():
    terminal_io = terminal.IO()

    if arguments.subreddit:
        subreddit_title = arguments.subreddit[0]
    else:
        subreddit_title = 'frontpage'

    with terminal_io.setup():
        page = pages.PageSubreddit(subreddit_title, terminal.terminal.width)
        terminal_io.pages.append(page)

        while True:
            page_current = terminal_io.pages[-1]

            terminal_io.render(page_current)

            key_pressed = terminal_io.get_key(1)
            if key_pressed.code == terminal.KEY_UP:
                page_current.item_selected -= 1

            elif key_pressed.code == terminal.KEY_DOWN:
                page_current.item_selected += 1

            elif key_pressed.code == terminal.KEY_PGUP:
                page_current.item_selected = terminal_io.get_out_of_screen_item_loc_prev(page_current)

            elif key_pressed.code == terminal.KEY_PGDN:
                page_current.item_selected = terminal_io.get_out_of_screen_item_loc_next(page_current)

            elif key_pressed.code == terminal.KEY_ENTER:
                submission_selected = page_current.items[page_current.item_selected]
                new_page = pages.PageSubmission(submission_selected, terminal.terminal.width)

                terminal_io.pages.append(new_page)
                terminal_io.reset()

            elif key_pressed.code == terminal.KEY_BACKSPACE:
                if len(terminal_io.pages) > 1:
                    del terminal_io.pages[-1]
                terminal_io.reset()

            elif key_pressed.code == terminal.KEY_ESCAPE:
                break

            elif not key_pressed:
                pass

            #logging.debug(key_pressed.code)

if __name__ == '__main__':
    main()
