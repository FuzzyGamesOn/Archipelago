from Options import OptionList, FreeText


class Locations(OptionList):
    """List of locations. See documentation."""
    display_name = "Locations"


class Items(OptionList):
    """List of items. See documentation"""
    display_name = "Items"


class FillerItemName(FreeText):
    """Item name for filler item to be used if locations specified are greater than items specified."""
    default = "The regret of not specifying a custom filler item"
    display_name = "Filler Item Name"


manual_options = {
    "locations": Locations,
    "items": Items,
    "filler_item_name": FillerItemName,
}