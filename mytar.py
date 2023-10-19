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


class Framer:
    def __init__(self, writer):
        self.writer = writer
    def insByte(self, val):
        if val == ord('|'):
            self.writer.writeByte(val)
        self.writer.writeByte(val)
    def insBytearray(self, barray):
        for val in barray:
            self.insByte(val)
    def terminate(self):
        self.writer.writeByte(ord('|'))
        self.writer.writeByte(ord('e'))
        self.writer.flush()


class Deframer:
    def __init__(self, reader):
        self.reader = reader
    def checkByte(self, val):
        if val == ord('|'):
            nextval = self.reader.readByte()
            if nextval == ord('e'):
                return False
        return True
    def readByteArray(self):
        content = ''
        
        while((bval := self.reader.readByte()) != None):
            term = self.checkByte(bval)
            
            if term:
                content += chr(bval)
            if not term:
                return content
            
        return None


def createFile(file_name):
    # Create the file path
    file_path = os.path.join(os.getcwd() + "/tar", file_name)
    # Check if the file exists, if it does delete it, create it
    if os.path.isfile(file_path):
        os.remove(file_path)
        os.mknod(file_path)
    else:
        os.mknod(file_path)
    # Open the file and return the file descriptor 
    file_fd = os.open(file_path, os.O_RDWR)
    return file_fd


def encodetofile(files):
    # Initialize the Writer 
    br = BufferedFdWriter(1)
    framer = Framer(br)
    
    for f in files:
        # Open the files
        file_path = os.path.join(os.getcwd() + "/src", f)
        file_fd = os.open(file_path, os.O_RDONLY)

        # initialize reader
        fd = BufferedFdReader(file_fd)
        f = f.encode()
        framer.insBytearray(f)
        framer.terminate()

        # Read the file and write to the buffer 
        while ((bval := fd.readByte()) != None):
            framer.insByte(bval)
        framer.terminate()
                
        # close the file 
        fd.close()

    # flush the writer
    # cannot close stdout 
    br.flush()


def decodefromfile(tar_file):
    # initialize the reader
    tar_path = os.path.join(os.getcwd() + "/tar", tar_file)
    tar_fd = os.open(tar_path, os.O_RDONLY)
    tar = BufferedFdReader(tar_fd)
    deframer = Deframer(tar)

    content = ''
    is_file = 1

    # Read from the tar
    while ((content := deframer.readByteArray()) != None):
        if is_file:
            print(f'Filename: ', content)
            fd = createFile(content)
            out = BufferedFdWriter(fd)
        if not is_file:
            for bval in content: 
                out.writeByte(ord(bval))
            out.close()
        is_file = 1 - is_file
        content = ''

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
