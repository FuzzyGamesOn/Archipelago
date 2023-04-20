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

def evaluate_postfix(expr):
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
    return stack.pop()

def set_rules(base: World, world: MultiWorld, player: int):
    # Location access rules
    for location in base.location_table:
        locFromWorld = world.get_location(location["name"], player)
        if "requires" in location: # Specific item access required
            def fullLocationCheck(state, location=location):
                # parse user written statement into list of each item
                reqires_raw = re.split('(\[|&&|\|\||]| AND | OR)', location["requires"]) # regex probaly misses some cases i have to relearn regex everytime i use it
                reqires_stripped = [x.strip() for x in reqires_raw]
                requires_list = [x for x in reqires_stripped if x != '']
                
                for i, item in enumerate(requires_list):
                    if item == "[":                     # square brackets used so user can name items with ()
                        requires_list[i] = "("
                    elif item == "]":
                        requires_list[i] = ")"
                    elif item == "||" or item == "OR":
                        requires_list[i] = "|"
                    elif item == "&&" or item == "AND":
                        requires_list[i] = "&"
                    else:
                        item_parts = item.split(":")
                        item_name = item
                        item_count = 1

                        if len(item_parts) > 1:
                            item_name = item_parts[0]
                            item_count = int(item_parts[1])

                        if state.has(item_name, player, item_count):    # if player has the item replace the text with 1 otherwiwse 0
                            requires_list[i] = "1"
                        else:
                            requires_list[i] = "0"

                requires_string = infix_to_postfix("".join(requires_list))
                return(evaluate_postfix(requires_string))

            set_rule(locFromWorld, fullLocationCheck)
        else: # Only region access required
            def allRegionsAccessible(state, location=location):
                return True
            set_rule(locFromWorld, allRegionsAccessible) # everything is in the same region in manual

    # Victory requirement
    world.completion_condition[player] = lambda state: state.has("__Victory__", player)