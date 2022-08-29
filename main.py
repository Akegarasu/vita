from core.log import logger
from core.vita import Vita
import click


@click.command(name="vita")
@click.option(
    "-t",
    help="目标文件/目录",
)
@click.option(
    "-r",
    help="规则文件目录",
)
def cli(t, r):
    v = Vita(rule_path=r)
    v.run(1)


if __name__ == "__main__":
    cli()
