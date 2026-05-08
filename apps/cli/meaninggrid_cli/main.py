import httpx
import typer
from rich import print

from meaninggrid_core.config import get_settings

app = typer.Typer(help="MeaningGrid local CLI.")


@app.command()
def version() -> None:
    """Print the MeaningGrid CLI version."""
    print("MeaningGrid 0.1.0")


@app.command()
def health(api_url: str | None = None) -> None:
    """Check API health."""
    settings = get_settings()
    url = api_url or settings.api_public_url
    response = httpx.get(f"{url}/health", timeout=10)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    app()
