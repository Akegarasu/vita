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
    "-o",
    default="./templates",
    help="输出文件路径",
)
@click.option(
    "-ignore",
    default="",
    help="忽略的文件后缀 使用英文逗号分割",
)
def cli(t, r, o, ignore):
    logger.info(f"start run vita using rule {r}, target {t}, output {o}")
    Vita(rule_path=r, output_path=o).run(
        file_path=t,
        ignore=ignore
    )


if __name__ == "__main__":
    cli()
