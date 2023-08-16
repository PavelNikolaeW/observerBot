class APIException(Exception):
    pass


class ScaleNotFoundException(Exception):
    pass


class ScaleValueException(Exception):
    pass


class TimerValueException(Exception):
    pass


class TimerStarted(Exception):
    pass


class TimerNotStarted(Exception):
    pass


class WrongTitle(Exception):
    pass
