from fastapi import HTTPException

class ImageTooLargeError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="File too large")

class InvalidImageTypeError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="File must be an image")

class AnalysisTimeoutError(HTTPException):
    def __init__(self):
        super().__init__(status_code=504, detail="Analysis timed out")

class ConfigurationError(HTTPException):
    def __init__(self):
        super().__init__(status_code=500, detail="Configuration error")