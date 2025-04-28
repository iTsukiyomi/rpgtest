from dis import disco
import discord
from redbot.core import commands, Config
from redbot.core.bot import Red
from typing import Dict, Any, Optional

from .config import rpgconfig
from .player import PlayerManager

class RPG(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot

        self.config_manager = rpgconfig(self)
        self.player_manager = PlayerManager(self)
    
    @commands.command(name="reset", hidden=True)
    async def reset(self, ctx, user: discord.Member):
        await self.config_manager.del_user(user.id)
        await ctx.send(f"restted {user.display_name}")
        await ctx.send("rip")


    @commands.group(name="rpg")
    async def rpg(self, ctx):
        pass
    @rpg.command(name="start")
    async def rpg_start(self,ctx: commands.Context, name:str):
        """start yur crazy jurney"""
        if name is  None:
            await ctx.send('PUT YUR NAME')
            return
        result = await self.player_manager.create_player(ctx.author.id, name)
        await ctx.send(result)

    @rpg.command(name="profile")
    async def rpg_profile(self, ctx):
        """shows yur profile ofc.."""
        profile_embed = await self.player_manager.get_profile_embed(ctx.author.id)
        if isinstance(profile_embed, str):
            await ctx.send(profile_embed)
        else:
            await ctx.send(embed = profile_embed)

    @rpg.command(name="families")
    async def show_family(self,ctx):
        """shows all the available families and their passives."""
        file = discord.File(r"C:\Users\Asus\Desktop\prac\rpg\family-chart.png", filename="family-chart.png")

        e = discord.Embed(
            title="Family Passives",
            description="View the different family bonuses by rarity level",
            color=discord.Color.dark_gold()
        )
        e.set_image(url="attachment://family-chart.png")
        await ctx.send(file=file, embed=e)
    