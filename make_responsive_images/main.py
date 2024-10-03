import logging
from pathlib import Path
from typing import Optional

import typer

from . import __app_name__, __version__
from .utils import make_html, resize_image

app = typer.Typer(
    name="resize",
    # invoke_without_command means that if no subcommand is provided, the main function is called
    invoke_without_command=True,
    # no_args_is_help=True means that if no arguments are provided, the help message is shown
    no_args_is_help=False,
    # add_completion=True means that the command will support shell completion
    add_completion=True,
    # help is the help message for the main command
    help="Resize images",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def version(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> bool:
    """Show the application's version and exit."""
    if version:
        return True
    return False


@app.command()
def image(
    image: str = typer.Argument(
        str(
            Path(__file__)
            .parent.parent.joinpath("tests")
            .joinpath("fixtures")
            .joinpath("xfer-original.jpg")
        ),
        help="Image file location",
    ),
    widths: str = typer.Option("600,1000,1400", help="Widths of new images, in pixels"),
    html: bool = typer.Option(True, help="Generate HTML <img> tag"),
    classes: str = typer.Option(
        None, help='Classnames to add to the <img> tag (e.g. class="img-fluid")'
    ),
    img_sizes: str = typer.Option(
        "100vw", help='Sizes for the <img> tag (e.g. sizes="100vw")'
    ),
    lazy: bool = typer.Option(False, help='Adds loading="lazy" to <img> tag for SEO'),
    alt: str = typer.Option(
        "", help='Adds alt="" to the <img> tag (e.g. alt="Funny image")'
    ),
    dir: str = typer.Option(
        None, help='Images directory to prepend to the src (e.g. src="dir/images")'
    ),
    fmt: str = typer.Option(
        "webp", help='Image type to save as ("jpg" and "webp" supported)'
    ),
    qual: int = typer.Option(100, help="Compression to apply (i.e. 0=max, 100=min)"),
    lower: bool = typer.Option(True, help="Converts filename to lowercase"),
    dashes: bool = typer.Option(True, help="Converts underscores to dashes for SEO"),
    flask: bool = typer.Option(
        False, help="Uses Python Flask's 'url_for('static', ...)'"
    ),
    delete: bool = typer.Option(
        True, help="Delete the original image after resizing"
    ),
) -> bool:
    """This function is the entry point of the CLI."""

    typer.secho(f"Image: {image}", fg=typer.colors.GREEN)
    typer.echo(f"Widths needed: {widths}")
    typer.echo(f"HTML wanted: {html}")
    typer.echo(f"Classes wanted: {classes}")
    typer.echo(f"Image sizes wanted: {img_sizes}")
    typer.echo(f"Lazy loading wanted: {lazy}")
    typer.echo(f"Alt text wanted: {alt}")
    typer.echo(f"Directory to append: {dir}")
    typer.echo(f"Image format wanted: {fmt}")
    typer.echo(f"Quality/compression wanted: {qual}")
    typer.echo(f"Lowercase filename wanted: {lower}")
    typer.echo(f"Dashes wanted: {dashes}")
    typer.echo(f"Flask url_for() wanted: {flask}")

    widths_split = widths.split(",")
    widths_list = [int(width) for width in widths_split]

    file = Path(image)
    filenames = resize_image(
        file=file,
        widths=widths_list,
        fmt=fmt,
        qual=qual,
        lower=lower,
        dashes=dashes,
    )
    typer.echo(f"filenames: {filenames}")

    if html:
        html_str: str = make_html(
            orig_img_file=file,
            filenames=filenames,
            classes=classes,
            img_sizes=img_sizes,
            lazy=lazy,
            alt=alt,
            dir=dir,
            flask=flask,
        )
        typer.echo(f"HTML <img> tag: \n\n{html_str}")

    if delete:
        file.unlink()
        typer.echo(f"Deleted original image: {file}")

    typer.echo("\n\nDone!\n")

    return True


if __name__ == "__main__":
    app()
