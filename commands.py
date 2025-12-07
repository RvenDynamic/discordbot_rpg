import discord
from discord.ext import commands
from discord.ui import View, Button, Select
from equipment import weapons
from potion import potions
import random

from player import Player
from equipment import Weapon
from monster import Monster, Boss
from map_data import areas
from battle import BattleActionView

players = {}

def setup(bot):

    @bot.command()
    async def start(ctx):
        user_id = ctx.author.id
        if user_id in players:
            await ctx.send(f"{ctx.author.mention}, kamu sudah memiliki karakter.")
            return

        # Buat player baru dengan user_id dan nama discord
        players[user_id] = Player(user_id, ctx.author.name)

        class WeaponSelectView(View):
            def __init__(self):
                super().__init__(timeout=60)
                self.user_id = ctx.author.id

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                if interaction.user.id != self.user_id:
                    await interaction.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                    return False
                return True

            @discord.ui.button(label="Pedang 1 Tangan", style=discord.ButtonStyle.primary)
            async def sword(self, interaction: discord.Interaction, button: Button):
                players[user_id].set_weapon("Pedang 1 Tangan")
                await interaction.response.edit_message(content=f"{ctx.author.mention}, kamu memilih **Pedang 1 Tangan** sebagai senjatamu! Karakter siap digunakan.", view=None)

            @discord.ui.button(label="Busur", style=discord.ButtonStyle.success)
            async def bow(self, interaction: discord.Interaction, button: Button):
                players[user_id].set_weapon("Busur")
                await interaction.response.edit_message(content=f"{ctx.author.mention}, kamu memilih **Busur** sebagai senjatamu! Karakter siap digunakan.", view=None)

            @discord.ui.button(label="Tongkat", style=discord.ButtonStyle.secondary)
            async def staff(self, interaction: discord.Interaction, button: Button):
                players[user_id].set_weapon("Tongkat")
                await interaction.response.edit_message(content=f"{ctx.author.mention}, kamu memilih **Tongkat** sebagai senjatamu! Karakter siap digunakan.", view=None)

        view = WeaponSelectView()
        await ctx.send(f"{ctx.author.mention}, pilih senjata untuk karaktermu:", view=view)

    @bot.command()
    async def status(ctx):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]
        embed = discord.Embed(title=f"Status {p.name}", color=discord.Color.blue())
        embed.add_field(name="Level", value=p.level)
        embed.add_field(name="HP", value=f"{p.hp}/{p.max_hp}")
        embed.add_field(name="Attack", value=p.attack)
        embed.add_field(name="Defense", value=p.defense)
        embed.add_field(name="EXP", value=f"{p.exp}/{p.exp_to_next}")
        embed.add_field(name="STR (Strength)", value=p.strength)
        embed.add_field(name="VIT (Vitality)", value=p.vitality)
        embed.add_field(name="AGI (Agility)", value=p.agility)
        embed.add_field(name="Flee (Menghindar)", value=f"{p.flee}%")
        embed.add_field(name="Lokasi", value=p.location)
        embed.add_field(name="Potion", value=p.inventory.get("potion", 0))
        embed.add_field(name="Flux", value=p.flux)
        embed.add_field(name="Point Status Tersisa", value=p.status_points)
        embed.add_field(name="Senjata", value=p.weapon if p.weapon else "Belum memilih senjata")
        await ctx.send(embed=embed)

    @bot.command()
    async def allocate(ctx, attr: str = None, points: int = 1):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]

        if p.status_points == 0:
            await ctx.send(f"{ctx.author.mention}, kamu tidak memiliki point status yang bisa dialokasikan.")
            return

        if attr is None:
            await ctx.send(f"{ctx.author.mention}, gunakan command dengan format: `!allocate <str|vit|agi> [jumlah]`")
            return

        attr = attr.lower()
        if points < 1:
            await ctx.send(f"{ctx.author.mention}, jumlah point harus minimal 1.")
            return

        success, msg = p.allocate_point(attr, points)
        if success:
            await ctx.send(f"{ctx.author.mention}, {msg} Point status tersisa: {p.status_points}.")
        else:
            await ctx.send(f"{ctx.author.mention}, gagal: {msg}")

    @bot.command()
    async def location(ctx):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]

        current_area = p.location
        area_info = areas[current_area]

        embed = discord.Embed(
            title=f"Pilih Lokasi Baru (Saat ini: {current_area})",
            description=area_info["description"],
            color=discord.Color.blue()
        )

        # Tampilkan deskripsi area terhubung
        connected_areas = area_info.get("connections", [])
        for area in connected_areas:
            embed.add_field(name=area, value=areas[area]["description"], inline=False)

        # Tampilkan NPC jika ada
        npcs = area_info.get("npcs", [])

        if npcs:
            embed.add_field(name="NPC Tersedia", value=", ".join(npcs), inline=False)

        view = View(timeout=120)

        # Tombol pindah area
        def make_move_callback(area_name):
            async def callback(interaction: discord.Interaction):
                if interaction.user.id != user_id:
                    await interaction.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                    return
                p.location = area_name
                if area_name == "Kastil Kegelapan":
                    await interaction.response.edit_message(
                        content=f"Anda memasuki area bos **Raja Kegelapan** (Level 25), harap berhati-hati dan direkomendasikan untuk memiliki party untuk melakukan battle.",
                        embed=None, view=None)
                elif area_name == "Kota Awal":
                    p.heal_full()
                    await interaction.response.edit_message(
                        content=f"Kamu pindah ke **{area_name}** dan HP kamu telah sembuh penuh!",
                        embed=None, view=None)
                else:
                    await interaction.response.edit_message(
                        content=f"Kamu pindah ke **{area_name}**. Bersiaplah berburu monster!",
                        embed=None, view=None)
            return callback

        for area_name in connected_areas:
            btn = Button(label=f"Pindah ke {area_name}", style=discord.ButtonStyle.primary)
            btn.callback = make_move_callback(area_name)
            view.add_item(btn)

        # Tombol interaksi NPC
        def make_npc_callback(npc_name):
            async def callback(interaction: discord.Interaction):
                if interaction.user.id != user_id:
                    await interaction.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                    return
                if npc_name == "Alchemist":
                    await show_alchemist(interaction, p)
                elif npc_name == "Blacksmith":
                    await show_blacksmith(interaction, p)
                else:
                    await interaction.response.send_message(f"NPC {npc_name} belum tersedia.", ephemeral=True)
            return callback

        for npc_name in npcs:
            btn = Button(label=f"Interaksi dengan {npc_name}", style=discord.ButtonStyle.secondary)
            btn.callback = make_npc_callback(npc_name)
            view.add_item(btn)

        await ctx.send(embed=embed, view=view)

    async def show_alchemist(interaction, player):
        embed = discord.Embed(
            title="Alchemist",
            description="Selamat datang di Alchemist! Kamu bisa membeli, menjual, dan membuat potion di sini.",
            color=discord.Color.purple()
        )
        embed.add_field(name="Potion", value="Harga beli: 50 flux\nHarga jual: 25 flux", inline=False)

        view = View(timeout=120)

        # Tombol beli potion (beli Potion Penyembuh default)
        btn_buy = Button(label="Beli Potion Penyembuh (50 flux)", style=discord.ButtonStyle.green)
        async def buy_callback(inter):
            if inter.user.id != player.user_id:
                await inter.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                return
            success, msg = player.spend_flux(50)
            if not success:
                await inter.response.send_message(msg, ephemeral=True)
                return
            player.potions["Potion Penyembuh"] = player.potions.get("Potion Penyembuh", 0) + 1
            await inter.response.edit_message(content=f"Kamu membeli 1 Potion Penyembuh seharga 50 flux.", embed=None, view=None)
        btn_buy.callback = buy_callback
        view.add_item(btn_buy)

        # Tombol jual potion (jual Potion Penyembuh default)
        btn_sell = Button(label="Jual Potion Penyembuh (25 flux)", style=discord.ButtonStyle.red)
        async def sell_callback(inter):
            if inter.user.id != player.user_id:
                await inter.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                return
            if player.potions.get("Potion Penyembuh", 0) < 1:
                await inter.response.send_message("Kamu tidak punya Potion Penyembuh untuk dijual.", ephemeral=True)
                return
            player.potions["Potion Penyembuh"] -= 1
            if player.potions["Potion Penyembuh"] == 0:
                del player.potions["Potion Penyembuh"]
            player.add_flux(25)
            await inter.response.edit_message(content=f"Kamu menjual 1 Potion Penyembuh dan mendapatkan 25 flux.", embed=None, view=None)
        btn_sell.callback = sell_callback
        view.add_item(btn_sell)

        # Select menu untuk memilih potion yang ingin dibuat
        options = []
        for pname, pobj in potions.items():
            options.append(discord.SelectOption(label=pname, description=pobj.description[:50]))

        select = Select(placeholder="Pilih potion yang ingin dibuat", options=options)

        async def select_callback(inter):
            if inter.user.id != player.user_id:
                await inter.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                return
            potion_name = select.values[0]
            # Contoh: crafting gratis tanpa bahan
            player.potions[potion_name] = player.potions.get(potion_name, 0) + 1
            await inter.response.edit_message(content=f"Kamu berhasil membuat 1 {potion_name}.", embed=None, view=None)
        select.callback = select_callback
        view.add_item(select)

        await interaction.response.send_message(embed=embed, view=view)

    async def show_blacksmith(interaction, player):
        embed = discord.Embed(
            title="Blacksmith",
            description="Selamat datang di Blacksmith! Kamu bisa membeli, menjual, dan membuat senjata di sini.",
            color=discord.Color.dark_grey()
        )
        weapons_shop = {
            "Pedang 1 Tangan": 200,
            "Busur": 250,
            "Tongkat": 300,
        }
        desc = ""
        for wpn, price in weapons_shop.items():
            desc += f"- {wpn}: Harga beli {price} flux\n"
        embed.add_field(name="Senjata Tersedia", value=desc, inline=False)

        view = View(timeout=120)

        # Tombol beli senjata (langsung beli dan pakai)
        for wpn, price in weapons_shop.items():
            btn = Button(label=f"Beli & Pakai {wpn} ({price} flux)", style=discord.ButtonStyle.green)
            async def buy_callback(inter, weapon=wpn, cost=price):
                if inter.user.id != player.user_id:
                    await inter.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                    return
                success, msg = player.spend_flux(cost)
                if not success:
                    await inter.response.send_message(msg, ephemeral=True)
                    return
                # Tambah senjata ke inventory jika belum ada
                if not any(w.name == weapon for w in player.weapons):
                    player.weapons.append(weapons[weapon])
                # Set senjata aktif
                player.set_weapon(weapon)
                await inter.response.edit_message(content=f"Kamu membeli dan memakai senjata **{weapon}** seharga {cost} flux.", embed=None, view=None)
            btn.callback = buy_callback
            view.add_item(btn)

        # Tombol jual senjata yang sedang dipakai (setengah harga)
        btn_sell = Button(label="Jual Senjata Saat Ini (setengah harga)", style=discord.ButtonStyle.red)
        async def sell_callback(inter):
            if inter.user.id != player.user_id:
                await inter.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                return
            if not player.weapon:
                await inter.response.send_message("Kamu belum memakai senjata apapun.", ephemeral=True)
                return
            sell_price = weapons_shop.get(player.weapon.name, 0) // 2
            # Hapus senjata dari inventory
            player.weapons = [w for w in player.weapons if w != player.weapon]
            player.weapon = None
            player.weapon_category = None
            player.recalculate_stats()
            player.add_flux(sell_price)
            await inter.response.edit_message(content=f"Kamu menjual senjata dan mendapatkan {sell_price} flux.", embed=None, view=None)
        btn_sell.callback = sell_callback
        view.add_item(btn_sell)

        # Select menu untuk memilih senjata yang ingin dibuat (craft)
        options = []
        for wpn_name in weapons_shop.keys():
            options.append(discord.SelectOption(label=wpn_name, description=weapons[wpn_name].description[:50]))

        select = Select(placeholder="Pilih senjata yang ingin dibuat", options=options)

        async def select_callback(inter):
            if inter.user.id != player.user_id:
                await inter.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                return
            weapon_name = select.values[0]
            # Crafting gratis, tambahkan ke inventory tanpa mengganti senjata aktif
            if not any(w.name == weapon_name for w in player.weapons):
                player.weapons.append(weapons[weapon_name])
                await inter.response.edit_message(content=f"Kamu berhasil membuat senjata **{weapon_name}** dan menambahkannya ke inventory.", embed=None, view=None)
            else:
                await inter.response.send_message(f"Kamu sudah memiliki senjata **{weapon_name}** di inventory.", ephemeral=True)
        select.callback = select_callback
        view.add_item(select)

        await interaction.response.send_message(embed=embed, view=view)

    class BossBattleView(View):
        def __init__(self):
            super().__init__(timeout=120)
            self.user_id = ctx.author.id
            self.boss = boss
            self.player = p
            self.battle_started = False

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Ini bukan giliranmu!", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="Status Bos", style=discord.ButtonStyle.secondary)
        async def status_boss(self, interaction: discord.Interaction, button: Button):
            embed = discord.Embed(title=f"Status Bos: {self.boss.name}", color=discord.Color.dark_red())
            embed.add_field(name="Level", value=self.boss.level)
            embed.add_field(name="HP", value=f"{self.boss.hp}/{self.boss.max_hp}")
            embed.add_field(name="Attack", value=self.boss.attack)
            embed.add_field(name="Defense", value=self.boss.defense)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        @discord.ui.button(label="Lawan", style=discord.ButtonStyle.danger)
        async def fight(self, interaction: discord.Interaction, button: Button):
            if self.battle_started:
                await interaction.response.send_message("Pertarungan sudah dimulai!", ephemeral=True)
                return
            self.battle_started = True
            view = BattleActionView(self.player, self.boss, ctx)
            await interaction.response.edit_message(content=f"Pertarungan dimulai melawan bos **{self.boss.name}**!", embed=None, view=view)

        @discord.ui.button(label="Lari", style=discord.ButtonStyle.secondary)
        async def run_away(self, interaction: discord.Interaction, button: Button):
            prev_area = "Rawa Berbahaya"
            p.location = prev_area
            await interaction.response.edit_message(content=f"Kamu melarikan diri dan pindah ke **{prev_area}**.", embed=None, view=None)
            self.stop()

    @bot.command()
    async def whereami(ctx):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]
        loc = p.location
        desc = areas[loc]["description"]
        await ctx.send(f"{ctx.author.mention}, kamu berada di **{loc}**.\n{desc}")

    @bot.command()
    async def hunt(ctx):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]

        current_area = p.location
        area_info = areas[current_area]

        if current_area == "Kota Awal":
            p.heal_full()
            await ctx.send(f"{ctx.author.mention}, kamu berada di **Kota Awal**. Tidak ada monster di sini dan HP kamu telah sembuh penuh.")
            return

        monster_name = random.choice(area_info["monsters"])
        min_lvl, max_lvl = area_info["level_range"]
        monster_level = random.randint(min_lvl, max_lvl)

        monster = Monster(monster_name, monster_level)

        embed = discord.Embed(title=f"Monster Ditemukan di {current_area}: {monster.name} (Level {monster.level})", color=discord.Color.red())
        embed.add_field(name="HP", value=f"{monster.hp}/{monster.max_hp}")
        embed.add_field(name="Attack", value=monster.attack)
        embed.add_field(name="Defense", value=monster.defense)
        embed.set_footer(text="Giliran kamu untuk bertindak!")

        view = BattleActionView(p, monster, ctx)
        message = await ctx.send(embed=embed, view=view)
        view.result_message = message

    @bot.command()
    async def inventory(ctx):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]

        inventory_entries = []

        # Senjata
        if hasattr(p, 'weapons') and p.weapons:
            for wpn_obj in p.weapons:
                wpn_name = getattr(wpn_obj, 'name', str(wpn_obj))
                locked = p.locked_items.get(wpn_name, False)
                inventory_entries.append(("Senjata", wpn_name, 1, locked))

        # Item biasa
        for item_name, qty in p.inventory.items():
            locked = p.locked_items.get(item_name, False)
            inventory_entries.append(("Item", item_name, qty, locked))

        # Potion
        for potion_name, qty in p.potions.items():
            locked = p.locked_items.get(potion_name, False)
            inventory_entries.append(("Potion", potion_name, qty, locked))

        if not inventory_entries:
            await ctx.send(f"{ctx.author.mention}, inventory kamu kosong.")
            return

        embed = discord.Embed(title=f"Inventory {p.name}", color=discord.Color.green())
        description_lines = []
        for idx, (typ, name, qty, locked) in enumerate(inventory_entries, start=1):
            lock_status = "🔒" if locked else ""
            description_lines.append(f"**{idx}.** [{typ}] {name} {lock_status} — Jumlah: {qty}")

        embed.description = "\n".join(description_lines)
        embed.set_footer(text="Gunakan command !use <nomor>, !delete <nomor>, atau !lock <nomor> untuk mengelola item, senjata, dan potion.")

        await ctx.send(embed=embed)

    @bot.command()
    async def use(ctx, nomor: int):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]

        inventory_entries = []

        # Senjata
        if hasattr(p, 'weapons') and p.weapons:
            for wpn_obj in p.weapons:
                wpn_name = getattr(wpn_obj, 'name', str(wpn_obj))
                inventory_entries.append(("Senjata", wpn_name))

        # Item biasa
        for item_name in p.inventory.keys():
            inventory_entries.append(("Item", item_name))

        # Potion
        for potion_name in p.potions.keys():
            inventory_entries.append(("Potion", potion_name))

        if nomor < 1 or nomor > len(inventory_entries):
            await ctx.send(f"{ctx.author.mention}, nomor item tidak valid.")
            return

        typ, name = inventory_entries[nomor - 1]

        if typ == "Senjata":
            success, msg = p.equip_weapon(name)
            await ctx.send(f"{ctx.author.mention}, {msg}")
        else:
            success, msg = p.use_item(name)
            await ctx.send(f"{ctx.author.mention}, {msg}")

    @bot.command()
    async def delete(ctx, nomor: int):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]

        inventory_entries = []

        # Senjata
        if hasattr(p, 'weapons') and p.weapons:
            for wpn_obj in p.weapons:
                wpn_name = getattr(wpn_obj, 'name', str(wpn_obj))
                inventory_entries.append(("Senjata", wpn_name))

        # Item biasa
        for item_name in p.inventory.keys():
            inventory_entries.append(("Item", item_name))

        # Potion
        for potion_name in p.potions.keys():
            inventory_entries.append(("Potion", potion_name))

        if nomor < 1 or nomor > len(inventory_entries):
            await ctx.send(f"{ctx.author.mention}, nomor item tidak valid.")
            return

        typ, name = inventory_entries[nomor - 1]

        if p.locked_items.get(name, False):
            await ctx.send(f"{ctx.author.mention}, {typ} **{name}** terkunci dan tidak bisa dihapus!")
            return

        if typ == "Senjata":
            # Hapus senjata dari list
            for i, wpn_obj in enumerate(p.weapons):
                if getattr(wpn_obj, 'name', None) == name:
                    p.weapons.pop(i)
                    await ctx.send(f"{ctx.author.mention}, senjata **{name}** telah dihapus dari inventory.")
                    return
            await ctx.send(f"{ctx.author.mention}, senjata tidak ditemukan.")
        elif typ == "Item":
            if name in p.inventory:
                p.inventory[name] -= 1
                if p.inventory[name] <= 0:
                    del p.inventory[name]
                await ctx.send(f"{ctx.author.mention}, item **{name}** telah dihapus dari inventory.")
            else:
                await ctx.send(f"{ctx.author.mention}, item tidak ditemukan di inventory.")
        else:  # Potion
            if name in p.potions:
                p.potions[name] -= 1
                if p.potions[name] <= 0:
                    del p.potions[name]
                await ctx.send(f"{ctx.author.mention}, potion **{name}** telah dihapus dari inventory.")
            else:
                await ctx.send(f"{ctx.author.mention}, potion tidak ditemukan di inventory.")

    @bot.command()
    async def lock(ctx, nomor: int):
        user_id = ctx.author.id
        if user_id not in players:
            await ctx.send(f"{ctx.author.mention}, kamu belum membuat karakter. Gunakan `!start` dulu.")
            return
        p = players[user_id]

        inventory_entries = []

        # Senjata
        if hasattr(p, 'weapons') and p.weapons:
            for wpn_obj in p.weapons:
                wpn_name = getattr(wpn_obj, 'name', str(wpn_obj))
                inventory_entries.append(("Senjata", wpn_name))

        # Item biasa
        for item_name in p.inventory.keys():
            inventory_entries.append(("Item", item_name))

        # Potion
        for potion_name in p.potions.keys():
            inventory_entries.append(("Potion", potion_name))

        if nomor < 1 or nomor > len(inventory_entries):
            await ctx.send(f"{ctx.author.mention}, nomor item tidak valid.")
            return

        typ, name = inventory_entries[nomor - 1]

        locked = p.locked_items.get(name, False)
        if locked:
            p.locked_items[name] = False
            await ctx.send(f"{ctx.author.mention}, {typ} **{name}** telah dibuka kuncinya.")
        else:
            p.locked_items[name] = True
            await ctx.send(f"{ctx.author.mention}, {typ} **{name}** telah dikunci dan tidak bisa dihapus.")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{ctx.author.mention}, command tidak ditemukan! Gunakan `!help` untuk melihat daftar command yang tersedia.")
        else:
            raise error
