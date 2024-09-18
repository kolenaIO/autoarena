from fastapi import HTTPException


class BadRequestError(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=400, detail=msg)


class NotFoundError(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=404, detail=msg)


class MigrationError(RuntimeError): ...
