#!/bin/bash
function unz {
        echo -e "\033[01;34m[\033[01;32m*\033[01;34m]\033[1;37m $1\033[00m"
}

function sbrah {
	echo -e "\033[01;32mo.O\033[1;37m $1\033[00m"
}

function info {
	echo -e " \033[01;32m:\033[1;37m  $1\033[00m"
}

function cons {
	echo -e " :  \033[01;34m`basename $PWD` #\033[00m $1"
}

directory="$1"

if [ "$1" == "" ]; then
	echo
	sbrah "::::::::::..-:.     ::-.:::.       .,-::::: .::::::.    ...    :::  :::.     "
	sbrah " \`;;;\`\`\`.;;;';;.   ;;;;';;\`;;    ,;;;'\`\`\`\`',;;'\`\`\`';;,  ;;     ;;;  ;;\`;;    "
	sbrah "  \`]]nnn]]'   '[[,[[[' ,[[ '[[,  [[[       [[[     [[[\\[['     [[[ ,[[ '[[,  "
	sbrah "    \$\$\$\"\"        c\$\$\"  c\$\$\$cc\$\$\$c \$\$\$       \"\$\$c  cc\$\$\$\"\$\$      \$\$\$c\$\$\$cc\$\$\$c "
	sbrah "    888o       ,8P\"\`    888   888,\`88bo,__,o,\"*8bo,Y88b,88    .d888 888   888,"
	sbrah "    YMMMb     mM\"       YMM   \"\"\`   \"YUMMMMMP\" \"*YP\" \"M\" \"YmmMMMM\"\" YMM   \"\"\` "
	sbrah "                                                                              v 1.0"

	echo
	info "ei you! probably you are trying to install pyacqua on your box. I'm sorry,"
	info "but the task is not so simple. So you must read carefully this warning before"
	info "proceeding :D"
	info ""
	info "To install py-acqua you must type as root"
	info ""
	cons "./startup.sh /usr                                  (to install in /usr) "
	echo
	info "--- OR ---"
	echo
	cons "./startup.sh /usr/local                      (to install in /usr/local) "
	info ""
	info "mhh..remember! For bugs, insults, porn-photos we have a mail and also a website."
	info ""
	info "PyAcqua Team:"
	info "  info@pyacqua.net"
	info "  http://www.pyacqua.net"
	info ""
	info "ok it's all. Good luck $USER ;-)"
	echo
	info "Cowsay:"
	info "                                         ___________________________________ "
	info "                                        / No animals were harmed during the \\ "
	info "                                        \ making of this release.           /"
	info "                                         ----------------------------------- "
	info "                                                   \   ^__^"
	info "                                                    \  (oo)\_______"
	info "                                                       (__)\       )\/\\ "
	info "                                                           ||----w |"
	info "                                                           ||     ||"


	echo

	exit 
fi

unz "Cleaning up for backup file (~)"
. scripts/clean.sh

if [ "$1" == "makeupdate" ]; then
	# Creiamo la directory per l'update da piazzare sul sito

	unz "Cleaning the build-update/ directory..."
	rm -rf build-update/

	mkdir -p build-update/source/pyacqua

	cp -rf src build-update/source/pyacqua
	cp -rf pixmaps build-update/source/pyacqua
	cp -rf tips build-update/source/pyacqua
	cp -rf skins build-update/source/pyacqua
	cp -rf plugins build-update/source/pyacqua
	cp -rf locale build-update/source/
	
	unz "Creating the source-list.xml for this revision.."
	cd build-update/source/
	python pyacqua/src/generate.py makelist
	mv list.xml ../source-list.xml

	unz "Now you can put the build-update directory under your site with the name update"
else
	unz "Installing pyacqua to $directory ..."

	mkdir -p $directory/share/pyacqua
	mkdir -p $directory/bin

	cp -rf src $directory/share/pyacqua
	cp -rf pixmaps $directory/share/pyacqua
	cp -rf tips $directory/share/pyacqua
	cp -rf skins $directory/share/pyacqua
	cp -rf plugins $directory/share/pyacqua
	cp -rf locale $directory/share

	unz "Creating the bash wrapper with the name of bin/pyacqua"
	cat > $directory/bin/pyacqua << EOF
#!/bin/sh

function unz {
        echo -e "\033[01;34m[\033[01;32m*\033[01;34m]\033[1;37m \$1\033[00m"
}

if [ -f ~/.pyacqua/program/pyacqua/src/acqua.py ]; then
	unz "PyAcqua is already installed in home directory. Launching from ~/.pyacqua/program/share/pyacqua"
	
	cd ~/.pyacqua/program/pyacqua/

	if [ -f ~/.pyacqua/update/.diff.xml ]; then
		unz "Try to merge update..."
		python src/merger.py
	fi
	
	python src/acqua.py
else
	unz "Making dir structure..."
	mkdir -p ~/.pyacqua/program/

	unz "Copyng the program..."
	cp $directory/share/pyacqua ~/.pyacqua/program/ -rf

	unz "Copying the locale dir..."
	cp -rf $directory/share/locale ~/.pyacqua/program/

	unz "Ok. Now we are going to launch pyacqua from home directory..."
	unz "Good work pyacqua-user ;)"

	cd ~/.pyacqua/program/pyacqua/
	python src/acqua.py

	unz "Are you ok? .. Really? .. No crash? No explosion? .. mhh very strange.."
	unz "Hei \$USER! Remember to visit our site at http://www.pyacqua.net"
fi
EOF

	chmod +x $directory/bin/pyacqua

	unz "Creating the list.xml for this revision.."
	cd $directory/share/
	python pyacqua/src/generate.py makelist
	mv list.xml pyacqua/

	unz "Deleting .svn directories"
	cd ../
	for f in `find -name .svn -type d`; do rm -rf $f; done
fi
