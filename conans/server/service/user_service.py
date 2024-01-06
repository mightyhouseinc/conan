from conans.errors import AuthenticationException


class UserService(object):

    def __init__(self, authenticator, credentials_manager):
        self.authenticator = authenticator
        self.credentials_manager = credentials_manager

    def authenticate(self, username, password):
        if valid := self.authenticator.valid_user(username, password):
            return self.credentials_manager.get_token_for(username)
        else:
            raise AuthenticationException("Wrong user or password")
