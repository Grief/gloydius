import datetime, mmap, os

def path(*parts): return os.path.sep.join(parts)

def parent_dir(path, level):
    for i in range(0, level): path = os.path.dirname(path)
    return path

def read_file(name):
    f = open(name)
    return mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)

def read_file_lines(name):
    return [line.rstrip('\n') for line in open(name).readlines()]

def for_line(name, action, *state):
    for line in open(name, 'r'): state = action(line.rstrip('\n'), *state)

def write_file(name, content):
    parent = parent_dir(name, 1)
    if not os.path.exists(parent): os.makedirs(parent)
    elif   os.path.exists(name):   os.remove(name)
    with open(name, 'w') as f:
        f.write(content)

def utc_mtime(path):
    try: return datetime.datetime.utcfromtimestamp(os.stat(path).st_mtime)
    except OSError: return None