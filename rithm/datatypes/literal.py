class Literal:
    def __getattr__(self, attr):
        return getattr(self.value, attr)
