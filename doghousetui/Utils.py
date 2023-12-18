
API_SERVER = 'http://127.0.0.1:8000/api/v1'
API_SERVER_PORT = 8000
API_SERVER_LOGIN = API_SERVER+"/auth/login/"
API_SERVER_LOGIN_ROLE = API_SERVER+"/role/"
API_SERVER_LOGOUT = API_SERVER+"/auth/logout/"
API_SERVER_REGISTER = API_SERVER+"/auth/registration/"
API_SERVER_DOGS = API_SERVER + "/dogs/"

LOGIN_MENU_DESCRIPTION = 'DOGHOUSE Login'
LOGIN_ENTRY = 'login'
CONTINUE_WITHOUT_LOGIN_ENTRY = 'continue without login'
REGISTER_ENTRY = 'register'
EXIT_ENTRY = 'exit'
BACK_TO_LOGIN_MENU_ENTRY = "back to login menu"

USER_MENU_DESCRIPTION = 'DOGHOUSE '
SHOW_DOGS_ENTRY = 'show dogs'
SHOW_PREFERENCES_ENTRY = 'show preferences'
ADD_PREFERENCE_ENTRY = 'add preference'
REMOVE_PREFERENCE_ENTRY = 'remove preference'
LOGOUT_ENTRY = 'logout'

NOT_LOGGED_MENU_DESCRIPTION = 'DOGHOUSE'
GENERIC_USER_MENU_DESCRIPTION = 'generic user Menu'
ADMIN_MENU_DESCRIPTION='DOGHOUSE'
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

RESPONSE_ROLE_KEY = "role"
RESPONSE_USER_ROLE_USER_VALUE = "user"
RESPONSE_USER_ROLE_ADMIN_VALUE = "doghouse-worker"
INSERT_USERNAME_MESSAGE = 'insert username: '
INSERT_EMAIL_MESSAGE = 'insert email (OPTIONAL): '
INSERT_PASSWORD_MESSAGE = 'insert password: '
REPEAT_PASSWORD_MESSAGE = 'Repeat password: '
REGISTRATION_PASSWORDS_DO_NOT_COINCIDE = 'The passwords do not coincide'

LOGIN_ERROR_SERVER_RESPONSE_JSON_KEY = 'non_field_errors'

REGISTRATION_SUCCEEDED_MESSAGE = 'We have correctly registered your account, you are now able to login'
INVALID_MENU_SELECTION = 'Invalid selection. Please, try again...'

DATE_WRONG_FORMAT_MESSAGE = 'Expected iso format string'
INVALID_TOKEN = 'The received token is not valid'