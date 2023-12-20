
API_SERVER = 'http://127.0.0.1:8000/api/v1'
API_SERVER_PORT = 8000
API_SERVER_LOGIN = API_SERVER+"/auth/login/"
API_SERVER_LOGIN_ROLE = API_SERVER+"/role/"
API_SERVER_LOGOUT = API_SERVER+"/auth/logout/"
API_SERVER_REGISTER = API_SERVER+"/auth/registration/"
API_SERVER_DOGS = API_SERVER + "/dogs/"
API_SERVER_PREFERENCES = API_SERVER + "/dogs/favourite-dogs/"

LOGIN_MENU_DESCRIPTION = 'DOGHOUSE Login'
LOGIN_ENTRY = 'login'
CONTINUE_WITHOUT_LOGIN_ENTRY = 'continue without login'
REGISTER_ENTRY = 'register'
EXIT_ENTRY = 'exit'
BACK_TO_LOGIN_MENU_ENTRY = "back to login menu"

USER_MENU_DESCRIPTION = 'DOGHOUSE User Menu'
SHOW_DOGS_ENTRY = 'show dogs'
SHOW_PREFERENCES_ENTRY = 'show preferences'
SHOW_DOGS_WITH_FILTER_ENTRY = 'Show dogs with filters'
ADD_PREFERENCE_ENTRY = 'add preference'
REMOVE_PREFERENCE_ENTRY = 'remove preference'
LOGOUT_ENTRY = 'logout'

GENERIC_USER_MENU_DESCRIPTION = 'DOGHOUSE Not logged user Menu'
ADMIN_MENU_DESCRIPTION='DOGHOUSE Admin Menu'
ADD_DOG_ENTRY='add dog'
REMOVE_DOG_ENTRY='remove dog'

EXIT_MESSAGE = 'Bye!'
LOGOUT_MESSAGE = 'Logged out'

LOGGED_IN_MESSAGE = 'Logged in as %s'
SERVER_ERROR_STATUS_CODE = 'ERROR %d, failed to %s'
INVALID_USERNAME_ERROR="Invalid username"
INVALID_EMAIL_ERROR="Invalid email, it must be of the format <user>@<domain>"
INVALID_PASSWORD_ERROR="Invalid password"
CONNECTION_ERROR="Unable to contact server"
LOGIN_ERROR = 'We were unable to log you in'
LOGOUT_ERROR = 'Unable to logout'
REGISTRATION_ERROR = 'We were unable to register your account'
INVALID_CREDENTIALS = "Invalid credentials, please try again"

DEFAULT_TOKEN_VALUE = 'notloggedtoken00000000000000000000000000'

PATH_TO_BREED_JSON = 'resources/dogs_breeds.json'
INVALID_BREED = 'The selected breed is not among the valid ones'
INVALID_SEX = 'The provided value for sex is not valid'
INVALID_DESCRIPTION = 'The provided description is not valid'
INVALID_DOG_NAME = 'The provided dog name is not valid'
INVALID_DATE = 'The provided date is not valid'
INVALID_URL = 'The provided url is not valid'
INVALID_NEUTERED_VALUE = 'The provided value for neutered is not valid'
INVALID_ESTIMATED_SIZE = 'The provided value for estimated size must be a size such as: XS, S, M, L, XL'
RESPONSE_ROLE_KEY = "role"
RESPONSE_USER_ROLE_USER_VALUE = "user"
RESPONSE_USER_ROLE_ADMIN_VALUE = "doghouse-worker"
INSERT_USERNAME_MESSAGE = 'insert username: '
INSERT_EMAIL_MESSAGE = 'insert email (OPTIONAL): '
INSERT_PASSWORD_MESSAGE = 'insert password: '
CONFIRM_PASSWORD_MESSAGE = 'confirm password: '
REPEAT_PASSWORD_MESSAGE = 'Repeat password: '
REGISTRATION_PASSWORDS_DO_NOT_COINCIDE = 'The passwords do not coincide'

LOGIN_ERROR_SERVER_RESPONSE_JSON_KEY = 'non_field_errors'

REGISTRATION_SUCCEEDED_MESSAGE = 'We have correctly registered your account, you are now able to login'
INVALID_MENU_SELECTION = 'Invalid selection. Please, try again...'

DATE_WRONG_FORMAT_MESSAGE = 'Expected iso format string'
INVALID_TOKEN = 'The received token is not valid'

SHOW_DOGS_ERROR = 'There was an error while retrieving dogs'
DOG_RECEIVED_ERROR = 'Found corrupted dog data for a dog, ignored'
SHOW_DOGS_BATCH_SIZE = 2
WANTS_MORE_QUESTION = 'Want more?(y/n)'
WANTS_MORE_YES_ANSWER = 'y'
REQUIRE_INPUT_DOG_DATA = "Insert dog data"
DOG_ID_INPUT = '\t id: '
DOG_BREED_INPUT = '\t breed: '
DOG_SEX_INPUT = '\t sex(M/F): '
DOG_BIRTH_DATE_INPUT = '\t birth date(yyyy-mm-dd): '
DOG_ESTIMATED_ADULT_SIZE_INPUT = '\t estimated adult size(XS/S/M/L/XL): '
DOG_ENTRY_DATE_INPUT = '\t entry date(yyyy-mm-dd): '
DOG_NEUTERED_INPUT = '\t neutered:(Y/N) '
DOG_DESCRIPTION_INPUT = '\t description(enter to leave empty): '
DOG_NAME_INPUT = '\t name(enter to leave empty): '
DOG_PICTURE_INPUT = '\t picture url(enter to leave empty): '
DOG_ID_PRINT = '\t id: '
DOG_BREED_PRINT = '\t breed: '
DOG_SEX_PRINT = '\t sex: '
DOG_BIRTH_DATE_PRINT = '\t birth date: '
DOG_ESTIMATED_ADULT_SIZE_PRINT = '\t estimated adult size: '
DOG_ENTRY_DATE_PRINT = '\t entry date: '
DOG_NEUTERED_PRINT = '\t neutered: '
DOG_DESCRIPTION_PRINT = '\t description: '
DOG_NAME_PRINT = '\t name: '
DOG_PICTURE_PRINT = '\t picture url: '
DOG_ID_VALIDATION_ERROR = 'dog id must be a positive integer'
DOG_NOT_FOUND_ERROR = 'The specified dog does not exist'
DOG_DELETED_MESSAGE = 'correctly deleted'
DOG_ADDED_MESSAGE = 'correctly added'
DOG_BREED_FILTER = '\tbreed [OPTIONAL]: '
DOG_ESTIMATED_ADULT_SIZE_FILTER = '\testimated adult size [OPTIONAL]: '
DOG_LOWER_BIRTH_DATE_INPUT = '\tminimum birth year(yyyy) [OPTIONAL]: '
DOG_GREATER_BIRTH_DATE_INPUT = '\tminimum birth year(yyyy) [OPTIONAL]: '
SUGGEST_BREED_MESSAGE = 'Maybe you meant a breed among: '

PREFERENCES_DOG_ID_KEY = 'dog_id'
REGISTRATION_SUCCEEDED_MESSAGE = 'We have correctly registered your account, you are now able to login'
ADD_PREFERENCE_SUCCEEDED_MESSAGE = 'We have correctly added you preference, you can now see it by doing show preferences'
REMOVE_PREFERENCE_SUCCEEDED_MESSAGE = 'We have correctly removed you preference'
REMOVE_PREFERENCE_FAILED_MESSAGE = 'We were unable to remove the preference'
ADD_PREFERENCE_FAILED_DOG_ID = 'Preference could not be added since the specified dog does not exist'
ADD_PREFERENCE_FAILED_DUPLICATE = 'Preference could not be added since you already expressed preference for the specified dog'

PANIC_ERROR = 'Panic Error, something went wrong. Terminating'