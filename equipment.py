class Weapon:
    def __init__(self, name, category, attack_bonus=0, defense_bonus=0, agility_bonus=0, description=""):
        self.name = name
        self.category = category
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.agility_bonus = agility_bonus
        self.description = description

# Daftar senjata dengan atribut berbeda
weapons = {
    "Pedang 1 Tangan": Weapon(
        name="Pedang 1 Tangan",
        category="Pedang",
        attack_bonus=7,
        defense_bonus=2,
        agility_bonus=0,
        description="Senjata serbaguna dengan keseimbangan serangan dan pertahanan."
    ),
    "Pedang Pendek": Weapon(
        name="Pedang Pendek",
        category="Pedang",
        attack_bonus=4,
        defense_bonus=3,
        agility_bonus=2,
        description="Senjata cepat dengan keseimbangan serangan, pertahanan, dan kelincahan."
    ),
    "Busur": Weapon(
        name="Busur",
        category="Busur",
        attack_bonus=5,
        defense_bonus=0,
        agility_bonus=5,
        description="Senjata jarak jauh yang meningkatkan kelincahan."
    ),
    "Tongkat": Weapon(
        name="Tongkat",
        category="Tongkat",
        attack_bonus=3,
        defense_bonus=1,
        agility_bonus=0,
        description="Senjata sihir yang memberikan sedikit bonus serangan dan pertahanan."
    ),
    "Kapak Besar": Weapon(
        name="Kapak Besar",
        category="Kapak",
        attack_bonus=10,
        defense_bonus=0,
        agility_bonus=-2,
        description="Senjata berat dengan serangan tinggi tapi mengurangi kelincahan."
    ),
    "Belati": Weapon(
        name="Belati",
        category="Belati",
        attack_bonus=3,
        defense_bonus=0,
        agility_bonus=4,
        description="Senjata kecil yang sangat cepat dan meningkatkan kelincahan."
    )
}
