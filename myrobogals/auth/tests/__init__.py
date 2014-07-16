from myrobogals.auth.tests.basic import BASIC_TESTS
from myrobogals.auth.tests.views \
        import PasswordResetTest, ChangePasswordTest, LoginTest, LogoutTest
from myrobogals.auth.tests.forms import FORM_TESTS
from myrobogals.auth.tests.remote_user \
        import RemoteUserTest, RemoteUserNoCreateTest, RemoteUserCustomTest
from myrobogals.auth.tests.tokens import TOKEN_GENERATOR_TESTS

# The password for the fixture data users is 'password'

__test__ = {
    'BASIC_TESTS': BASIC_TESTS,
    'FORM_TESTS': FORM_TESTS,
    'TOKEN_GENERATOR_TESTS': TOKEN_GENERATOR_TESTS,
}
