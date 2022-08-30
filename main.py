from core.log import logger
from core.vita import Vita
import click


@click.command(name="vita")
@click.option(
    "-t",
    help="目标文件目录",
)
@click.option(
    "-r",
    help="规则文件目录",
)
@click.option(
    "-ignore",
    help="忽略的文件后缀",
)
def cli(t, r, ignore):
    logger.info(f"start run vita using rule {r}, target {t}")
    Vita(rule_path=r).run(
        file_path=t,
        ignore=ignore
    )


if __name__ == "__main__":
    cli()
