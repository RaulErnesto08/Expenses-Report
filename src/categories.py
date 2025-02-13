from enum import Enum

class Category(Enum):
    MEALS = "Meals"
    LODGING = "Lodging"
    AIRFARE = "Airfare"
    RENTAL_CAR = "Rental Car"
    TRANSPORTATION = "Transportation"
    OTHER = "Other"

    @classmethod
    def from_string(cls, category_str):
        """
        Converts a string to a valid category enum, or defaults to OTHER.
        """
        for category in cls:
            if category.value.lower() == category_str.lower():
                return category
        return cls.OTHER
