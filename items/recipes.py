from items import items


class Ingredient:
    def __init__(self, item, amount=1):
        self.item = item
        self.amount = amount

    def __str__(self):
        return f"Ingredient: {self.amount}x {self.item}"

    def __repr__(self):
        return str(self)


recipes = {
    items.PLANKS: [Ingredient(items.LOG)],
    items.CRAFTING_TABLE: [Ingredient(items.PLANKS, 4)],
    items.STICKS: [Ingredient(items.PLANKS, 2)],
    items.WOODEN_PICKAXE: [
        Ingredient(items.CRAFTING_TABLE), Ingredient(items.STICKS, 2), Ingredient(items.PLANKS, 3)
    ],
    items.STONE_PICKAXE: [
        Ingredient(items.CRAFTING_TABLE), Ingredient(items.STICKS, 2), Ingredient(items.COBBLESTONE, 3)
    ],
    items.IRON_PICKAXE: [
        Ingredient(items.CRAFTING_TABLE), Ingredient(items.STICKS, 2), Ingredient(items.IRON_INGOT, 3)
    ],
    items.FURNACE: [Ingredient(items.CRAFTING_TABLE), Ingredient(items.COBBLESTONE, 8)],
    items.IRON_INGOT: [Ingredient(items.FURNACE), Ingredient(items.IRON_ORE)],
    items.DIAMOND_PICKAXE: [
        Ingredient(items.CRAFTING_TABLE), Ingredient(items.STICKS, 2), Ingredient(items.DIAMOND, 3)
    ]
}


def has_recipe(item):
    return item in recipes


def get_ingredients(item):
    if has_recipe(item):
        return recipes[item]
    return None
