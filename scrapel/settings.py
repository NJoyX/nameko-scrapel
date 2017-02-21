from __future__ import unicode_literals, print_function, absolute_import

__author__ = 'Fill Q'
__all__ = ['Settings']


class SettingsKlass(dict):
    def set(self, **kwargs):
        self.update(**kwargs)


Settings = SettingsKlass
