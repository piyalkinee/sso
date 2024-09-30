from setproctitle import setproctitle

from .asgi import run as run_asgi

if __name__ == '__main__':
    setproctitle('sso_api_app:master')
    run_asgi()
