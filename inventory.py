HOTBAR_SIZE = 9

class Inventory():

    def __init__(self, info):
        if "inventoriesAvailable" not in info:
            print("Can't create inventory. No inventory available.")
            return
        
        size = self.getSize(info)
        if size == 0:
            print("Inventory size is 0")
            return 
        
        self.inventory = self.fillInventory(info, size)
        self.currentItem = info["currentItemIndex"]

        
    def getSize(self, info):
        size = 0
        for inventory in info["inventoriesAvailable"]:
            if inventory["name"] == "inventory":
                size = inventory["size"]
        return size

    def fillInventory(self, info, size):
        inventory = []
        for i in range(size):
            amount = info[f"InventorySlot_{i}_size"]
            item = info[f"InventorySlot_{i}_item"]
            inventory.append(InventorySlot(item, amount))
        return inventory

    def __str__(self):
        return str(self.inventory)

    def hasItem(self, item, amount = 1):
        found = 0
        for inventorySlot in self.inventory:
            if inventorySlot.item == item:
                found += inventorySlot.amount
        return found >= amount

    def findItem(self, item):
        for i, inventorySlot in enumerate(self.inventory):
            if inventorySlot.item == item:
                return i
        return -1


class InventorySlot():
    def __init__(self, item, amount):
        self.item = item
        self.amount = amount

    def __str__(self):
        return f"InventorySlot: {self.amount}x {self.item}"

    def __repr__(self):
        return str(self)

