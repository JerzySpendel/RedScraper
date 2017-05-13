class State:
    states = [
        'created',
        'getting_url',
        'downloading_site',
        'pushing_urls',
        'feeding_data',
        'done',
    ]

    def __init__(self, name):
        if name not in self.states:
            raise Exception("Invalid State name")
        self.name = name

    def __le__(self, other):
        return self.states.index(self.name) <= self.states.index(other.name)

    def __lt__(self, other):
        return self.states.index(self.name) < self.states.index(other.name)
