HERE=`pwd`
install:
	mkdir -p ~/.local/bin/
	echo "#!/bin/bash" > ~/.local/bin/dummy
	echo "python $(HERE)/dummy \$$@" >> ~/.local/bin/dummy
	chmod a+x ~/.local/bin/dummy
	PATH="$$PATH:~/.local/bin"

install-virt:
	mkdir -p ~/.local/bin/
	echo "#!/bin/bash" > ~/.local/bin/dummy
	echo "source $(HERE)/python/bin/activate" >> ~/.local/bin/dummy
	echo "python $(HERE)/dummy \$$@" >> ~/.local/bin/dummy
	chmod a+x ~/.local/bin/dummy
	PATH="$$PATH:~/.local/bin"
