from enum import Enum
from items.ingredient import Ingredient
from items.items import Item


class RecipeType(Enum):
    Crafting = 0
    Melting = 1


class Recipe:

    def __init__(self, ingredients, output_amount=1, station=None):
        self.ingredients = ingredients
        self.output_amount = output_amount
        self.station = station
        self.recipe_type = RecipeType.Melting if (station == Item.FURNACE) else RecipeType.Crafting


recipes = {
    Item.PLANKS: Recipe([Ingredient(Item.LOG)], 4),
    Item.CRAFTING_TABLE: Recipe([Ingredient(Item.PLANKS)], 4),
    Item.STICKS: Recipe([Ingredient(Item.PLANKS, 2)], 4),
    Item.FURNACE: Recipe([Ingredient(Item.COBBLESTONE, 8)], station=Item.CRAFTING_TABLE),
    Item.IRON_INGOT: Recipe([Ingredient(Item.COAL), Ingredient(Item.IRON_ORE)], station=Item.FURNACE),
    Item.WOODEN_PICKAXE: Recipe(
        [Ingredient(Item.STICKS, 2), Ingredient(Item.PLANKS, 3)],
        station=Item.CRAFTING_TABLE
    ),
    Item.STONE_PICKAXE: Recipe(
        [Ingredient(Item.STICKS, 2), Ingredient(Item.COBBLESTONE, 3)],
        station=Item.CRAFTING_TABLE
    ),
    Item.IRON_PICKAXE: Recipe(
        [Ingredient(Item.STICKS, 2), Ingredient(Item.IRON_INGOT, 3)],
        station=Item.CRAFTING_TABLE
    ),
    Item.DIAMOND_PICKAXE: Recipe(
        [Ingredient(Item.STICKS, 2), Ingredient(Item.DIAMOND, 3)],
        station=Item.CRAFTING_TABLE
    ),
    Item.WOODEN_SWORD: Recipe(
        [Ingredient(Item.STICKS, 2), Ingredient(Item.PLANKS, 2)],
        station=Item.CRAFTING_TABLE
    ),
    Item.WOODEN_FENCE: Recipe(
        [Ingredient(Item.STICKS, 2), Ingredient(Item.PLANKS, 4)],
        output_amount=3,
        station=Item.CRAFTING_TABLE
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
