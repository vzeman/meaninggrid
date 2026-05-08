import signal
import time

from meaninggrid_core.config import get_settings


def main() -> None:
    settings = get_settings()
    running = True

    def stop(_: int, __: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print(
        "MeaningGrid scheduler started "
        f"(env={settings.environment}, queue={settings.queue_backend})",
        flush=True,
    )
    while running:
        time.sleep(5)
    print("MeaningGrid scheduler stopped", flush=True)


if __name__ == "__main__":
    main()
