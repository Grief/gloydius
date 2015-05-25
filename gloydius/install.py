#!/usr/bin/python
import os, shutil, stat, zipfile
import tarfile
from gloydius import path

from gloydius.color import log
from gloydius.pytools import make_dirs

from gloydius.terminal import cursor_back

def find_in(directory, filters):
    include, exclude, result = set(), set(), set()

    def get_inclusion(variants):
        count = len(variants)
        inclusion = [-1] * count
        for i in range(count):
            v = variants[i]
            if   v in exclude: inclusion[i] = 0
            elif v in include: inclusion[i] = 1
        return inclusion

    negation = False
    for word in filters.lower().split(' '):
        if len(word) == 0: continue
        if word == 'not':
            negation = True
            continue
        if negation:
            exclude.add(word)
            negation = False
        else: include.add(word)

    type_inclusion = get_inclusion(['file', 'dir', 'link'])

    # print include, exclude
    for name in os.listdir(directory):
        full = path(directory, name)
        mode = os.stat(full).st_mode
        if any([inc != -1 and inc != getattr(stat, func)(mode) for inc, func in zip(type_inclusion, ['S_ISREG', 'S_ISDIR', 'S_ISLNK'])]): continue

        if 'hidden' in exclude and name.startswith('.'): continue

        result.add(name)
    return result

def symlink(link, target, backup=None):
    if os.path.islink(link) and os.readlink(link) == target:
        log('pass', '{} is already installed', link)
        return
    if os.path.isdir(link): shutil.rmtree(link)
    if os.path.exists(link) or os.path.islink(link):
        if backup is not None: shutil.move(link, backup)
        os.remove(link)
    try:
        os.symlink(target, link)
        log('info', '{} has been installed', link)
    except OSError as e:
        if e.errno == 13: log('err', '{}: not enough permissions', link)
        else: log('err', '{}: unknown error {}', link, e.errno)

def ini_config(name, changes, backup):
    log('info', '\nChanging ini configuration in {}', name)
    if not os.path.exists(name): log('warn', 'File {} does not exist', name)  #TODO: create parent dirs
    else:
        orig = name + '-original'
        os.rename(name, orig)
        with open(name, 'w') as ini:
            section = None
            if None not in changes: changes[None] = {}
            for line in open(orig):
                line = line[:-1]
                skip = False
                if line in changes: section = line
                else:
                    for param, value in changes[section].iteritems():
                        if line.startswith(param):  # vvv TODO more careful (strip middle and compare to '=')
                            if line == param + '=' + value: log('pass', '{} is already set to {} in {} section', param, value, section)
                            else:
                                ini.write((''.join((param, '=', value, '\n'))))
                                skip = True
                                log('info', '{} was set to {} in {} section (previously {})', param, value, section, line[len(param) + 1:])
                            del changes[section][param]
                            break
                if not skip: ini.write(line + '\n')
        if backup is None: os.remove(orig)
        else:
            backup = os.path.sep.join((backup, os.path.basename(name)))
            if os.path.exists(backup): os.remove(backup)
            shutil.move(orig, backup)
    with open(name, 'a') as ini:
        for section, params in changes.iteritems():
            if len(params) == 0: continue
            ini.write('\n')
            ini.write(''.join((section, '\n')))
            for param, value in params.iteritems():
                ini.write(''.join((param, '=', value, '\n')))

def extract_from_zip(archive, mask, target):
    with zipfile.ZipFile(archive) as zip:
        for name in zip.namelist():
            if mask.match(name) is None: continue
            with zip.open(name) as f, open(target, 'wb') as t:
                shutil.copyfileobj(f, t)
            return True
    return False

# TODO: Warning: Never extract archives from untrusted sources without prior inspection. It is possible that files are created outside of path, e.g. members that have absolute filenames starting with "/" or filenames with two dots "..".
def extract_tar_archive(archive, directory):
    make_dirs(directory)
    with tarfile.open(archive) as tar: tar.extractall(path=directory)
    return True

def ask():
    return True

    # if not found:
    #     log('warn', 'section {} not found in {}', section, ini)
