from __future__ import annotations
from typing import List
from dataclasses import dataclass
from Options import OptionSet
from ..game import Game
from ..game_objective_template import GameObjectiveTemplate
from ..enums import KeymastersKeepGamePlatforms

hitman_meta = {
    "name": "Hitman: World of Assassination",
    "platforms": ["PC", "PS4", "PS5", "XONE", "XSX"],
    "after_dark": True,

    "optional_constraints": [
        "Play on DIFFICULTY difficulty",
        "Suit Only",
        "Silent Assassin",
        "No items found in map",
        "Only suits where 47 isn't bald"
    ],

    "objectives": {
        "hitman1": {
            "Paris": ["Viktor Novikov", "Dalia Margolis"],
            "Sapienza": ["Silvio Caruso", "Francesca De Santis"],
            "Marrakesh": ["Reza Zaydan", "Claus Hugo Strandberg"],
            "Bangkok": ["Jordan Cross", "Ken Morgan"],
            "Colorado": ["Sean Rose", "Ezra Berg", "Penelope Graves", "Maya Parvati"],
            "Hokkaido": ["Erich Soders", "Yuki Yamazaki"]
        },
        "hitman2": {
            "Hawkes Bay": ["Alma Reynard"],
            "Miami": ["Robert Knox", "Sierra Knox"],
            "Santa Fortuna": ["Rico Delgado", "Andrea Martinez", "Jorge Franco"],
            "Mumbai": ["Dawood Rangan", "Vanya Shah"],
            "Whittleton Creek": ["Janus", "Nolan Cassidy"],
            "Isle of Sgail": ["Sophia Washington", "Zoe Washington"],
            "New York": ["Athena Savalas"],
            "Haven Island": ["Tyson Williams", "Ljudmila Vetrova", "Steven Bradley"]
        },
        "hitman3": {
            "Dubai": ["Carl Ingram", "Marcus Stuyvesant"],
            "Dartmoor": ["Alexa Carlisle"],
            "Berlin": ["Any Agent"] * 5,
            "Chongqing": ["Hush", "Imogen Royce"],
            "Mendoza": ["Don Yates", "Tamara Vidal"],
            "Ambrose Island": ["Noel Crest", "Sinhi Venthan"]
        }
    },

    "data": {
        "DIFFICULTY": lambda: ["Professional", "Master"],

        "WEAPON1": lambda: [
            "Silenced Pistol",
            "Non-silenced Pistol",
            "Sword/Katana",
            "Knife Stab",
            "Fiber Wire",
            "Shuriken/Thrown Knife",
            "Emetic (Drowning)",
            "Lethal Poison",
            "Sedative (Snap Neck)",
            "Thrown Explosive",
            "Remote Explosive",
            "Proximity Explosive"
        ]
        # WEAPON2 - WEAPON5 are set below from the same list as above
    }
}

hitman_meta["data"]["WEAPON2"] = hitman_meta["data"]["WEAPON1"]
hitman_meta["data"]["WEAPON3"] = hitman_meta["data"]["WEAPON1"]
hitman_meta["data"]["WEAPON4"] = hitman_meta["data"]["WEAPON1"]
hitman_meta["data"]["WEAPON5"] = hitman_meta["data"]["WEAPON1"]

@dataclass
class Hitman3Options:
    pass

class Hitman3Game(Game):
    options_cls = Hitman3Options

    name = hitman_meta["name"]
    platform = KeymastersKeepGamePlatforms[hitman_meta["platforms"][0]]
    platforms_other = [KeymastersKeepGamePlatforms[p] for p in hitman_meta["platforms"][1:]]
    is_adult_only_or_unrated = hitman_meta["after_dark"] or False

    def _get_data_templates(self) -> dict:
        return {
            k: (v, 1) for k, v in hitman_meta["data"].items()
        }

    def optional_game_constraint_templates(self) -> List[GameObjectiveTemplate]:
        return [
            GameObjectiveTemplate(label=constraint, data=self._get_data_templates())
                for constraint in hitman_meta["optional_constraints"]
        ]

    def game_objective_templates(self) -> List[GameObjectiveTemplate]:
        objective_list = {}

        for campaign in hitman_meta["objectives"].keys():
            for loc, targets in hitman_meta["objectives"][campaign].items():
                objective_list[loc] = targets

        location = lambda name: f"[color=a8b4f0][b]{name}[/b][/color]"
        target = lambda name: f"[color=e6f0a8][b]{name}[/b][/color]"
        weapon = lambda tag: f"[color=db7d85][b]{tag}[/b][/color]"

        objectives = {
            map: ", ".join([f"{target(v)} with {weapon('WEAPON' + str(k+1))}" for k, v in enumerate(targets)])
                for map, targets in objective_list.items()
        }

        return [
            GameObjectiveTemplate(
                label=f"{location(map)}: {objective_label}",
                data=self._get_data_templates(), 
                is_time_consuming=False,
                is_difficult=False,
                weight=1
            ) for map, objective_label in objectives.items()
        ]
    
# Archipelago Options
# ...

