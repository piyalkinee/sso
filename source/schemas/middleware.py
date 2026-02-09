from fastapi import Request
from databases.core import Connection


class Session:
    def __init__(self, request=None):
        request: Request = request
        db: Connection
        user = None  # Explicitly allow user attribute
