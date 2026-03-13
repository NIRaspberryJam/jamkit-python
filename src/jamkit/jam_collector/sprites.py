# src/jamkit/sprites.py
from dataclasses import dataclass
from importlib import resources as importlib_resources

@dataclass(frozen=True)
class Sprite:
    """A sprite that knows which asset file it uses."""
    name: str        # logical name, e.g. "raspberry"
    filename: str    # file under jamkit.assets/, e.g. "raspberry.gif"

    def path(self) -> str:
        """Return an absolute path suitable for turtle.addshape()."""
        # jamkit.assets is the package where the GIFs live
        return str(
            importlib_resources.files("jamkit.assets").joinpath(self.filename)
        )

# Public sprites for kids to use
raspberry = Sprite("raspberry", "raspberry.gif")
bug = Sprite("bug", "bug.gif")
fork = Sprite("fork", "fork_full.gif")
