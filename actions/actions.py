# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# function for accessing the site

import json
import logging
import sys

import requests
from rasa_sdk.executor import CollectingDispatcher

# def get_new_token():
#     auth_server_url = "https://10.64.1.150:9002/authorizationserver/oauth/token"
#     client_id = 'sandbox'
#     client_secret = '1234'
#
#     token_req_payload = {'grant_type': 'client_credentials'}
#
#     token_response = requests.post(auth_server_url, data=token_req_payload, verify=False, allow_redirects=False,
#                                    auth=(client_id, client_secret))
#
#     print(token_response)
#
#     if token_response.status_code != 200:
#         print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
#         sys.exit(1)
#     else:
#         print("Successfully obtained a new token")
#         tokens = json.loads(token_response.text)
#         print(tokens)
#         return tokens['access_token']


# time.sleep(30)
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionOrderStatus(Action):

    def name(self) -> Text:
        return "action_order_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.captureWarnings(True)

        test_api_url = "https://10.64.1.150:9002/wurthwebservices/v2/wurthusa/users/s22655/orders"
        auth_server_url = "https://10.64.1.150:9002/authorizationserver/oauth/token"
        client_id = 'sandbox'
        client_secret = '1234'

        token_req_payload = {'grant_type': 'client_credentials'}

        token_response = requests.post(auth_server_url, data=token_req_payload, verify=False, allow_redirects=False,
                                       auth=(client_id, client_secret))

        print(token_response)

        if token_response.status_code != 200:
            print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
            sys.exit(1)
        else:
            print("Successfully obtained a new token")
            tokens = json.loads(token_response.text)
            print(tokens)
        token = tokens
        print("this is the token\n")
        print("Reached here")
        print(token)
        print(type(token))
        print("\nAbove is the token")

        # while True:

        api_call_headers = {'Authorization': 'Bearer ' + token['access_token']}
        api_call_response = requests.get(test_api_url, headers=api_call_headers, verify=False)
        # print(api_call_response)
        print(api_call_headers)
        # ##
        # ##
        # if api_call_response.status_code == 401:
        #     print("Internet issues")
        # else:
        print("API is sending response")

        response = api_call_response.json()
        print(response)
        entities = tracker.latest_message['entities']
        print("These are the entities ", entities)
        order_code = None
        for e in entities:
            if e['entity'] == "order_code":
                order_code = e['value']
                print(order_code)

        for data in response['orders']:
            if data["code"] == order_code.title():
                print(data)
                a1 = data['code']
                a2 = data['placed']
                a3 = data['status']
                a4 = data['total']['formattedValue']

        date = a2.split("T")[0]
        time = (a2.split("T")[1]).split("+")[0]
        dispatcher.utter_message(text=" Order Number: " + a1)
        dispatcher.utter_message(text="Created On: " + date + " " + time)
        dispatcher.utter_message(text="Order Status: " + a3)
        dispatcher.utter_message(text="Total Value: " + a4)
        dispatcher.utter_message(text="Can I help you with something else?",
                                 buttons=[
                                     {"payload": "/affirm", "title": "Yes"},
                                     {"payload": "/deny", "title": "No"},
                                 ])

        return []


class ActionProductSearch(Action):

    def name(self) -> Text:
        return "action_product_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        entities = tracker.latest_message['entities']
        print("These are the entities ", entities)
        search_code = None
        for e in entities:
            if e['entity'] == "search_code":
                search_code = e['value']
                print(search_code)

        product_url = "https://10.64.1.150:9002/wurthwebservices/v2/wurthusa/products/search?currentPage=0&fields=DEFAULT&pageSize=20&query=" + search_code
        product_response = requests.get(product_url,
                                        verify=False).json()
        print(product_response)

        products_info = []  # empty list - to store all the product dictionaries
        name = []
        string = []
        url = []
        price = []
        img_url = []

        for data in product_response['products']:
            products_info.append(data)

        # new_carousel = {}

        for i in range(5):
            name.append(products_info[i]['name'])
            string = products_info[i]['url']
            url.append("https://10.64.1.150:9002/" + string)
            price.append(products_info[i]['price']['formattedValue'])
            print(name)
            print(url)
            print(price)

        temp_img_url = []
        for i in range(5):
            # print(products_info[i]['images'])
            for j in products_info[i]['images']:
                if j["format"] == 'product':
                    temp_img_url.append(j)

        for i in temp_img_url:
            # print(i['url'])
            img_url.append("https://10.64.1.150:9002/" + i['url'])

        # Carousel display in the chatbot
        new_carousel = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": name[0],
                        "subtitle": price[0],
                        "image_url": img_url[0],
                        "buttons": [
                            {
                                "title": "Details",  # details
                                "url": url[0],  # url of the result
                                "type": "web_url",
                            }
                        ]
                    },
                    {
                        "title": name[1],
                        "subtitle": price[1],
                        "image_url": img_url[1],
                        "buttons": [
                            {
                                "title": "Details",  # details
                                "url": url[1],  # url of the result
                                "type": "web_url",
                            }
                        ]
                    },
                    {
                        "title": name[2],
                        "subtitle": price[2],
                        "image_url": img_url[2],
                        "buttons": [
                            {
                                "title": "Details",  # details
                                "url": url[2],  # url of the result
                                "type": "web_url",
                            }
                        ]
                    },
                    {
                        "title": name[3],
                        "subtitle": price[3],
                        "image_url": img_url[3],
                        "buttons": [
                            {
                                "title": "Details",  # details
                                "url": url[3],  # url of the result
                                "type": "web_url",
                            }
                        ]
                    },
                    {
                        "title": name[4],
                        "subtitle": price[4],
                        "image_url": img_url[4],
                        "buttons": [
                            {
                                "title": "Details",  # details
                                "url": url[4],  # url of the result
                                "type": "web_url",
                            }
                        ]
                    }

                ]
            }
        }
        website_url = "https://10.64.1.150:9002/" + product_response["currentQuery"]['url']
        message = "For more results, Please [click here]({}) ".format(website_url)
        dispatcher.utter_message(text="These are the top 5 results I found for you.")
        dispatcher.utter_message(attachment=new_carousel)
        dispatcher.utter_message(text=message)
        # dispatcher.utter_message(text="For more details visit this url ")
        # dispatcher.utter_message("https://10.64.1.150:9002/" + product_response["currentQuery"]['url'])
        dispatcher.utter_message(text="Can I help you with something else?",
                                 buttons=[
                                     {"payload": "/affirm", "title": "Yes"},
                                     {"payload": "/deny", "title": "No"},
                                 ])

        return []
