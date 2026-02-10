"""Primary training entrypoint for the refactored structure."""


def main() -> None:
    """Run the legacy Click CLI through the new src.train entrypoint."""
    try:
        from main import cli
    except ModuleNotFoundError as exc:
        missing = exc.name or "unknown"
        raise SystemExit(
            f"Cannot start training CLI because dependency module '{missing}' is missing. "
            "Initialize project dependencies (including DCD_MUSIC) and retry."
        ) from exc

    cli()


if __name__ == "__main__":
    main()
