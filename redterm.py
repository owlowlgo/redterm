import reddit
import terminal

def main():
    terminal_io = terminal.IO()
    reddit_io = reddit.IO()

    #with terminal_io.listen_for_keys():
    # TODO Need to figure out how to encapsulate b
    with terminal_io.terminal.cbreak(), terminal_io.terminal.hidden_cursor():
        subreddit_title = 'newsokur'
        submissions = reddit_io.get_submissions(subreddit_title, 100)
        terminal_io.set_submissions(submissions)

        while True:
            terminal_io.render_subreddit()

            key_pressed = terminal_io.get_key(1)
            if key_pressed.code == terminal_io.terminal.KEY_UP and terminal_io.selected_menu > 0:
                terminal_io.selected_menu -= 1
            elif key_pressed.code == terminal_io.terminal.KEY_DOWN:
                terminal_io.selected_menu += 1
                if terminal_io.selected_menu >= terminal_io.terminal.height:
                    terminal_io.selected_menu = 0
                    terminal_io.render_offset += terminal_io.terminal.height

            if not key_pressed:
                pass

            if key_pressed.code == terminal_io.terminal.KEY_ESCAPE:
                break

    terminal_io.cleanup()

    #comments = io.get_comments(submissions[0])

if __name__ == '__main__':
    main()
