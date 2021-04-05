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
    return info.get(Inventory.CURRENT_SELECTION, 0)


class Inventory:
    CURRENT_SELECTION = "currentItemIndex"

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
        self.currentItem = info["currentItemIndex"]

    def __str__(self):
        return str(self.inventory)

    def has_item(self, item, amount=1):
        found = 0
        for inventorySlot in self.inventory:
            if inventorySlot.item == item:
                found += inventorySlot.amount
        return found >= amount

    def has_item_equipped(self, item):
        return self.inventory[self.current_selection].item == item

    def find_item(self, item):
        for i, inventorySlot in enumerate(self.inventory):
            if inventorySlot.item == item:
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
