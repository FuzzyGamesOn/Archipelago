from BaseClasses import Region
from .Locations import ManualLocation


def create_regions(self):
    region = Region("Menu", self.player, self.multiworld)
    region.locations.append(ManualLocation(self.player, "Victory", None, region))
    for location in self.multiworld.locations[self.player].value:
        if location["name"] != "Victory":
            region.locations.append(ManualLocation(self.player, location["name"],
                                                   self.location_name_to_id[location["name"]], region))
    self.multiworld.regions.append(region)

