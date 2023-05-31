import requests
import threading
from time import sleep

# Global Variables
COOKIE = "Your cookie"
AUTHORIZATION = "Your authorization"
PAYMENT_INSTRUMENT_ID = "Your payment instrument id"
USER_AGENT = "Your user agent"
VEHICLE_HANDLES = ["vehicle1", "vehicle2", "vehicle3"]  # Replace with your vehicle handles

class BoltRideManager:
    BASE_URL = "https://germany-rental.taxify.eu"
    HEADERS = {
        "Host": "germany-rental.taxify.eu",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en;q=0.9",
        "Cache-Control": "no-cache"
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.session.headers.update({"Cookie": COOKIE, "Authorization": AUTHORIZATION, "User-Agent": USER_AGENT})
        self.payment_instrument_id = PAYMENT_INSTRUMENT_ID

    def create_and_start_order(self, vehicle_handle):
        data = {
            "vehicle_handle": {"value": vehicle_handle, "type": "uuid"},
            "source": "single_order",
            "payment_instrument_id": self.payment_instrument_id
        }
        return self.send_request('POST', "/micromobility/user/ui/order/createAndStart", data)

    def get_active_order(self, id_value, vehicle_handle):
        data = {
            "source": "single_order",
            "order_id": id_value,
            "vehicle_handle": {"value": vehicle_handle, "type": "uuid"}
        }
        return self.send_request('POST', "/micromobility/user/ui/order/getActive", data)

    def finish_order(self, getactive1_id_value):
        data = {
            "gps_lat" : "50.092434640968932",
            "order_id" : getactive1_id_value,
            "gps_lng" : "8.2257654130646571"
        }
        return self.send_request('POST', "/micromobility/user/order/finish", data)

    def confirm_order_finish(self, getactive1_id_value):
        data = {
            "order_id" : getactive1_id_value,
            "gps_lng" : 8.2257654130646571,
            "gps_lat" : 50.092434640968932,
            "confirmed_view_keys" : ["photo_capture_key"]
        }
        return self.send_request('POST', "/micromobility/user/order/finish", data)
    
    def send_request(self, method, endpoint, data):
        try:
            response = self.session.request(method, self.BASE_URL + endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"Other error occurred: {err}")

def thread_handler(vehicle_handle, bolt_ride_manager):
    try:
        response = bolt_ride_manager.create_and_start_order(vehicle_handle)
        id_value = response.get('data', {}).get('order', {}).get('id')

        sleep(5)

        get_active_order_response = bolt_ride_manager.get_active_order(id_value, vehicle_handle)
        get_active_order_id_value = get_active_order_response.get('data', {}).get('order', {}).get('id')

        sleep(5)

        bolt_ride_manager.finish_order(get_active_order_id_value)
        sleep(5)

        bolt_ride_manager.confirm_order_finish(get_active_order_id_value)
        print("Ride finished for vehicle handle", vehicle_handle)
    except Exception as e:
        print("Error occurred:", e)

def main():
    bolt_ride_manager = BoltRideManager()
    threads = []
    for vehicle_handle in VEHICLE_HANDLES:
        t = threading.Thread(target=thread_handler, args=(vehicle_handle, bolt_ride_manager))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
