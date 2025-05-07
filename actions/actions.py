import os
import time
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List

API_BASE = os.getenv("API_URL", "https://thesis-backend-production-6496.up.railway.app")

class ActionTrackOrder(Action):
    def name(self) -> Text:
        return "action_track_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_id = tracker.sender_id or ""          

        if user_id in ("", "guest"):             
            dispatcher.utter_message(text="Please log in to track your orders.")
            return []

        try:
            response = requests.get(f"{API_BASE}/api/orders/by-user/{user_id}")
            if response.status_code == 401:
                dispatcher.utter_message(text="Please log in to track your orders.")
                return []

            if response.status_code != 200:
                dispatcher.utter_message(text="Sorry, I couldn’t fetch your orders.")
                return []

            orders = response.json().get("orders", [])
            if not orders:
                dispatcher.utter_message(text="You don't have any active orders.")
                return []

            buttons = []
            for order in orders:
                order_id = order["_id"]
                buttons.append({
                    "title": f"{order['status']} - {order_id[:6]}...",
                    "payload": f"/select_order{{\"order_id\": \"{order_id}\"}}"
                })

            dispatcher.utter_message(text="Here are your recent orders. Click one to see details:", buttons=buttons)
            return []

        except Exception as e:
            print("Error in action_track_order:", str(e))
            dispatcher.utter_message(text="An error occurred while fetching orders.")
            return []
        

class ActionShowOrderDetails(Action):
    def name(self) -> Text:
        return "action_show_order_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        order_id = tracker.get_slot("order_id")

        if not order_id:
            dispatcher.utter_message(text="Please provide a valid order ID.")
            return []

        try:
            response = requests.get(f"{API_BASE}/api/orders/by-id/{order_id}")
            if response.status_code != 200:
                dispatcher.utter_message(text="Couldn’t retrieve order details.")
                return []

            order = response.json().get("order", {})

            message = (
                         f"Order Summary\n\n"
                         f"Order ID: {order['_id']}\n"
                         f"Status: {order.get('status', 'Processing')}\n\n"
                         f"Items:\n"
                    )
            for item in order.get("items", []):
                product = item.get("productId", {})
                message += f"• {product.get('name')} (${product.get('price')})\n"

            dispatcher.utter_message(
                text=message,
                buttons=[
                    {"title": "🔁 Check Another Order", "payload": "/track_order"},
                    {"title": "🏠 Return to Main Menu", "payload": "/go_to_main_menu"},
                ]
            )
            return []

        except Exception as e:
            print("Error in action_show_order_details:", str(e))
            dispatcher.utter_message(text="An error occurred while retrieving order details.")
            return []



class ActionLogTicket(Action):
    def name(self) -> Text:
        return "action_log_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        order_id = next(tracker.get_latest_entity_values("order_id"), None)

        if not order_id:
            dispatcher.utter_message(response="utter_ask_again")
        else:
            dispatcher.utter_message(response="utter_ticket_logged")

        return []
    
class ActionDelayedGreeting(Action):
    def name(self) -> Text:
        return "action_delayed_greeting"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # First greeting message
        dispatcher.utter_message(text="Hello, I am your Shop Sphere chatbot.")
        time.sleep(0.2)  # Reduced delay: 0.2 seconds instead of 1 second
        # Second greeting message
        dispatcher.utter_message(text="How can I help you today? Just write in the text box or use one of our quick answers.")
        time.sleep(0.2)  # Reduced delay before sending buttons
        # Send buttons as a separate message (with non-empty text to ensure they're rendered)
        dispatcher.utter_message(
            text=" ",
            buttons=[
                {"title": "A delivery, return or refund", "payload": "/ask_help"},
                {"title": "My Account", "payload": "/my_account"},
                {"title": "Something else", "payload": "/something_else"}
            ]
        )
        return []
    
