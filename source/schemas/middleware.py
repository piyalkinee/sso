from databases.core import Connection
from fastapi import Request


class Session:
    def __init__(self, request=None):
        request: Request = request
        db: Connection
