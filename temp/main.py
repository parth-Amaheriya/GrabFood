
from pydantic import BaseModel,field_validator
import re
import json

class Location(BaseModel):
    latitude:float
    longitude:float

    @field_validator("latitude")
    def validate_latitude(cls, v):
        if not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v):
        if not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v
        
class Availability(BaseModel):
    day: str
    time_range:str   

class Items(BaseModel):
    item_name:str
    item_img:str | None
    price:float
    discount_price:float | None
    description:str

    @field_validator("price")
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

class Menu(BaseModel):
    category:str
    items:list[Items]

class GrabFood(BaseModel):
    restaurant_name: str
    product_category:str
    img:str
    location:Location
    timeZone:str
    currency:str
    delivery_time:float
    rating:float | None
    availability:list[Availability]
    deliverable_distance:float
    menu:list[Menu]

    @field_validator("currency")
    def validate_currency(cls, v):
        if not re.match(r"^[A-Z]{2}$", v):
            raise ValueError("Invalid currency code")
        return v
    
    @field_validator("delivery_time", mode="before")
    def validate_delivery_time(cls, v):
        match = re.search(r"\d+", str(v)) 
        if not match:
            raise ValueError("Invalid delivery time format")
        return float(match.group())

with open('grabfood.json','r',encoding='utf-8') as f:
    data=json.load(f)


try:
    data=data['merchant']
    restaurant_name=data['name']
    product_category=data['cuisine']
    img=data['photoHref']

    longitude=data['latlng']['longitude']
    latitude=data['latlng']['latitude']
    location=Location(latitude=latitude,longitude=longitude)

    timeZone=data['timeZone']
    currency=data['currency']['symbol']
    delivery_time=data['deliveryETARange']
    rating=data['rating']

    if "openingHours" in data:
        days = {"sun", "mon", "tue", "wed", "thu", "fri", "sat"}
        availability_list = [
            {"day": day, "time_range": value}
            for day, value in data["openingHours"].items()
            if day in days
        ]
    else:
        print("Opening hours data is missing or in an unexpected format.")
        availability_list = []    
           
    deliverable_distance=data['distanceInKm']

    menu_list = []
    if "menu" in data and "categories" in data["menu"]:
        print("Parsing menu data...")
        for menu in data["menu"]['categories']:
            if menu["name"].lower() == "for you":
                continue

            category = menu["name"]
            items = []
            for item in menu["items"]:
                item_name = item.get("name", "")
                item_img = item.get('imgHref', None)
                price = item['priceV2']['amountDisplay']
                discount_price=item["discountedPriceV2"]['amountDisplay']
                description = item.get("description", "")
                items.append(Items(item_name=item_name, item_img=item_img, price=price, discount_price=discount_price, description=description))
            menu_list.append(Menu(category=category, items=items))
    else:
        print("Menu data is missing or in an unexpected format.")        

    grab_food = GrabFood(
        restaurant_name=restaurant_name,
        product_category=product_category,
        img=img,
        location=location,
        timeZone=timeZone,
        currency=currency,
        delivery_time=delivery_time,
        rating=rating,
        availability=availability_list,
        deliverable_distance=deliverable_distance,
        menu=menu_list
    ) 
except Exception as e:
    print(f"Error parsing data: {e}")

with open('grabfood_output.json', 'w', encoding='utf-8') as f:
    json.dump(grab_food.model_dump(), f, ensure_ascii=False, indent=4)




