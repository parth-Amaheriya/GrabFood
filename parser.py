import json
from models import GrabFood, Location, Menu, Items
from db import OUTPUT_FOLDER_PATH

def parse_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    try:
        data = raw['merchant']

        location = Location(
            latitude=data['latlng']['latitude'],
            longitude=data['latlng']['longitude']
        )

        availability_list = []
        if "openingHours" in data:
            days = {"sun", "mon", "tue", "wed", "thu", "fri", "sat"}
            availability_list = [
                {"day": day, "time_range": value}
                for day, value in data["openingHours"].items()
                if day in days
            ]

        menu_list = []
        if "menu" in data and "categories" in data["menu"]:
            for menu in data["menu"]['categories']:
                if menu["name"].lower() == "for you":
                    continue

                items = []
                for item in menu["items"]:
                    items.append(Items(
                        item_name=item.get("name", ""),
                        item_img=item.get('imgHref'),
                        price=item['priceV2']['amountDisplay'],
                        discount_price=item.get("discountedPriceV2").get("amountDisplay"),
                        description=item.get("description", "")
                    ))

                menu_list.append(Menu(category=menu["name"], items=items))

        grab_food = GrabFood(
            restaurant_name=data['name'],
            product_category=data['cuisine'],
            img=data['photoHref'],
            location=location,
            timeZone=data['timeZone'],
            currency=data['currency']['symbol'],
            delivery_time=data['deliveryETARange'],
            rating=data.get('rating'),  
            availability=availability_list,
            deliverable_distance=data['distanceInKm'],
            menu=menu_list
        )

        with open(f"{OUTPUT_FOLDER_PATH}/{data['name']}_output.json", 'w', encoding='utf-8') as f:
            json.dump(grab_food.model_dump(), f, ensure_ascii=False, indent=4)
        
        return grab_food

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None  