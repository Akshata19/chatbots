import time
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

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