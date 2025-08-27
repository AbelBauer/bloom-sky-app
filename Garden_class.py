import requests

class Garden:
    def __init__(self, indoor_plants=None, outdoor_plants=None):
        self.indoor_plants = indoor_plants if indoor_plants else []
        self.outdoor_plants = outdoor_plants if outdoor_plants else []
        self.indoor_plants_data = {}
        self.outdoor_plants_data = {}

    #def __repr__(self):
     #   return (f"{self.__class__.__name__}")
        
    def __str__(self):
        all_plants = self.indoor_plants + self.outdoor_plants
        if not all_plants:
            return "Your garden is currently empty"
        return f"Your garden has a total of {len(all_plants)} plants: " + ", ".join[(plant.title() for plant in all_plants)]
    
    @staticmethod
    def validate_plant(name):
        if not isinstance(name, str):
            raise TypeError("Plant name must be a string of text.")
        if name not in plant_database:
            raise ValueError(f"{name} not recognize. Try checking spelling or searching for an alternative name.")
        return True
    
    def add_plants(self, location_type):
        LOC_TYPE = ["indoor", "outdoor"] # for input validation...WIP
        new_plants = []
        user_plants = input(f"Type in your {location_type} plants: ➤ ").lower().strip()
        for plant in user_plants.split(","):
            cleaned = plant.lower().strip()
            if cleaned and self.validate_plant(cleaned):
                new_plants.append(cleaned)

        if location_type == LOC_TYPE[0]:
            self.indoor_plants.extend(new_plants)
            print("\nYour indoor plants:")
            for i, plant in enumerate(self.indoor_plants, 1):
                print(f"{i}. {plant.title()}")

        elif location_type == LOC_TYPE[1]:
            self.outdoor_plants.extend(new_plants)
            print("\nYour outdoor plants:")
            for i, plant in enumerate(self.outdoor_plants, 1):
                print(f"{i}. {plant.title()}")
        else:
            print("Plant location not yet supported")
            raise ValueError

    def list_total_plants(self):
        print("\n🌿 In your garden live:")
        for i, plant in enumerate(self.indoor_plants + self.outdoor_plants, 1):
            print(f"{i}. {plant.title()}")

    def get_plant_info(self, name: str):
        fo




    def get_care_summary(self, plant_name):
        pass