import click
import sys
import json
from .start_alerts import get_data_for_day

def validate_rolls(ctx, param, value):
    try:
        return json.loads(value)
    except ValueError:
        raise click.BadParameter('not a valid json input string')

@click.group()
def main():
    """"""
    pass

@main.command()
@click.pass_context
@click.argument('config_json', callback=validate_rolls)
def main(ctx, config_json):
    if ctx.invoked_subcommand is None:
        if type(config_json) == dict:
            pass
        else:
            click.echo("config json is not List.")
            exit()
        # print(config_json)
        get_data_for_day(config_json)
    else:
        click.echo('Generating sample config.')

# if __name__ == '__main__':
#     cli(obj={})