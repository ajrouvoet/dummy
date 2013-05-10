
install:
	mkdir -p ~/.local/bin/
	echo "#!/bin/bash" > ~/.local/bin/dummy
	echo 'python ~/repositories/dwarv-testing/src/dummy $$@' >> ~/.local/bin/dummy
	chmod a+x ~/.local/bin/dummy
	PATH="$$PATH:~/.local/bin"
