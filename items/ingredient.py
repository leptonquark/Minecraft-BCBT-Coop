class Ingredient:
    def __init__(self, item, amount=1, same_variant=False):
        self.item = item
        self.amount = amount
        self.same_variant = same_variant

    def __str__(self):
        return f"Ingredient: {self.amount}x {self.item}"

    def __repr__(self):
        return str(self)
