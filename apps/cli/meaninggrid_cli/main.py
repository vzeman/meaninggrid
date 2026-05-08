import httpx
import typer
from meaninggrid_core.config import get_settings
from meaninggrid_db.database import session_scope
from meaninggrid_db.seed import ensure_local_seed
from rich import print

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


@app.command()
def seed() -> None:
    """Run the idempotent local database seed."""
    with session_scope() as session:
        result = ensure_local_seed(session)
    print(result)


if __name__ == "__main__":
    app()
