import logging
import os
import webbrowser


def open_browser(browser, url):
    if browser == 'lynx':
        b = webbrowser.get('lynx')
    else:
        b = webbrowser

    b.open_new_tab(url)
