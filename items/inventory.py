from items import items

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

    def has_item(self, item, amount=1):
        found = sum(inventory_slot.amount for inventory_slot in self.inventory if inventory_slot.item == item)
        return found >= amount

    def has_item_equipped(self, item):
        return self.inventory[self.current_selection].item == item

    def find_item(self, item):
        for i, inventory_slot in enumerate(self.inventory):
            if inventory_slot.item == item:
                return i
        return -1

    def has_ingredients(self, item):
        ingredients = get_ingredients(item)

        for ingredient in ingredients:
            if not self.has_item(ingredient.item, ingredient.amount):
                return False
        return True

    def get_fuel(self):
        for fuel in fuels:
            if self.has_item(fuel):
                return fuel
        return None


class InventorySlot:
    def __init__(self, item, amount):
        self.item = item
        self.amount = amount

    def __str__(self):
        return f"InventorySlot: {self.amount}x {self.item}"

    def __repr__(self):
        return str(self)
