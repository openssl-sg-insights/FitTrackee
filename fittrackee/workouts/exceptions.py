from fittrackee.exceptions import GenericException


class PrivateWorkoutException(Exception):
    ...


class WorkoutException(GenericException):
    ...


class WorkoutGPXException(GenericException):
    ...


class WorkoutForbiddenException(GenericException):
    def __init__(self) -> None:
        super().__init__('error', 'you do not have permissions')
