from ..generic.Rules import set_rule


def set_rules(self):
    multiworld = self.multiworld
    player = self.player
    # Location access rules
    for location in multiworld.locations[player].value:
        locFromWorld = multiworld.get_location(location["name"], player)
        if "requires" in location:  # Specific item access required
            def fullLocationCheck(state, location=location):
                canAccess = True

                for item in location["requires"]:
                    if isinstance(item, dict) and "or" in item and isinstance(item["or"], list):
                        canAccessOr = True

                        for or_item in item["or"]:
                            or_item_parts = or_item.split(":")
                            or_item_name = or_item
                            or_item_count = 1

                            if len(or_item_parts) > 1:
                                or_item_name = or_item_parts[0]
                                or_item_count = int(or_item_parts[1])

                            if not state.has(or_item_name, player, or_item_count):
                                canAccessOr = False

                        if canAccessOr:
                            canAccess = True
                            break
                    else:
                        item_parts = item.split(":")
                        item_name = item
                        item_count = 1

                        if len(item_parts) > 1:
                            item_name = item_parts[0]
                            item_count = int(item_parts[1])

                        if not state.has(item_name, player, item_count):
                            canAccess = False

                return canAccess
            set_rule(locFromWorld, fullLocationCheck)

    multiworld.completion_condition[player] = lambda state: state.has("Victory", player)
