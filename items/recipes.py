from enum import Enum
from items import items
from items.ingredient import Ingredient


class RecipeType(Enum):
    Crafting = 0
    Melting = 1


class Recipe:

    def __init__(self, ingredients, output_amount=1, station=None):
        self.ingredients = ingredients
        self.output_amount = output_amount
        self.station = station
        self.recipe_type = RecipeType.Melting if (station == items.FURNACE) else RecipeType.Crafting


recipes = {
    items.PLANKS: Recipe([Ingredient(items.LOG)], 4),
    items.CRAFTING_TABLE: Recipe([Ingredient(items.PLANKS)], 4),
    items.STICKS: Recipe([Ingredient(items.PLANKS, 2)], 4),
    items.FURNACE: Recipe([Ingredient(items.COBBLESTONE, 8)], station=items.CRAFTING_TABLE),
    items.IRON_INGOT: Recipe([Ingredient(items.COAL), Ingredient(items.IRON_ORE)], station=items.FURNACE),
    items.WOODEN_PICKAXE: Recipe(
        [Ingredient(items.STICKS, 2), Ingredient(items.PLANKS, 3)],
        station=items.CRAFTING_TABLE
    ),
    items.STONE_PICKAXE: Recipe(
        [Ingredient(items.STICKS, 2), Ingredient(items.COBBLESTONE, 3)],
        station=items.CRAFTING_TABLE
    ),
    items.IRON_PICKAXE: Recipe(
        [Ingredient(items.STICKS, 2), Ingredient(items.IRON_INGOT, 3)],
        station=items.CRAFTING_TABLE
    ),
    items.DIAMOND_PICKAXE: Recipe(
        [Ingredient(items.STICKS, 2), Ingredient(items.DIAMOND, 3)],
        station=items.CRAFTING_TABLE
    ),
    items.WOODEN_SWORD: Recipe(
        [Ingredient(items.STICKS, 2), Ingredient(items.PLANKS, 2)],
        station=items.CRAFTING_TABLE
    ),
    items.WOODEN_FENCE: Recipe(
        [Ingredient(items.STICKS, 2), Ingredient(items.PLANKS, 4)],
        output_amount=3,
        station=items.CRAFTING_TABLE
    )
}


def has_recipe(item):
    return item in recipes


def get_ingredients(item):
    if has_recipe(item):
        return recipes[item].ingredients
    return None


def get_recipe(item):
    return recipes.get(item, None)
