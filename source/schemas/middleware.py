from fastapi import Request


class Session:
    def __init__(self, request=None):
        request: Request = request
