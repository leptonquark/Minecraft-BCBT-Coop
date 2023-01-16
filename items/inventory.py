from items import items
from items.gathering import get_sufficient_pickaxes, get_gathering_tier_by_pickaxe
from items.items import get_variants
from items.recipes import get_ingredients, get_recipe

NO_SELECTION = -1
HOTBAR_SIZE = 9

# Ordered by value
fuels = [items.COAL, items.PLANKS, items.LOG]


def get_size(info):
    return next((i["size"] for i in info["inventoriesAvailable"] if i["name"] == "inventory"), 0)


def fill_inventory(info, size):
    return [get_inventory_slot_from_info(info, slot) for slot in range(size)]


def get_inventory_slot_from_info(info, slot):
    amount = info[f"InventorySlot_{slot}_size"]
    item = info[f"InventorySlot_{slot}_item"]
    variant = info.get(f"InventorySlot_{slot}_variant", None)
    if item == items.LOG_2:
        item = items.LOG
    return InventorySlot(item, amount, variant)


def get_selection_from_info(info):
    return info.get(Inventory.KEY_CURRENT_SELECTION, NO_SELECTION)


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

    def has_item(self, item, amount=1, same_variant=False):
        return self.get_item_amount(item, same_variant) >= amount

    def has_item_equipped(self, item):
        return self.inventory[self.current_selection].item in get_variants(item)

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
        return next((i for i, slot in enumerate(self.inventory) if slot.item in get_variants(item)), None)

    def find_item_by_min_amount(self, item, amount, same_variant=False):
        variants = get_variants(item)
        return next((i for i, s in enumerate(self.inventory) if s.has_variants(variants, amount, same_variant)), None)

    def has_ingredients(self, item):
        ingredients = get_ingredients(item)
        return all(self.has_item(ingredient.item, ingredient.amount) for ingredient in ingredients)

    def get_variants(self, item):
        recipe = get_recipe(item)
        variants = [self.get_ingredient_variant(ingredient) for ingredient in recipe.ingredients]
        return [variant for variant in variants if variant is not None]

    def get_ingredient_variant(self, ingredient):
        item_position = self.find_item_by_min_amount(ingredient.item, ingredient.amount, ingredient.same_variant)
        return self.inventory[item_position].variant if item_position is not None else None

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
        else:
            return max(available_pickaxes, key=lambda pickaxe: get_gathering_tier_by_pickaxe(pickaxe).value)


class InventorySlot:
    HELMET_SLOT = 39
    CHEST_SLOT = 40
    PANTS_SLOT = 41
    BOOTS_SLOT = 42

    def __init__(self, item, amount, variant):
        self.item = item
        self.amount = amount
        self.variant = variant

    def __str__(self):
        return f"InventorySlot: {self.amount}x {self.item} : {self.variant}"

    def __repr__(self):
        return str(self)

    def has_variants(self, variants, amount, same_variant):
        return self.item in variants and self.amount >= amount and (not same_variant or self.variant is not None)
