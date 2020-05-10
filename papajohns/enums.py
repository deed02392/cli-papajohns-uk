from enum import Enum, IntEnum

class ProductTypeId(IntEnum):
    PIZZA = 1
    SIDE = 2
    DESSERT = 3
    DRINK = 4


    def GetDisplayName(self):
        return str.capitalize(self.name)

    @classmethod
    def GetProductType(cls, id):
        if (id == cls.PIZZA.value):
            return cls.PIZZA
        elif (id == cls.SIDE.value):
            return cls.SIDE
        elif (id == cls.DESSERT.value):
            return cls.DESSERT
        elif (id == cls.DRINK.value):
            return cls.DRINK
        else:
            raise ValueError("Unknown ProductTypeId")

