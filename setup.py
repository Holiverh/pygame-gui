
from distutils.core import setup

# WARNING: WILL BALLS UP PYGAME'S __init__.py IF YOU USE IT

setup(
	name="Pygame GUI",
	version="1.0",
	description="Provides GUI functionality for PyGame",
	author="Oliver Ainsworth",
	author_email="ottajay@googlemail.com",
	packages=["pygame", "pygame.gui"],
	#package_data={"pygame.gui": ["cursors", "themes"]}
	)
