import pytest

from machine_plugins.commander import Command, CommandArgument

N = 'some-name'


def test_commandargument_definitions_errors():
    """Tests covering definition errors like incorrect arguments or type mismatch."""
    for t in [bytes, dict, list, tuple]:
        with pytest.raises(TypeError):
            CommandArgument(name=N, target_type=t)
    with pytest.raises(AssertionError):
        CommandArgument(name=N, target_type=str, choices=['a', 'b'], validation=(lambda s: True,))
    with pytest.raises(TypeError):
        CommandArgument(name=N, validation=('Forgotten callable as first argument.',))
    with pytest.raises(ValueError):
        CommandArgument(name=N, target_type=int, choices=['1.337'])


def test_commandargument_validation_exception():
    def crashing_validator(_):
        assert 1 == 2

    ca = CommandArgument(name=N, validation=(crashing_validator,))
    assert ca.errors('irrelevant') != []


def test_commandargument_definitions_successes():
    CommandArgument(name=N, target_type=str)
    CommandArgument(name=N, target_type=str, choices=['a'])
    c = CommandArgument(
        name=N,
        target_type=float,
        validation=(lambda f: 0 <= float(f) < 1, 'Value not between 0 and 1 (exlusive).'),
        description='Some value between 0 and 1 (exclusive).',
    )
    assert c.errors('0.5') is None
    err = c.errors('1')
    assert isinstance(err, str)


def test_command_definitions_simple():
    with pytest.raises(TypeError):
        Command(name=N, description='You do not need this if you have no arguments!')

    echo_cmd = Command(
        name='echo',
        description='Echoes back what one word you said.',
        arguments=[
            CommandArgument(name='msg', description='Anything really...'),
        ],
    )
    assert echo_cmd.errors('') != []
    assert echo_cmd.errors('42') == []


def test_command_definitions_realistic_example():
    scale_cmd = Command(
        name='scale',
        description='Scale a deployment.',
        arguments=[
            CommandArgument(
                name='namespace',
                target_type=str,
                choices=['default', 'dev'],
                description='Namespace of the deployment.',
            ),
            CommandArgument(
                name='deployment',
                validation=(lambda d: d.startswith('deployment-prefix-'),),
                description='Name of the deployment.',
            ),
            CommandArgument(
                name='replicas',
                target_type=int,
                validation=(lambda r: 2 <= int(r) <= 10, 'You can not scale under 2 or above 10 replicas.'),
            ),
        ],
    )
    scale_cmd.usage
    assert scale_cmd.errors('default deployment-prefix-1 3') == []
    # too few or too many arguments
    assert scale_cmd.errors('default deployment-prefix-1') != []
    assert scale_cmd.errors('default deployment-prefix-1 3 ohhaither') != []
    # validation errors for individual arguments
    assert scale_cmd.errors('definitely-not-dev deployment-prefix-1 3') != []
    assert scale_cmd.errors('default foo 3') != []
    assert scale_cmd.errors('default deployment-prefix-1 11') != []
    assert scale_cmd.errors('default deployment-prefix-1 1.337') != []
