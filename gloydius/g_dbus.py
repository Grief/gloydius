#!/usr/bin/python
import dbus

from gloydius import GLOYDIUS_DATA
from gloydius.fs import path as p

GLOYDIUS_ICON = p(GLOYDIUS_DATA, 'gloydius-icon.png')

def dbus_method(bus, path, interface, method, *args): return getattr(dbus.SessionBus().get_object(bus, path), method)(*args, dbus_interface=interface)

def get_capabilities():
    name = 'org.freedesktop.Notifications'
    # method= 'org.freedesktop.Notifications.GetCapabilities'
    print dbus_method(name, '/' + name.replace('.', '/'), name, 'GetCapabilities')

def desktop_notify(summary, body=None, persist=True, icon=GLOYDIUS_ICON):
    name = 'org.freedesktop.Notifications'
    dbus_method(name, '/' + name.replace('.', '/'), name, 'Notify',
                'Gloydius', 0, icon, summary, '' if body is None else body, [], {}, 0 if persist else -1)
