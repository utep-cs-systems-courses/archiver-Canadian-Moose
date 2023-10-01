#! usr/bin/env python3

import os
import re
import sys


def encodetofile(files, tar_file):
    # create the directory 
    path = os.getcwd() + "/tar"
    if not os.path.exists(path):
        os.makedirs(path)
    
    # open the tar_file for storing
    tar_path = os.path.join(os.getcwd() + "/tar", tar_file)

    if os.path.isfile(tar_path):
        os.remove(tar_path)
        os.mknod(tar_path)
    else:
        os.mknod(tar_path)
    
    tar_fd = os.open(tar_path, os.O_RDWR)
    
    for f in files:
        # Open the files
        file_path = os.path.join(os.getcwd() + "/src", f)
        file_fd = os.open(file_path, os.O_RDONLY)
        file_size = os.path.getsize(tar_path)

        # Read file into a buffer and write to tar_file 
        ibuf = os.read(file_fd, file_size)
        os.write(tar_fd, ibuf)

        # write file to the tar file 
        os.write(tar_fd, ("|" + f + "|").encode('latin-1'))

        # close the file 
        os.close(file_fd)
    
    # close tar
    os.close(tar_fd)
    sys.stdout.write("Files successfully encoded\n")


def decodefromfile(tar_file):
    # open the tar file
    tar_path = os.path.join(os.getcwd() + "/tar", tar_file)
    tar_fd = os.open(tar_path, os.O_RDONLY)
    file_size = os.path.getsize(tar_path)
    
    # read the file content
    file_content = os.read(tar_fd, file_size).decode('latin-1')
    file_content = file_content.split("|")

    i = 0
    while i < len(file_content)-1:
        file_path = os.path.join(os.getcwd() + "/tar", file_content[i+1])
        if os.path.isfile(file_path):
            os.remove(file_path)
            os.mknod(file_path)
        else:
            os.mknod(file_path)
        file_fd = os.open(file_path, os.O_RDWR)
        os.write(file_fd, bytes(file_content[i], 'latin-1'))
        os.close(file_fd)
        i += 2
    
    # print out the file contents
    os.close(tar_fd)
    sys.stdout.write("Files successfully decoded\n")


command = sys.argv[1]
tar_file = sys.argv[-1]
    
if command == "c":
    files = sys.argv[2:-1]
    encodetofile(files, tar_file)

elif command == "x":
    decodefromfile(tar_file)

else:
    sys.stdout.write("Usage: mytar.py c|x <file1> <file2> ... <fileN> <tarFile>\n")
    sys.exit(1)
