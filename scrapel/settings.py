__all__ = ['Settings']


class SettingsKlass(dict):
    def set(self, **kwargs):
        self.update(**kwargs)


Settings = SettingsKlass
