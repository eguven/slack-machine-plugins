# slack-machine-plugins

Utility plugins for Slack-Machine, the sexy, simple, yet powerful and extendable Slack bot.

```shell
pip install slack-machine-plugins
```

## commander

Commander provides two classes ``Command`` and ``CommandArgument`` for a declarative way to define chat commands and their arguments for input validation and error feedback for the user. Features include:

* Type and length validation for chat command arguments.
* Strict choices.
* Custom validation and error messages.
* Usage and error texts for user feedback.

### Example Usage

Taken from test case, realistic example.

```python
# command definition
####################
from machine_plugins.commander import Command, CommandArgument

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

# command usage in slack-machine
################################
from machine.plugins.base import MachineBasePlugin
from machine.plugins.decorators import respond_to


class DeploymentPlugin(MachineBasePlugin):

    @respond_to(regex=r'^scale ?(?P<args>.*)$')
    def scale(self, msg, args):
        errs = scale_cmd.errors(args)
        if errs:
            resp = '\n'.join(errs)
            msg.say(f'```{resp}```')
            return
        # input validation complete, do your thing e.g `scale(*args.split())`
```
