from items import items
from items.gathering import get_sufficient_pickaxes, get_gathering_tier_by_pickaxe

from items.recipes import get_ingredients

NO_SELECTION = -1
HOTBAR_SIZE = 9

# Ordered by value
fuels = [items.COAL, items.PLANKS, items.LOG]


def get_size(info):
    size = 0
    for inventory in info["inventoriesAvailable"]:
        if inventory["name"] == "inventory":
            size = inventory["size"]
    return size


def fill_inventory(info, size):
    inventory = []
    for i in range(size):
        amount = info[f"InventorySlot_{i}_size"]
        item = info[f"InventorySlot_{i}_item"]
        inventory.append(InventorySlot(item, amount))
    return inventory


def get_selection_from_info(info):
    return info.get(Inventory.KEY_CURRENT_SELECTION, 0)


class Inventory:
    KEY_CURRENT_SELECTION = "currentItemIndex"

    def __init__(self, info):
        self.inventory = None
        if "inventoriesAvailable" not in info:
            print("Can't create inventory. No inventory available.")
            return

        size = get_size(info)
        if size == 0:
            print("Inventory size is 0")
            return

        self.inventory = fill_inventory(info, size)
        self.current_selection = get_selection_from_info(info)

    def __str__(self):
        return str(self.inventory)

    def __iter__(self):
        for inventory_slot in self.inventory:
            yield inventory_slot

    def has_item(self, item, amount=1):
        return self.get_item_amount(item) >= amount

    def has_item_equipped(self, item):
        return self.inventory[self.current_selection].item == item

    def get_item_amount(self, item):
        if self.inventory is None:
            return 0
        else:
            return sum(inventory_slot.amount for inventory_slot in self.inventory if inventory_slot.item == item)

    def find_item(self, item):
        for i, inventory_slot in enumerate(self.inventory):
            if inventory_slot.item == item:
                return i
        return -1

    def has_ingredients(self, item):
        ingredients = get_ingredients(item)
        return all(self.has_item(ingredient.item, ingredient.amount) for ingredient in ingredients)

    def get_fuel(self):
        return next((fuel for fuel in fuels if self.has_item(fuel)), None)

    def has_pickaxe_by_minimum_tier(self, min_tier):
        sufficient_pickaxes = get_sufficient_pickaxes(min_tier)
        return any(self.has_item(pickaxe) for pickaxe in sufficient_pickaxes)

    def has_best_pickaxe_by_minimum_tier_equipped(self, min_tier):
        best_pickaxe = self.get_best_pickaxe(min_tier)
        return self.inventory[self.current_selection].item == best_pickaxe

    def get_best_pickaxe(self, min_tier):
        sufficient_pickaxes = get_sufficient_pickaxes(min_tier)
        available_pickaxes = [pickaxe for pickaxe in sufficient_pickaxes if self.has_item(pickaxe)]
        if len(available_pickaxes) == 0:
            return None
        return max(available_pickaxes, key=lambda pickaxe: get_gathering_tier_by_pickaxe(pickaxe).value)


class InventorySlot:
    def __init__(self, item, amount):
        self.item = item
        self.amount = amount

    def __str__(self):
        return f"InventorySlot: {self.amount}x {self.item}"

    def __repr__(self):
        return str(self)
