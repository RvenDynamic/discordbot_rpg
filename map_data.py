areas = {
    "Kota Awal": {
        "description": "Kota Pemula yang aman, tidak ada monster di sini. HP kamu akan sembuh penuh saat berada di kota.",
        "monsters": [],
        "level_range": (0, 0),
        "connections": ["Hutan Hijau", "Lembah Berangin"],
        "npcs": ["Alchemist", "Blacksmith"]
    },
    "Hutan Hijau": {
        "description": "Hutan Hijau, penuh monster level 1-5.",
        "monsters": ["Goblin", "Serigala", "Tikus Raksasa"],
        "level_range": (1, 5),
        "connections": ["Kota Awal", "Gunung Terjal"]
    },
    "Lembah Berangin": {
        "description": "Lembah Berangin, monster level 6-10.",
        "monsters": ["Orc", "Harimau", "Zombie"],
        "level_range": (6, 10),
        "connections": ["Kota Awal", "Rawa Berbahaya"]
    },
    "Gunung Terjal": {
        "description": "Gunung Terjal, monster level 11-15.",
        "monsters": ["Naga Muda", "Troll", "Serigala Hitam"],
        "level_range": (11, 15),
        "connections": ["Hutan Hijau"]
    },
    "Rawa Berbahaya": {
        "description": "Rawa Berbahaya, monster level 16-20.",
        "monsters": ["Laba-laba Raksasa", "Kodok Beracun", "Hantu"],
        "level_range": (16, 20),
        "connections": ["Lembah Berangin", "Kastil Kegelapan"]
    },
    "Kastil Kegelapan": {
        "description": "Area bos level 25. Tempat tinggal sang Raja Kegelapan.",
        "monsters": ["Raja Kegelapan"],
        "level_range": (25, 25),
        "connections": ["Rawa Berbahaya"]
    }
}
