class UnverifiedUser(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
class UnverifiedUserToken(Exception):
    pass

class InvalidToken(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class UserNotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MailAlreadyExist(Exception):
    pass

class CodeExpired(Exception):
    pass

class CodeDoesNotMatch(Exception):
    pass