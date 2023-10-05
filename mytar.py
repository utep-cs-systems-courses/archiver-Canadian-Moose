#! /usr/bin/env python3
import os
import re
import sys


class BufferedFdReader:
    def __init__(self, fd, bufLen = 1024*16):
        self.fd = fd
        self.buf = b""
        self.index = 0
        self.bufLen = bufLen
    def readByte(self):
        if self.index >= len(self.buf):
            self.buf = os.read(self.fd, self.bufLen)
            self.index = 0
        if len(self.buf) == 0:
            return None
        else:
            retval = self.buf[self.index]
            self.index += 1
            return retval
    def close(self):
        os.close(self.fd)


class BufferedFdWriter:
    def __init__(self, fd, bufLen = 1024*16):
        self.fd = fd
        self.buf = bytearray(bufLen)
        self.index = 0
    def writeByte(self, bVal):
        self.buf[self.index] = bVal
        self.index += 1
        if self.index >= len(self.buf):
            self.flush()
    def flush(self):
        startIndex, endIndex = 0, self.index
        while startIndex < endIndex:
            nWritten = os.write(self.fd, self.buf[startIndex:endIndex])
            if nWritten == 0:
                os.write(2,f"buf.BufferedFdWriter(fd={self.fd}): flush failed\n".encode())
                sys.exit(1)
            startIndex += nWritten
        self.index = 0
    def close(self):
        self.flush()
        os.close(self.fd)


def bufferedCopy(byteReader, byteWriter):
    while (bv := byteReader.readByte()) is not None:
        byteWriter.writeByte(bv)
    byteWriter.flush()


def createFile(file_name):
    file_path = os.path.join(os.getcwd() + "/tar", file_name)
    if os.path.isfile(file_path):
        os.remove(file_path)
        os.mknod(file_path)
    else:
        os.mknod(file_path)
    file_fd = os.open(file_path, os.O_RDWR)
    return file_fd


def encodetofile(files):
    # Initialize the Writer 
    en = BufferedFdWriter(1)
    
    for f in files:
        # Open the files
        file_path = os.path.join(os.getcwd() + "/src", f)
        file_fd = os.open(file_path, os.O_RDONLY)

        # initialize reader
        fd = BufferedFdReader(file_fd)
        
        # Write file name
        for i in f:
            i = i.encode()
            print(i)
            if i == b'|':
                en.writeByte(i)
            en.writeByte(i)
        
        # Write terminator
        en.writeByte('|'.encode())
        en.writeByte('e'.encode())

        # Read the file and write to the buffer 
        ibuf = fd.readByte()
        while ibuf != None:
            # Replace terminators with duplicates
            if ibuf == b'|':
                en.writeByte(ibuf)
            en.writeByte(ibuf)
            ibuf = fd.readByte()

        # Write file terminator
        en.writeByte('|')
        en.writeByte('e')

        # close the file 
        fd.close()

    # close the writer and print done 
    print("Files successfully encoded\n")
    en.close()


def decodefromfile(tar_file):
    # initialize the reader
    tar_path = os.path.join(os.getcwd() + "/tar", tar_file)
    tar_fd = os.open(tar_path, os.O_RDONLY)
    tar = BufferedFdReader(tar_fd)

    is_name = 1
    file_name = b''

    # Read from the tar 
    ibuf = tar.readByte()
    while ibuf != None:
        if ibuf == b'|':
            ibuf = tar.readByte()
            if ibuf == b'e':
                if is_name:
                    temp = createFile(file_name)
                    is_name = 1 - is_name
                    fd = BufferedFdWriter(temp)
                    ibuf = tar.readByte()
                else:
                    fd.close()
                    is_name = 1 - is_name
                    ibuf = tar.readByte()
        if is_name:
            file_name += ibuf
        else:
            fd.writeByte(ibuf)

    print("Files successfully decoded\n")
    tar.close()


command = sys.argv[1]
    
if command == "c":
    files = sys.argv[2:]
    encodetofile(files)

elif command == "x":
    tar_file = sys.argv[2]
    decodefromfile(tar_file)

else:
    sys.stdout.write("Usage: mytar.py c|x <file1> <file2> ... <fileN>\n")
    sys.exit(1)
