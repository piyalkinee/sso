from fastapi import Request
from databases.core import Connection


class Session:
    def __init__(self, request=None):
        self.request: Request = request
        self.db: Connection = None
        self.user = None
