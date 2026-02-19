__version__ = "0.2.0"

# Lazy imports: do not import submodules at package level to avoid side effects
# (e.g. argparse setup, path resolution) when the package is merely imported
# as a library.  Use explicit imports where needed:
#   from gabbe.main import main
#   from gabbe.database import init_db, get_db
