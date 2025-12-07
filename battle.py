import random
import discord
from discord.ui import View, Button

class BattleActionView(View):
    def __init__(self, player, monster, ctx):
        super().__init__(timeout=120)
        self.player = player
        self.monster = monster
        self.ctx = ctx
        self.result_message = None
        self.action_chosen = None
        self.user_id = ctx.author.id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Ini bukan giliranmu!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.result_message:
            await self.result_message.edit(view=self)

    @discord.ui.button(label="Serangan Biasa", style=discord.ButtonStyle.primary)
    async def normal_attack(self, interaction: discord.Interaction, button: Button):
        await self.handle_action(interaction, "normal_attack")

    @discord.ui.button(label="Menangkis", style=discord.ButtonStyle.secondary)
    async def block(self, interaction: discord.Interaction, button: Button):
        await self.handle_action(interaction, "block")

    @discord.ui.button(label="Menghindar", style=discord.ButtonStyle.secondary)
    async def dodge(self, interaction: discord.Interaction, button: Button):
        await self.handle_action(interaction, "dodge")

    @discord.ui.button(label="Skill", style=discord.ButtonStyle.success)
    async def skill(self, interaction: discord.Interaction, button: Button):
        await self.handle_action(interaction, "skill")

    @discord.ui.button(label="Item Konsumsi", style=discord.ButtonStyle.secondary)
    async def item(self, interaction: discord.Interaction, button: Button):
        await self.handle_action(interaction, "item")

    async def handle_action(self, interaction: discord.Interaction, action: str):
        self.action_chosen = action
        await interaction.response.defer()
        await self.process_turn(interaction)

    async def process_turn(self, interaction: discord.Interaction):
        p = self.player
        m = self.monster
        text = ""

        # Player action
        if self.action_chosen == "normal_attack":
            damage = max(p.attack - m.defense, 1)
            m.hp -= damage
            m.hp = max(m.hp, 0)
            text += f"**{p.name}** menyerang **{m.name}** dengan serangan biasa dan memberikan {damage} damage!\n"

        elif self.action_chosen == "block":
            text += f"**{p.name}** menangkis serangan berikutnya!\n"

        elif self.action_chosen == "dodge":
            text += f"**{p.name}** bersiap menghindar serangan berikutnya!\n"

        elif self.action_chosen == "skill":
            damage = max(int(p.attack * 1.5) - m.defense, 1)
            m.hp -= damage
            m.hp = max(m.hp, 0)
            text += f"**{p.name}** menggunakan skill dan memberikan {damage} damage ke **{m.name}**!\n"

        elif self.action_chosen == "item":
            if p.inventory.get("potion", 0) > 0:
                heal_amount = 30
                p.hp += heal_amount
                if p.hp > p.max_hp:
                    p.hp = p.max_hp
                p.inventory["potion"] -= 1
                text += f"**{p.name}** menggunakan potion dan sembuh {heal_amount} HP! (HP sekarang: {p.hp})\n"
            else:
                text += f"**{p.name}** tidak memiliki potion!\n"

        # Check monster death
        if m.hp == 0:
            text += f"**{m.name}** kalah! Kamu mendapatkan EXP.\n"
            leveled_up = p.gain_exp(m.level * 20)
            if leveled_up:
                text += f"Selamat! Kamu naik ke level {p.level}!\n"
            embed = discord.Embed(title="Pertarungan Selesai", description=text, color=discord.Color.green())
            await interaction.followup.send(embed=embed)
            self.stop()
            return

        # Monster turn
        damage_to_player = 0
        flee_chance = p.flee
        block_active = False
        dodge_active = False

        if self.action_chosen == "block":
            block_active = True
        if self.action_chosen == "dodge":
            dodge_active = True
            flee_chance += 20

        if dodge_active and random.randint(1, 100) <= flee_chance:
            text += f"**{p.name}** berhasil menghindari serangan **{m.name}**!\n"
        else:
            if block_active:
                damage_to_player = max(m.attack - p.defense * 2, 0)
            else:
                damage_to_player = max(m.attack - p.defense, 1)
            p.hp -= damage_to_player
            p.hp = max(p.hp, 0)
            text += f"**{m.name}** menyerang dan memberikan {damage_to_player} damage! (HP kamu: {p.hp})\n"

        # Check player death
        if p.hp == 0:
            text += f"**{p.name}** kalah dalam pertarungan...\n"
            embed = discord.Embed(title="Pertarungan Selesai", description=text, color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            self.stop()
            return

        # Show status
        embed = discord.Embed(title="Giliran Pertarungan", color=discord.Color.orange())
        embed.add_field(name=p.name, value=f"HP: {p.hp}/{p.max_hp}\nLevel: {p.level}\nEXP: {p.exp}/{p.exp_to_next}", inline=True)
        embed.add_field(name=m.name, value=f"HP: {m.hp}/{m.max_hp}\nLevel: {m.level}", inline=True)
        embed.set_footer(text="Pilih aksi kamu:")

        for child in self.children:
            child.disabled = False

        self.result_message = await interaction.followup.send(content=text, embed=embed, view=self)
