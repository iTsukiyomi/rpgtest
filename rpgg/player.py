import discord
import random
import time
from typing import Dict, Any, List, Union, Tuple
from datetime import datetime, timedelta
from redbot.core.bot import Red

from .config import rpgconfig

class PlayerManager:
    def __init__(self,cog):
        self.cog  = cog
        self.config = rpgconfig(self.cog)

    async def create_player(self, user_id:int, name:str):
        if await self.config.user_exists(user_id):
            return "You already hab a character brehhhhh"
        family = await self._assign_random_family()
        await self.config.create_user(user_id,name,family)
        family_data = (await self.config.get_family_list())[family]

        player_data = await self.config.get_user_data(user_id)

        special_stats = {}

        for key in list(player_data.keys()):
            if key not in ['name', 'family', 'level', 'exp', 'gold', 'stats', 'inventory', 'equipped', 'skills', 'story_progress', 'quest_completed', 'reset_timestamp']:
                if isinstance(player_data[key], int ) and player_data[key] > 0:
                    special_stats[key] = player_data[key]
        if special_stats:
            for key, value in special_stats.items():
                await self.config.update_user_field(user_id,key,value)

        return f"Welcome to the world, `{name}` of the `{family.capitalize()}` family! " \
               f"Your family grants you: `{family_data['passive']}`. " \
               f"Your journey begins! Use `;rpg profile` to see your stats."
    

    async def _assign_random_family(self) -> str:
        families = await self.config.get_family_list()

        family_groups={
            "common":[],
            "rare":[],
            "epic":[],
            "legendary":[],
            "ultra":[]
        }

        for name,data in families.items():
            family_groups[data["rarity"]].append(name)
        weights = [70, 20,7,2.9,0.1]
        rarity_roll = random.choices(["common", "rare", "epic", "legendary","ultra"], weights=weights)[0]
        return random.choice(family_groups[rarity_roll])
    
    async def get_profile_embed(self, user_id : int) -> Union[discord.Embed, str]:
        if not await self.config.user_exists(user_id):
            return "bro atleast start first with ;rpg start"
        player_data = await self.config.get_user_data(user_id)
        families = await self.config.get_family_list()
        family_name = player_data['family']

        if not family_name or family_name not in families:
            family_name = await self._assign_random_family()
            await self.config.update_user_field(user_id, "family", family_name)

        family_rarity = families[family_name]['rarity']

        modified_stats = await self._calculate_stats_with_passives(player_data)
        base_stats = player_data['stats']

        e = discord.Embed(
            title=f"{player_data['name']}'s profile",
            description=f"Level {player_data['level']}, adventurer of {player_data['family'].capitalize()} family",
            color=self._get_rarity_color(family_rarity)
        )

        stats_txt = ""
        for stat_name, base_value in base_stats.items():
            modified_value = modified_stats[stat_name]

            if modified_value > base_value:
                stats_txt += f"{self._get_stat_emoji(stat_name)} {stat_name.capitalize()}: {base_value} -> **{modified_value}**\n"
            else:
                stats_txt += f"{self._get_stat_emoji(stat_name)} {stat_name.capitalize()}: {base_value}\n"
            
        e.add_field(name="Stats", value=stats_txt)
        
        special_bonus = self._get_special_bonus(player_data)
        if special_bonus:
            e.add_field(name="Special bonus", value=special_bonus, inline=False)

        
        next_lvl_xp = self._calculate_next_level_exp(player_data["level"])
        e.add_field(
            name="Progression",
            value=f"Exp: {player_data['exp']}/{next_lvl_xp}\n"
                  f"Gold: {player_data['gold']}\n"
                  f"Story progress: chap {player_data['story_progress']}"
        )
        e.add_field(
            name='Family legacy',
            value=f"passives: {families[family_name]['passive']}",
            inline=False
        )
        return e
    
    def _get_stat_emoji(self, stat_name:str) -> str:
        emojis = {
            "health": "❤️",
            "attack": "⚔️",
            "defense": "🛡️",
            "speed": "⚡",
            "magic": "✨"
        }
        return emojis.get(stat_name, "📊")
    
    def _get_special_bonus(self,player_data:dict)-> str:
        special_stats = []
        for stat_name, value in player_data.items():
            if stat_name in ['magic_find', 'energy_regen', 'exp_bonus', 'dodge_chance', 
                           'spell_crit', 'melee_crit', 'life_drain', 'rare_drop_chance',
                           'elemental_damage', 'elemental_resistance', 'critical_damage',
                           'stealth_chance', 'attack_speed', 'lightning_chain', 'skill_potency',
                           'cooldown_reduction', 'damage_negate', 'damage_bonus', 'fear_chance',
                           'double_action', 'reality_bend']:
                if value > 0:
                    formatted_name = ''.join(word.capitalize() for word in stat_name.split('_'))
                    special_stats.append(f"{formatted_name}: +{value}%")
        return '\n'.join(special_stats) if special_stats else ""


    def _get_rarity_color(self, rarity: str) -> discord.Color:
        colors = {
            "common": discord.Color.light_grey(),
            "rare": discord.Color.blue(),
            "epic": discord.Color.purple(),
            "legendary": discord.Color.gold(),
            "ultra": discord.Color(0xFF5733) 
        }
        return colors.get(rarity, discord.Color.default())
    
    def _calculate_next_level_exp(self, current_level: int) -> int:
        return 100 * (current_level ** 2)
    
    async def _calculate_stats_with_passives(self,player_data: dict) -> dict:
        base_stats = player_data['stats'].copy()
        modified_stats = base_stats.copy()
        family_name = player_data['family']
        families = await self.config.get_family_list()

        if not family_name or family_name not in families:
            return base_stats
        family_data = families[family_name]
        passive = family_data['passive']

        if family_name == "earthen":
            modified_stats['defense'] = int(base_stats['defense'] * 1.05)
        elif family_name == "swift":
            modified_stats['speed'] = int(base_stats['speed'] * 1.05)
        elif family_name == "bright":
            player_data['magic_find'] = player_data.get('magic_find', 0) + 5
        elif family_name == "hearty":
            modified_stats['health'] = int(base_stats['health'] * 1.05)
        elif family_name == "focused":
            player_data['energy_regen'] = player_data.get('energy_regen', 0) + 5
        elif family_name == "strong":
            modified_stats['attack'] = int(base_stats['attack'] * 1.05)
        elif family_name == "skilled":
            player_data['exp_bonus'] = player_data.get('exp_bonus', 0) + 5

        elif family_name == "stoneheart":
            modified_stats['defense'] = int(base_stats['defense'] * 1.10)
            modified_stats['health'] = int(base_stats['health'] * 1.05)
        elif family_name == "shadowstep":
            modified_stats['speed'] = int(base_stats['speed'] * 1.10)
            player_data['dodge_chance'] = player_data.get('dodge_chance', 0) + 5
        elif family_name == "flamecaster":
            player_data['magic_damage'] = player_data.get('magic_damage', 0) + 10
            player_data['spell_crit'] = player_data.get('spell_crit', 0) + 5
        elif family_name == "irongrip":
            player_data['physical_damage'] = player_data.get('physical_damage', 0) + 10
            player_data['melee_crit'] = player_data.get('melee_crit', 0) + 5
        elif family_name == "lifeblood":
            player_data['healing_received'] = player_data.get('healing_received', 0) + 10
            player_data['life_drain'] = player_data.get('life_drain', 0) + 5
        elif family_name == "starseer":
            player_data['magic_find'] = player_data.get('magic_find', 0) + 10
            player_data['rare_drop_chance'] = player_data.get('rare_drop_chance', 0) + 5

        elif family_name == "dragonkin":
            player_data['elemental_damage'] = player_data.get('elemental_damage', 0) + 15
            player_data['elemental_resistance'] = player_data.get('elemental_resistance', 0) + 10
        elif family_name == "nightstalker":
            player_data['critical_damage'] = player_data.get('critical_damage', 0) + 15
            player_data['stealth_chance'] = player_data.get('stealth_chance', 0) + 10
        elif family_name == "stormlord":
            player_data['attack_speed'] = player_data.get('attack_speed', 0) + 15
            player_data['lightning_chain'] = player_data.get('lightning_chain', 0) + 10
        elif family_name == "worldshaper":
            player_data['skill_potency'] = player_data.get('skill_potency', 0) + 15
            player_data['cooldown_reduction'] = player_data.get('cooldown_reduction', 0) + 10

        elif family_name == "celestial":
            for stat in modified_stats:
                modified_stats[stat] = int(base_stats[stat] * 1.20)
            player_data['damage_negate'] = player_data.get('damage_negate', 0) + 15
        elif family_name == "abyssal":
            player_data['damage_bonus'] = player_data.get('damage_bonus', 0) + 20
            player_data['fear_chance'] = player_data.get('fear_chance', 0) + 15
        elif family_name == "timeless":
            player_data['cooldown_reduction'] = player_data.get('cooldown_reduction', 0) + 20
            player_data['double_action'] = player_data.get('double_action', 0) + 15

        elif family_name == "primordial":
            for stat in modified_stats:
                modified_stats[stat] = int(base_stats[stat] * 1.25)
            player_data['reality_bend'] = player_data.get('reality_bend', 0) + 20

        return modified_stats
    