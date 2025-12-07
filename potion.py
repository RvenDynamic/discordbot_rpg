class Potion:
    def __init__(self, name, category, heal=0, defense_bonus=0, attack_bonus=0, description=""):
        self.name = name
        self.category = category  # misal: "Penyembuh", "Defense", "Attack"
        self.heal = heal
        self.defense_bonus = defense_bonus
        self.attack_bonus = attack_bonus
        self.description = description

# Contoh daftar potion
potions = {
    "Potion Penyembuh": Potion(
        name="Potion Penyembuh",
        category="Penyembuh",
        heal=50,
        description="Menyembuhkan 50 HP."
    ),
    "Potion Defense": Potion(
        name="Potion Defense",
        category="Defense",
        defense_bonus=10,
        description="Meningkatkan pertahanan sebesar 10 selama beberapa waktu."
    ),
    "Potion Attack": Potion(
        name="Potion Attack",
        category="Attack",
        attack_bonus=10,
        description="Meningkatkan serangan sebesar 10 selama beberapa waktu."
    )
}
