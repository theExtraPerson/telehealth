from flask import Blueprint



@display.route('/')
def display():
    return '<h1>hello from display</h1>'

@display.route('/second')
def second():
    return 'the second display'


