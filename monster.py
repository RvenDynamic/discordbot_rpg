class Monster:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.max_hp = 50 + level * 20
        self.hp = self.max_hp
        self.attack = 5 + level * 5
        self.defense = 3 + level * 2

class Boss(Monster):
    def __init__(self, name, level):
        super().__init__(name, level)
        # Boss lebih kuat, misal HP dan attack 2x lipat
        self.max_hp *= 2
        self.hp = self.max_hp
        self.attack *= 2
        self.defense *= 2
