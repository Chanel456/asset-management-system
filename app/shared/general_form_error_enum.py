from enum import Enum


class GeneralFormError(Enum):
    INVALID_URL = 'Please enter a valid URL'
    INVALID_EMAIL = 'Please enter a valid email'
    INVALID_EMAIL_LENGTH = 'Email address cannot exceed 150 characters'
    INTEGER_NOT_GREATER_THAN_OR_EQUAL_TO_ZERO= 'Please enter a valid integer greater than 0'
    INTEGER_NOT_GREATER_THAN_OR_EQUAL_TO_ONE = 'Please enter a valid integer greater than 1'