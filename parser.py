import json
from models import GrabFood, Location, Menu, Items
from db import OUTPUT_FOLDER_PATH
import gzip

def parse_file(file_path):

    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            raw = json.load(f)
        if raw.get('merchant') is not None :
            data = raw.get('merchant',{})
        else:
            print("no merchant found") 
            return GrabFood(
                restaurant_name=None,
                product_category=None,
                img=None,
                location=Location(latitude=0, longitude=0),
                timeZone=None,
                currency=None,
                delivery_time=None,
                rating=None,
                availability=[],
                deliverable_distance=None,
                menu=[]
            )   


        location = Location(
            latitude=data.get('latlng',{}).get('latitude',None),
            longitude=data.get('latlng',{}).get('longitude',None)
        )

        availability_list = []
        if "openingHours" in data:
            days = {"sun", "mon", "tue", "wed", "thu", "fri", "sat"}
            availability_list = [
                {"day": day, "time_range": value}
                for day, value in data.get("openingHours").items()
                if day in days
            ]

        menu_list = []
        if "menu" in data and "categories" in data.get("menu",{}):
            for menu in data.get("menu",{}).get('categories',{}):
                if menu.get("name", "").lower() == "for you":
                       continue

                items = []
                for item in menu.get("items", []):
                    items.append(Items(
                        item_name=item.get("name", ""),
                        item_img=item.get('imgHref'),
                        price=item.get('priceV2',{}).get('amountDisplay'),
                        discount_price = item.get("discountedPriceV2", {}).get("amountDisplay"),
                        description=item.get("description", "")
                    ))

                menu_list.append(Menu(category=menu.get("name",""), items=items))

        grab_food = GrabFood(
            restaurant_name=data.get('name',""),
            product_category=data.get('cuisine',""),
            img=data.get('photoHref',""),
            location=location,
            timeZone=data.get('timeZone',""),
            currency=data.get('currency',{}).get('symbol',''),
            delivery_time=data.get('deliveryETARange'),
            rating=data.get('rating'),
            availability=availability_list,
            deliverable_distance=data.get('distanceInKm'),
            menu=menu_list
        )

        # with open(f"{OUTPUT_FOLDER_PATH}/{data['name']}_output.json", 'w', encoding='utf-8') as f:
        #     json.dump(grab_food.model_dump(), f, ensure_ascii=False, indent=4)
        
        return grab_food

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None  