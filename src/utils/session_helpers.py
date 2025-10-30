
from flask import session


def set_last_visited_page(url):
    session['last_visited_page'] = url
