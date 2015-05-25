#!/usr/bin/python
import os, sys

def dimensions(): return tuple(map(int, os.popen('stty size', 'r').read().split()))

def cursor_back(symbols): sys.stdout.write('\033[' + symbols + 'D')

def cursor_up(lines=1): print '\033[{}A'.format(lines)