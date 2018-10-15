import pendulum
from molten.validation.field import Validator


class PendulumValidator(Validator):
    def validate(self, value):
        return pendulum.parse(value)
