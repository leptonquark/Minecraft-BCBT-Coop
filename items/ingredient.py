class Ingredient:
    def __init__(self, item, amount=1):
        self.item = item
        self.amount = amount

    def __str__(self):
        return f"Ingredient: {self.amount}x {self.item}"

    def __repr__(self):
        return str(self)
