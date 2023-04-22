from BaseClasses import Item, ItemClassification


def create_items(self):
    # Generate item pool
    pool = []

    for item in self.multiworld.items[self.player].value:

        item_name = item["name"].split(":")[0]
        if ":" in item["name"]:
            item_count = int(item["name"].split(":")[1])
        else:
            item_count = 1

        classification = getattr(ItemClassification, "filler" if "classification" not in item else item["classification"])

        for i in range(item_count):
            manual_item = ManualItem(item_name, classification,
                                     self.item_name_to_id[item_name], player=self.player)

            pool.append(manual_item)

    extras = (len(self.multiworld.locations[self.player].value) - len(pool)) - 1

    for i in range(0, extras):
        pool.append(self.create_filler())

    self.multiworld.itempool += pool


class ManualItem(Item):
    game = "Manual"
