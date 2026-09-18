from importlib import import_module


def _require_package(package: str, *, feature: str, extra: str) -> None:
    try:
        import_module(package)
    except ImportError as e:
        raise ImportError(
            f"{package} is required for {feature}. "
            f"Install it with `pip install pynimate[{extra}]`."
        ) from e
