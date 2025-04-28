from redbot.core import Config
from typing import Dict, Any, Optional, List

class rpgconfig:
    def __init__(self,cog):
        self.cog = cog
        self.config = Config.get_conf(cog, identifier=699659)

        self._register_defaults()

    def _register_defaults(self):

        global_defaults = {
            "families": {
                "earthen": {"rarity": "common", "passive": "5% increased defense"},
                "swift": {"rarity": "common", "passive": "5% increased speed"},
                "bright": {"rarity": "common", "passive": "5% increased magic find"},
                "hearty": {"rarity": "common", "passive": "5% increased max health"},
                "focused": {"rarity": "common", "passive": "5% increased energy regen"},
                "strong": {"rarity": "common", "passive": "5% increased attack"},
                "skilled": {"rarity": "common", "passive": "5% increased experience gain"},

                "stoneheart": {"rarity": "rare", "passive": "10% increased defense, 5% max health"},
                "shadowstep": {"rarity": "rare", "passive": "10% increased speed, 5% dodge chance"},
                "flamecaster": {"rarity": "rare", "passive": "10% increased magic damage, 5% spell crit"},
                "irongrip": {"rarity": "rare", "passive": "10% increased physical damage, 5% melee crit"},
                "lifeblood": {"rarity": "rare", "passive": "10% increased healing received, 5% life drain"},
                "starseer": {"rarity": "rare", "passive": "10% increased magic find, 5% rare drop chance"},
                
                "dragonkin": {"rarity": "epic", "passive": "15% increased all elemental damage, 10% elemental resistance"},
                "nightstalker": {"rarity": "epic", "passive": "15% increased critical damage, 10% stealth chance"},
                "stormlord": {"rarity": "epic", "passive": "15% increased attack speed, 10% chance to chain lightning"},
                "worldshaper": {"rarity": "epic", "passive": "15% increased skill potency, 10% reduced cooldowns"},

                "celestial": {"rarity": "legendary", "passive": "20% increased all stats, 15% chance to negate damage"},
                "abyssal": {"rarity": "legendary", "passive": "20% increased damage, 15% chance to cause fear"},
                "timeless": {"rarity": "legendary", "passive": "20% cooldown reduction, 15% chance for double action"},

                "primordial": {"rarity": "ultra", "passive": "25% increased all stats, 20% chance to bend reality"}
            },

            "weapons": {},
            "artifacts":{},
            "story_chapters":{}
        }

        user_defaults = {
            "name": "",
            "family": "",
            "level": 1,
            "exp": 0,
            "gold": 100,
            "stats":{
                "health":100,
                "attack":10,
                "defense":5,
                "speed":5,
                "magic":5
            },
            "inventory":{
                "weapons":[],
                "artifacts":[],
                "items":[]
            },
            "equipped":{
                "weapon":"",
                "artifacts":[]
            },
            "skills":[],
            "story_progress":0,
            "quest_completed":[],
            "reset_timestamp":0
        }

        self.config.register_global(**global_defaults)
        self.config.register_user(**user_defaults)

    async def get_family_list(self) -> Dict[str, Dict[str, any]]:
        return await self.config.families()
    
    async def get_user_data(self, user_id : int) -> Dict[str, any]:
        user_data = await self.config.user_from_id(user_id).all()
        return user_data
    
    async def user_exists(self, user_id : int) -> bool:
        user_data = await self.config.user_from_id(user_id).name()
        return bool(user_data)
    
    async def create_user(self, user_id : int, name : str, family :str) -> None:
        user_conf = self.config.user_from_id(user_id)
        await user_conf.name.set(name)
        await user_conf.family.set(family)

    async def update_user_field(self, user_id:int, field:str,value:Any) -> None:
        user_conf = self.config.user_from_id(user_id)
        await user_conf.set_raw(field,value=value)
    async def del_user(self, user_id:int):
        await self.config.user_from_id(user_id).clear()