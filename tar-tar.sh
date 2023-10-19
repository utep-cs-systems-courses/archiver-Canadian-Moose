#! /usr/bin/env bash

./mytar.py c foo.txt goo.gif > tar/tar.tar
./mytar.py x tar.tar

if diff src/foo.txt tar/foo.txt && diff src/goo.gif tar/goo.gif
then
    echo "success" >&2		# error msg to stdout
    exit 0			# return success
else
    echo "failure" >&2
    exit 1			# return failure
fi
