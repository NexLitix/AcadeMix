class InvalidPointsException(BaseException):
    def __init__(self, error_text: str) -> None:
        self.error_text = error_text
        
    def __str__(self) -> str:
        return self.error_text