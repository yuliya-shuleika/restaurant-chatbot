import json

from typing import Any, Text, Dict, List
import dateparser


from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionGetMenuItems(Action):

    def name(self) -> Text:
        return "action_get_menu_items"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu_items = json.load(open("menu.json", "r"))["items"]
        menu_items_text = "\n".join([f"{item['name']} - ${item['price']}" for item in menu_items])
        dispatcher.utter_message(f"Here's available mebu items: {menu_items_text}")

        return []

class ActionCheckOpeningHours(Action):
    def name(self) -> Text:
        return "action_check_opening_hours"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        opening_hours = json.load(open("opening_hours.json", "r"))["items"]
        date = tracker.get_slot("date")
        print(date)

        if not date:
            date = "now"

        parsed_date = dateparser.parse(date)
        weekday = parsed_date.strftime("%A")

        print(parsed_date)
        print(weekday)
        opening_hours_requested_day = opening_hours[weekday]
        print(opening_hours_requested_day)
        opening_hour = opening_hours_requested_day["open"]
        closing_hour = opening_hours_requested_day["close"]

        if opening_hour == 0 and closing_hour == 0:
            dispatcher.utter_message(f"Sorry, we are closed on {weekday}.")
        else:
            dispatcher.utter_message(f"We are open on {weekday} from {opening_hour} to {closing_hour}.")

        return []

class ActionPlaceOrder(Action):

    def name(self) -> Text:
        return "action_place_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        menu_items = json.load(open("menu.json", "r"))["items"]
        order_items = tracker.get_slot("order_items")
        additional_requests = tracker.get_slot("additional_requests")
        print(f"order_items: {order_items}")
        print(f"additional_requests: {additional_requests}")
        if not order_items:
            dispatcher.utter_message(text="I couldn't process your order. Please specify the items and quantities.")
            return []

        total_price = 0
        max_time = 0
        unavailable_items = []
        order_summary = []

        for item_name in order_items:
            item = next((i for i in menu_items if i["name"].lower() == item_name.lower()), None)
            if not item:
                unavailable_items.append(item_name)
                continue

            item_price = item["price"]
            item_time = item["preparation_time"]

            total_price += item_price
            max_time = max(max_time, item_time)
            order_summary.append(f" {item_name} - ${item_price}")

        response_text = "Your order summary:\n" + "\n".join(order_summary)
        response_text += f"\nTotal Price: ${total_price}\nEstimated Preparation Time: {max_time} hours."

        if additional_requests:
            response_text += f"\nAdditional requests: {additional_requests}"

        if unavailable_items:
            response_text += f"\nNote: We don't have {', '.join(unavailable_items)} on the menu."

        dispatcher.utter_message(text=response_text)
        return []

class ActionConfirmDelivery(Action):
    def name(self) -> Text:
        return "action_confirm_delivery"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[
        Dict[Text, Any]]:
        address = tracker.get_slot("delivery_address")

        if not address:
            dispatcher.utter_message(text="I still need your delivery address. Where should we deliver your order?")
            return []

        dispatcher.utter_message(text=f"Your order will be delivered to: {address}. Thank you!")

        return []
