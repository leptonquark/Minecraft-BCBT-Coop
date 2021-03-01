class RecipeBook():
    
    def __init__(self):
        self.recipes = {
            "planks" : [Ingredient("log")],
            "crafting_table" : [Ingredient("planks", 4)],
            "stick" : [Ingredient("planks", 2)],
            "wooden_pickaxe" : [Ingredient("crafting_table"), Ingredient("stick", 2), Ingredient("planks", 3)],   
            "stone_pickaxe" : [Ingredient("crafting_table"), Ingredient("stick", 2), Ingredient("cobblestone", 3)]
        }

    def getIngredients(self, item):
        for recipe in self.recipes:
            if recipe == item:
                return self.recipes[item]
        return None


class Ingredient():
    def __init__(self, item, amount = 1):
        self.item = item
        self.amount = amount

    def __str__(self):
        return f"Ingredient: {self.amount}x {self.item}"

    def __repr__(self):
        return str(self)
