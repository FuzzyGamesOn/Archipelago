from .Regions import create_regions
from .Items import ManualItem, create_items
from .Rules import set_rules
from .Options import manual_options

from BaseClasses import ItemClassification, Tutorial
from worlds.AutoWorld import World, WebWorld, AutoWorldRegister
import worlds

class ManualWeb(WebWorld):
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up manual game integration for Archipelago multiworld games.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Fuzzy"]
    )]


class ManualWorld(World):
    """
    Manual games allow you to set custom check locations and custom item names that will be rolled into a multiworld.
    This allows any variety of game -- PC, console, board games, Microsoft Word memes... really anything -- to be part of a multiworld randomizer.
    The key component to including these games is some level of manual restriction. Since the items are not actually withheld from the player, 
    the player must manually refrain from using these gathered items until the tracker shows that they have been acquired or sent.
    """
    game: str = "Manual"
    web = ManualWeb()

    option_definitions = manual_options
    data_version = 0
    required_client_version = (0, 3, 4)

    create_items = create_items
    create_regions = create_regions
    set_rules = set_rules

    item_name_to_id = {}
    location_name_to_id = {}

    def pre_fill(self):
        victory = self.multiworld.get_location("Victory", self.player)
        victory.place_locked_item(ManualItem("Victory", ItemClassification.progression, None, self.player))

    def stage_generate_early(self):
        item_index = 1000000
        loc_index = 1000000
        item_name_to_id = {}
        location_name_to_id = {}
        for player in self.get_game_players("Manual"):
            for item in self.items[player].value:
                item_name = item["name"].split(":")[0]
                if item_name not in item_name_to_id:
                    item_name_to_id[item_name] = item_index
                    item_index += 1
            for location in self.locations[player].value:
                if location["name"] not in location_name_to_id:
                    location_name_to_id[location["name"]] = loc_index
                    loc_index += 1
            if self.filler_item_name[player].value not in item_name_to_id:
                item_name_to_id[self.filler_item_name[player].value] = item_index
                item_index += 1
        location_id_to_name = {}
        for location, id in location_name_to_id.items():
            location_id_to_name[id] = location
        item_id_to_name = {}
        for item, id in item_name_to_id.items():
            item_id_to_name[id] = item
        for world in [AutoWorldRegister.world_types["Manual"], *self.get_game_worlds("Manual")]:
            world.item_name_to_id = item_name_to_id
            world.location_name_to_id = location_name_to_id
            world.location_id_to_name = location_id_to_name
            world.item_id_to_name = item_id_to_name
        worlds.network_data_package["games"]["Manual"] = world.get_data_package_data()
    
    def fill_slot_data(self):
        # return {
        #     "DeathLink": bool(self.multiworld.death_link[self.player].value)
        # }

        pass

    def create_item(self, name):
        if name == self.multiworld.filler_item_name[self.player].value:
            return ManualItem(name, ItemClassification.filler, self.item_name_to_id[name], self.player)
        for item in self.multiworld.items[self.player].value:
            if item["name"] == name:
                classification = getattr(ItemClassification,
                                         "filler" if "classification" not in item else item["classification"])
                return ManualItem(name, classification, self.item_name_to_id[name], self.player)
        raise KeyError(f"Invalid item name {name} for Manual player {self.player}")


    def get_filler_item_name(self) -> str:
        return self.multiworld.filler_item_name[self.player].value

