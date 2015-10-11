import logging

import reddit
import terminal

logging.basicConfig(filename="sample.log", level=logging.DEBUG, filemode="w" )


def main():
    terminal_io = terminal.IO()
    reddit_io = reddit.IO()

    with terminal_io.setup():
        subreddit_title = 'worldnews'
        submissions = reddit_io.get_submissions(subreddit_title, 100)
        terminal_io.set_submissions(submissions)

        while True:
            terminal_io.render_submissions()

            key_pressed = terminal_io.get_key(1)
            if key_pressed.code == terminal_io.terminal.KEY_UP:
                terminal_io.selected_menu -= 1
            elif key_pressed.code == terminal_io.terminal.KEY_DOWN:
                terminal_io.selected_menu += 1

            if not key_pressed:
                pass

            if key_pressed.code == terminal_io.terminal.KEY_ESCAPE:
                logging.debug("This is a debug message")
                break

    terminal_io.cleanup()

if __name__ == '__main__':
    main()
