from ..generic.Rules import set_rule
from ..AutoWorld import World
from BaseClasses import MultiWorld
import re


def infix_to_postfix(expr):
    prec = {"&": 2, "|": 2, "!": 3}

    stack = []
    postfix = ""

    for c in expr:
        if c.isnumeric():
            postfix += c
        elif c in prec:
            while stack and stack[-1] != "(" and prec[c] <= prec[stack[-1]]:
                postfix += stack.pop()
            stack.append(c)
        elif c == "(":
            stack.append(c)
        elif c == ")":
            while stack and stack[-1] != "(":
                postfix += stack.pop()
            stack.pop()
    while stack:
        postfix += stack.pop()

    return postfix


def evaluate_postfix(expr, location):
    stack = []
    for c in expr:
        if c == "0":
            stack.append(False)
        elif c == "1":
            stack.append(True)
        elif c == "&":
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(op1 and op2)
        elif c == "|":
            op2 = stack.pop()
            op1 = stack.pop()
            stack.append(op1 or op2)
        elif c == "!":
            op = stack.pop()
            stack.append(not op)

    if len(stack) != 1:
        raise KeyError("Invalid logic format for location {}.".format(location["name"]))
    return stack.pop()


def set_rules(base: World, world: MultiWorld, player: int):
    # Location access rules
    for location in base.location_table:
        locFromWorld = world.get_location(location["name"], player)
        if "requires" in location:  # Specific item access required
            # item access is in string logic form
            if isinstance(location["requires"], str):

                def fullLocationCheckString(state, location=location):
                    # parse user written statement into list of each item
                    reqires_raw = re.split('(\AND|\)|\(|OR|\|)', location["requires"])
                    remove_spaces = [x.strip() for x in reqires_raw]
                    remove_empty = [x for x in remove_spaces if x != '']
                    requires_list = [x for x in remove_empty if x != '|']

                    for i, item in enumerate(requires_list):
                        if item.lower() == "or":
                            requires_list[i] = "|"
                        elif item.lower() == "and":
                            requires_list[i] = "&"
                        elif item == ")" or item == "(":
                            continue
                        else:
                            item_parts = item.split(":")
                            item_name = item
                            item_count = 1

                            if len(item_parts) > 1:
                                item_name = item_parts[0]
                                item_count = int(item_parts[1])

                            if state.has(item_name, player, item_count):
                                requires_list[i] = "1"
                            else:
                                requires_list[i] = "0"

                    requires_string = infix_to_postfix("".join(requires_list))
                    return (evaluate_postfix(requires_string, location))

                set_rule(locFromWorld, fullLocationCheckString)

            else:  # item access is in dict form

                def fullLocationCheck(state, location=location):
                    canAccess = True

                    for item in location["requires"]:
                        # if the require entry is an object with "or" or a list of items, treat it as a standalone require of its own
                        if (isinstance(item, dict) and "or" in item and isinstance(item["or"], list)) or (isinstance(item, list)):
                            canAccessOr = True
                            or_items = item
                            
                            if isinstance(item, dict):
                                or_items = item["or"]

                            for or_item in or_items:
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

        else:  # Only region access required
            def allRegionsAccessible(state, location=location):
                return True
            # everything is in the same region in manual
            set_rule(locFromWorld, allRegionsAccessible)

    # Victory requirement
    world.completion_condition[player] = lambda state: state.has("__Victory__", player)
