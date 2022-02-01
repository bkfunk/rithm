# import fire
import click
from rithm.rithm import Rithm


@click.command()
@click.option("-f", "--file", "file", type=click.File(), help="Rithm file to process")
@click.option("-i", "--input", "input", type=str, help="Literal input to evaluate")
# @click.option('-d', '--debug', 'debug', type=bool, default=True, help="Whether to turn on debug logging")
def rithm(file, input, debug: bool = True):
    rtm = Rithm()
    if file is not None:
        pass
    elif input is not None:
        try:
            res = rtm(input=input, debug=debug, result=True)
            click.echo(res)
            exit(0)
        except Exception:
            exit(65)
    else:
        # REPL
        while True:
            try:
                input = click.prompt("> ", prompt_suffix="")
                if input == "exit()":
                    click.echo("Exiting")
                    exit(0)
                res = rtm(input=input, debug=debug, result=True)
                click.echo(res)
                # self.error_handler.had_error = False
            except KeyboardInterrupt:
                click.echo("\nKeyboardInterrupt")
            except EOFError:
                click.echo()
                exit(0)
            except Exception as e:
                pass


if __name__ == "__main__":
    # fire.Fire(rithm)
    rithm()
