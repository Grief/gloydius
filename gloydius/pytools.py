#!/usr/bin/python
import functools, os, errno, itertools, datetime, psutil, pygments, pygments.lexers, pygments.formatters, subprocess, struct, xml.dom.minidom

from PIL import Image
from termcolor import colored

XML_LEXER         = pygments.lexers.get_lexer_by_name('xml')
CONSOLE_FORMATTER = pygments.formatters.get_formatter_by_name('console')


def get_pid(name):
    for proc in psutil.process_iter():
        print(proc)
        if name in '.'.join(proc.cmdline): return proc.pid
    return 0


def check_running(message, name):
    pid = get_pid(name)
    if pid == 0: status = colored('NOT RUNNING', 'red')
    else: status = colored('PID %s' % pid, 'green')
    print('{0:15} {1}'.format(message, status))


def run(command):
    try: subprocess.call(command)
    except os.error as e:
        print('{0:15} {1}\n\t'.format(colored('CANNOT RUN', 'red'), command), e)

def make_dirs(path):
    try: os.makedirs(path)
    except OSError as e:
        if not (e.errno == errno.EEXIST and os.path.isdir(path)): raise e

def create_symlink(name, target):
    try: os.symlink(target, os.path.expanduser(name))
    except os.error as e:
        if e.errno == errno.EEXIST:
            print('{0:20} {1:40} -> {2}'.format(colored('EXISTS', 'yellow'), name, target))
            return True
        print('Cannot create symlink %s -> %s:\n\t' % (name, target), e)
        return False
    print('{0:20} {1:40} -> {2}'.format(colored('LINKED', 'green'), colored(name, 'blue'), target))
    return True


def remove_file(name):
    try: os.remove(name)
    except os.error as e:
        if e.errno == errno.ENOENT:
            print('{0:20} {1}'.format(colored('REMOVED', 'yellow'), name))
            return True
        print('Cannot delete' + colored(name, 'red') + '\n\t', e)
        return False
    print('{0:20} {1:40}'.format(colored('DELETED ', 'green'), name))
    return True


def print_table(command, separator=':', headers=False):
    lines, sizes = [], []

    def     update(parts): return [max((len(part) if part else 0), (0 if size is None else size)) for part, size in itertools.zip_longest(parts, sizes)]
    def print_line(parts): print("|".join(map(lambda part, size: '{:{}}'.format(part, size), parts, sizes)))

    if headers: sizes = update(headers)

    for line in subprocess.check_output(command, shell=True, universal_newlines=True).split('\n'):
        words = line.split(separator)
        lines.append(words)
        sizes = update(words)

    horizontal = '-' * (functools.reduce(lambda size1, size2: size1 + size2, sizes) + len(sizes) - 1)
    print(horizontal)

    if headers:
        print_line(headers)
        print(horizontal)

    for line in lines: print_line(line)
    print(horizontal)


def terminal_size(): return tuple(map(int, os.popen('stty size', 'r').read().split()))


def print_xml(text): print(pygments.highlight(xml.dom.minidom.parseString(text).toprettyxml(indent='    '), XML_LEXER, CONSOLE_FORMATTER))

def gradient(color1, color2, length=4, escape=None):
    return ' '.join([esc(bg=tuple([int((c2 - c1) * i / (length - 1) + c1) for c1, c2 in zip(color1, color2)]), escape=escape) for i in range(length)]) + ' '


def print_image(file_name, columns=0, aspect=2):
    if columns < 1: columns = terminal_size()[1]
    img = Image.open(file_name)
    width, height = img.size
    width, height = (columns, int(height * columns / width / aspect)) if width > columns else (width, int(height / aspect))
    pix = img.resize((width, height), Image.ANTIALIAS).load()
    for y in range(0, height): print(' '.join([esc(bg=pix[x, y]) for x in range(0, width)]) + ' ' + esc())


def enum(**values):
    e = values.copy()
    e['dict'] = values
    return type('Enum', (), e)

def unicode_clock(time=None):
    if time is None: time = datetime.datetime.now()
    hour   = time.hour
    minute = time.minute
    half = False
    if 15 <= minute:
        if minute < 45: half = True
        else: hour += 1
    if hour == 0: hour  = 12
    if hour > 12: hour -= 12
    return struct.pack('<I', (128347 if half else 128335) + hour).decode('UTF-32')
