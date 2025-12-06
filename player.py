from equipment import weapons
from potion import potions  # pastikan file potion.py ada dan import benar
from equipment import Weapon  # import class Weapon untuk tipe senjata

class Player:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.level = 1
        self.exp = 0
        self.exp_to_next = 100

        self.strength = 5
        self.vitality = 5
        self.agility = 5

        self.inventory = {}  # item biasa, contoh: {"item1": 2}
        self.potions = {"Potion Penyembuh": 3}  # contoh potion awal
        self.weapons = []  # list objek Weapon
        self.locked_items = {}  # item_name: bool, True = terkunci
        self.location = "Kota Awal"

        self.status_points = 0  # point status yang belum dialokasikan
        self.weapon = None  # objek Weapon yang dipakai player
        self.weapon_category = None

        self.recalculate_stats()
        self.hp = self.max_hp  # set hp penuh saat awal

    def gain_exp(self, amount):
        self.exp += amount
        leveled_up = False
        while self.exp >= self.exp_to_next:
            self.exp -= self.exp_to_next
            self.level += 1
            self.exp_to_next = int(self.exp_to_next * 1.5)

            self.status_points += 2  # dapat 2 point status tiap level up

            leveled_up = True
        if leveled_up:
            self.recalculate_stats()
            self.hp = self.max_hp
        return leveled_up

    def recalculate_stats(self):
        # Hitung ulang stats dasar
        self.max_hp = 100 + self.vitality * 10
        # Hitung bonus senjata jika ada
        attack_bonus = self.weapon.attack_bonus if self.weapon else 0
        defense_bonus = self.weapon.defense_bonus if self.weapon else 0
        flee_bonus = self.weapon.agility_bonus if self.weapon else 0

        self.attack = 10 + self.strength * 2 + attack_bonus
        self.defense = 5 + self.vitality * 2 + defense_bonus
        self.flee = min(self.agility * 2 + flee_bonus, 50)

        # Jangan turunkan hp jika sudah di bawah max_hp
        if hasattr(self, 'hp') and self.hp > self.max_hp:
            self.hp = self.max_hp

    def allocate_point(self, attr, points):
        if points > self.status_points:
            return False, "Point tidak cukup."
        if attr == "str":
            self.strength += points
        elif attr == "vit":
            self.vitality += points
        elif attr == "agi":
            self.agility += points
        else:
            return False, "Atribut tidak valid. Gunakan str, vit, atau agi."
        self.status_points -= points
        self.recalculate_stats()
        return True, f"Berhasil menambahkan {points} point ke {attr.upper()}."

    def set_weapon(self, weapon_name):
        # Cari objek Weapon di self.weapons berdasarkan nama
        for wpn in self.weapons:
            if wpn.name == weapon_name:
                self.weapon = wpn
                self.weapon_category = wpn.category
                self.recalculate_stats()
                return True, f"Senjata diganti menjadi {weapon_name}."
        return False, "Senjata tidak ditemukan di inventory."

    def add_weapon(self, weapon_name):
        # Tambah senjata ke inventory weapons jika ada di weapons dict
        if weapon_name in weapons:
            wpn_obj = weapons[weapon_name]
            self.weapons.append(wpn_obj)
            return True, f"Senjata {weapon_name} ditambahkan ke inventory."
        else:
            return False, "Senjata tidak dikenal."

    def use_item(self, item_name):
        # Gunakan potion
        if item_name in self.potions and self.potions[item_name] > 0:
            potion_obj = potions.get(item_name)
            if not potion_obj:
                return False, "Potion tidak ditemukan."
            # Contoh efek potion penyembuh
            if potion_obj.heal > 0:
                self.hp = min(self.hp + potion_obj.heal, self.max_hp)
                self.potions[item_name] -= 1
                if self.potions[item_name] == 0:
                    del self.potions[item_name]
                return True, f"Potion {item_name} digunakan, HP bertambah {potion_obj.heal}!"
            # Bisa ditambah efek lain sesuai kategori potion
            # Contoh sederhana:
            self.potions[item_name] -= 1
            if self.potions[item_name] == 0:
                del self.potions[item_name]
            return True, f"Potion {item_name} digunakan."
        
        # Gunakan item biasa
        elif item_name in self.inventory and self.inventory[item_name] > 0:
            # Contoh: item biasa belum ada efek khusus
            self.inventory[item_name] -= 1
            if self.inventory[item_name] == 0:
                del self.inventory[item_name]
            return True, f"Item {item_name} digunakan."
        
        # Gunakan senjata (ganti senjata aktif)
        elif any(wpn.name == item_name for wpn in self.weapons):
            return self.set_weapon(item_name)
        
        else:
            return False, "Item tidak bisa digunakan atau tidak ada di inventory."

    def add_flux(self, amount):
        if amount < 0:
            return False, "Jumlah harus positif."
        self.flux += amount
        return True, f"Flux bertambah {amount}. Total flux: {self.flux}"

    def spend_flux(self, amount):
        if amount < 0:
            return False, "Jumlah harus positif."
        if self.flux < amount:
            return False, "Flux tidak cukup."
        self.flux -= amount
        return True, f"Flux berkurang {amount}. Sisa flux: {self.flux}"

    def heal_full(self):
        self.hp = self.max_hp