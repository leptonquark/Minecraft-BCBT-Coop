from items import items
from items.gathering import get_sufficient_pickaxes, get_gathering_tier_by_pickaxe
from items.items import get_variants
from items.recipes import get_ingredients, get_recipe

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
        variant = info.get(f"InventorySlot_{i}_variant", None)
        if item == items.LOG_2:
            item = items.LOG
        inventory.append(InventorySlot(item, amount, variant))
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

    def has_ingredient(self, ingredient):
        return self.get_item_amount(ingredient.item) >= ingredient.amount

    def has_item(self, item, amount=1, same_variant=False):
        return self.get_item_amount(item, same_variant) >= amount

    def has_item_equipped(self, item):
        return self.inventory[self.current_selection].item == item

    def get_item_amount(self, item, same_variant=False):
        if self.inventory is None:
            return 0
        else:
            variants = get_variants(item)
            if same_variant:
                # There are two types of variants. One defined by me and uses the variant table,
                # and one defined by Minecraft and is contained in the slot information.
                # If {same_variant} is true we should return the max amount of the same variant.
                return max(self.get_max_slot_variant_amount(item_variant) for item_variant in variants)

            else:
                return sum(slot.amount for slot in self.inventory if slot.item in variants)

    def get_max_slot_variant_amount(self, item_variant):
        variant_amount = {}
        for slot in self.inventory:
            if slot.item == item_variant:
                variant_amount[slot.variant] = variant_amount.get(slot.variant, 0) + slot.amount
        return max(amount for amount in variant_amount.values()) if variant_amount else 0

    def find_item(self, item):
        variants = get_variants(item)
        for i, inventory_slot in enumerate(self.inventory):
            if inventory_slot.item in variants:
                return i
        return None

    def find_item_by_min_amount(self, item, amount, same_variant=False):
        variants = get_variants(item)
        for i, inventory_slot in enumerate(self.inventory):
            if inventory_slot.item in variants and (not same_variant or inventory_slot.amount >= amount):
                return i
        return None

    def has_ingredients(self, item):
        ingredients = get_ingredients(item)
        return all(self.has_item(ingredient.item, ingredient.amount) for ingredient in ingredients)

    def get_variants(self, item):
        variants = []
        recipe = get_recipe(item)

        for ingredient in recipe.ingredients:
            item_position = self.find_item_by_min_amount(ingredient.item, ingredient.amount, ingredient.same_variant)
            if item_position is not None:
                variant = self.inventory[item_position].variant
                if variant is not None:
                    variants.append(variant)
        return variants

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
        if not available_pickaxes:
            return None
        return max(available_pickaxes, key=lambda pickaxe: get_gathering_tier_by_pickaxe(pickaxe).value)


class InventorySlot:
    def __init__(self, item, amount, variant):
        self.item = item
        self.amount = amount
        self.variant = variant

    def __str__(self):
        return f"InventorySlot: {self.amount}x {self.item} : {self.variant}"

    def __repr__(self):
        return str(self)
