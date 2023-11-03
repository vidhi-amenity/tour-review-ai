import importlib


def import_bot(stream_name):
    # Import the correct Bot Instance
    module = f"streams.scrapers.{stream_name}.bot.ScraperBot"
    imported_module = importlib.import_module(module.rsplit(".", 1)[0])
    return getattr(imported_module, module.rsplit(".", 1)[1])
