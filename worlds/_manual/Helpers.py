from BaseClasses import MultiWorld

from typing import Union, List, Dict

def is_option_enabled(world: MultiWorld, player: int, name: str) -> bool:
    return get_option_value(world, player, name) > 0

def get_option_value(world: MultiWorld, player: int, name: str) -> Union[int, dict]:
    option = getattr(world, name, None)
    if option == None:
        return 0

    return option[player].value

def category_join(table: List[Dict[str, any]]):
    for item in table:
        if len({'category', 'dev_category'}.intersection(item.keys())):
            item['all_category'] = item.get('category', []) + item.get('dev_category', [])
