

def start():
    import flask
    from flask_terminado import Terminal

    terminal_host = flask.Flask(__name__)

    @terminal_host.route('/')
    def home():
        return 'home'

    terminal = Terminal(terminal_host)
    terminal.add_terminal('/bash', ['bash'])
    terminal.run(port=5000, host='0.0.0.0')
start()