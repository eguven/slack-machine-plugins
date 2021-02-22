import logging

from typing import Callable, Optional, Sequence, Tuple, Type, Union

logger = logging.getLogger(__name__)

T_Choices = Union[Type[str], Type[int], Type[float]]
T_Validation = Tuple[Callable[[str], bool], str]  # (lambda s: True, 'err')


class CommandArgument:
    """Represents one expected argument in a chat command."""

    def __init__(
        self,
        name: str,
        target_type: T_Choices = str,
        choices: Optional[Sequence[str]] = None,
        validation: Optional[T_Validation] = None,
        description: Optional[str] = None,
    ):
        """
        :param name: Name for the argument, used for help and feedback texts.
        :param target_type: Type for the argument, used for type checking input and choices. Only
           str (default), int, float are supported for now.
        :param choices: A sequence of strictly defined choices, must be type castable to target_type.
        :param validation: A tuple of a callable (str -> bool) which should return True for success, and
            an error text that will be used for user feedback. The validator will be run on the input
            ie. the input string and not the value after type cast. The error text can include properties
            of the argument for str.format() i.e.
            error_text='Input for {name} was expected to be one of {choices}'.
        """
        _default_validation_error_text = 'Validation error for "{name}"'
        _supported_types = [str, int, float]

        if target_type not in _supported_types:
            raise TypeError(f'target_type "{target_type}" not in supported types {_supported_types}"')

        self.name = name
        self.target_type = target_type
        self.choices = choices
        self.__assert_choices()
        self.description = description

        self.validator, self.validation_error_text = None, None
        if validation is not None and callable(validation[0]):
            if self.choices:
                raise AssertionError('You can not provide a validation when you provide choices.')
            self.validator = validation[0]
            if len(validation) > 1 and validation[1] is not None:
                self.validation_error_text = str(validation[1])
            else:
                self.validation_error_text = _default_validation_error_text

        elif validation is not None:
            raise TypeError('First element of the validation tuple is not a callable.')

    @property
    def usage(self):
        """Build the usage string for feedback."""
        usage = f'{self.name}'
        if self.choices:
            usage += ' · [{}]'.format('|'.join(self.choices))
        if self.description:
            usage += ' · {}'.format(self.description)
        return usage

    def _run_validator(self, input: str) -> Optional[str]:
        """Run validator if one was provided, if successful return None. Return the formatted
        validation error string otherwise.
        """
        if self.validator is None:
            logger.debug(f'No validator provided for "{self.name}"')
            return None

        # unnecessary, but keeps mypy happy
        if self.validation_error_text is not None:
            err = self.validation_error_text.format(
                name=self.name,
                target_type=self.target_type,
                choices=self.choices,
                description=self.description,
            )
        try:
            if self.validator is not None and self.validator(input) is True:
                return None
            else:  # validation error
                return err
        except Exception:  # pokemon!
            logger.exception(f'Exception in _run_validator for "{self.name}"')
            return err

    def __assert_choices(self) -> None:
        """If choices are provided, ensure that they can be cast to target_type.
        Raise ValueError otherwise.
        """
        if self.choices is None:
            return
        for choice in self.choices:
            try:
                self.target_type(choice)
            except ValueError:
                raise ValueError(f'Provided choice "{choice}" can not be cast to target type {self.target_type}')

    def errors(self, input: str) -> Optional[str]:
        """Return None if input is correct, return an error string otherwise."""
        if self.choices is not None and input in self.choices:  # expected input
            return None
        elif self.choices is not None:  # unexpected input
            return f'Argument error for "{self.name}". Expected one of {self.choices}, got "{input}".'
        try:  # builtin type check and custom validation if provided
            self.target_type(input)
            _validator_error = self._run_validator(input)
            if _validator_error is not None:
                return _validator_error
        except ValueError:  # no choices defined, can't cast to target type
            return f'Provided input "{input}" can not be cast to target type {self.target_type}'
        # no choices defined and can cast, return None
        return None


class Command:
    """Definition of a chat command with expected arguments as defined by ``CommandArgument``"""

    def __init__(self, name: str, arguments: Sequence[CommandArgument], description: Optional[str]):
        """
        :param name: Name of command, used for help and feedback texts.
        :param arguments: Iterable of CommandArgument objects for the comamnd.
        :param description: Command description, used for help and feedback texts.
        """
        self.name = name
        self.arguments = arguments
        self.description = description

    @property
    def usage(self):
        """Build the usage string for feedback."""
        usage = f'{self.name} - {self.description}'
        for arg in self.arguments:
            usage += f'\n  {arg.usage}'
        return usage

    def errors(self, args_string: str) -> Sequence[str]:
        """Input verification and user feedback. Returns a list of error strings. Error strings
        attempt to be useful for the user.

        :param args_string: String from the chat message (excluding the command name) intended as
            input for the command.
        """
        error_list = []
        # only use the expected number of arguments for verification
        input_args = args_string.split()
        acknowledged_args = input_args[: len(self.arguments)]
        for idx, arg in enumerate(acknowledged_args):
            # error: Missing positional argument "self" in call to "errors" of "CommandArgument"
            err = self.arguments[idx].errors(arg)
            if err is not None:
                error_list.append(err)
        # check additionally for incorrect number of arguments
        input_len, expected_len = len(input_args), len(self.arguments)
        if input_len > expected_len:
            for extra_arg in input_args[expected_len:]:
                error_list.append(f'Extra argument: "{extra_arg}".')
        elif input_len < expected_len:
            for missing_arg in self.arguments[input_len:]:
                error_list.append(f'Missing argument: {missing_arg.usage}')
        return error_list
