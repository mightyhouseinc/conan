import getpass
import os
import sys

from conans.errors import ConanException


def is_terminal(stream):
    return hasattr(stream, "isatty") and stream.isatty()


def color_enabled(stream):
    """
    NO_COLOR: No colors

    https://no-color.org/

    Command-line software which adds ANSI color to its output by default should check for the
    presence of a NO_COLOR environment variable that, when present (**regardless of its value**),
    prevents the addition of ANSI color.

    CLICOLOR_FORCE: Force color

    https://bixense.com/clicolors/
    """

    if os.getenv("CLICOLOR_FORCE", "0") != "0":
        # CLICOLOR_FORCE != 0, ANSI colors should be enabled no matter what.
        return True

    return False if os.getenv("NO_COLOR") is not None else is_terminal(stream)


def init_colorama(stream):
    import colorama
    if color_enabled(stream):
        if os.getenv("CLICOLOR_FORCE", "0") != "0":
            # Otherwise it is not really forced if colorama doesn't feel it
            colorama.init(strip=False, convert=False)
        else:
            colorama.init()


class UserInput(object):
    """Class to interact with the user, used to show messages and ask for information"""

    def __init__(self, non_interactive):
        """
        Params:
            ins: input stream
            out: ConanOutput, should have "write" method
        """
        self._ins = sys.stdin
        # FIXME: circular include, move "color_enabled" function to better location
        from conan.api.output import ConanOutput
        self._out = ConanOutput()
        self._interactive = not non_interactive

    def _raise_if_non_interactive(self):
        if not self._interactive:
            raise ConanException("Conan interactive mode disabled")

    def raw_input(self):
        self._raise_if_non_interactive()
        return input()

    def request_login(self, remote_name, username=None):
        """Request user to input their name and password
        :param remote_name:
        :param username If username is specified it only request password"""
        self._raise_if_non_interactive()
        if not username:
            self._out.write(f"Remote '{remote_name}' username: ")
            username = self.get_username()

        self._out.write(f'Please enter a password for "{username}" account: ')
        try:
            pwd = self.get_password()
        except ConanException:
            raise
        except Exception as e:
            raise ConanException(f'Cancelled pass {e}')
        return username, pwd

    def get_username(self):
        """Overridable for testing purpose"""
        return self.raw_input()

    @staticmethod
    def get_password():
        """Overridable for testing purpose"""
        try:
            return getpass.getpass("")
        except BaseException:  # For KeyboardInterrupt too
            raise ConanException("Interrupted interactive password input")

    def request_string(self, msg, default_value=None):
        """Request user to input a msg
        :param default_value:
        :param msg Name of the msg
        """
        self._raise_if_non_interactive()

        if default_value:
            self._out.write(f'{msg} ({default_value}): ')
        else:
            self._out.write(f'{msg}: ')
        s = self._ins.readline().replace("\n", "")
        return default_value if default_value is not None and s == '' else s

    def request_boolean(self, msg, default_option=None):
        """Request user to input a boolean"""
        ret = None
        while ret is None:
            if default_option is True:
                s = self.request_string(f"{msg} (YES/no)")
            elif default_option is False:
                s = self.request_string(f"{msg} (NO/yes)")
            else:
                s = self.request_string(f"{msg} (yes/no)")
            if default_option is not None and s == '':
                return default_option
            if s.lower() in ['yes', 'y']:
                ret = True
            elif s.lower() in ['no', 'n']:
                ret = False
            else:
                self._out.error(f"{s} is not a valid answer")
        return ret
