# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Swiggy Order Analysis

import requests
from datetime import datetime
from collections import namedtuple
from typing import List, Tuple, Optional

OrderItem = namedtuple("OrderItem", ("name", "is_veg", "quantity", "price"))
Order = namedtuple(
    "Order",
    (
        "id_",
        "items",
        "time_of_order",
        "restaurant_name",
        "restaurant_cuisine",
        "total_price",
        "delivery_time_in_seconds",
        "restaurant_lat_lng",
        "restaurant_customer_distance",
        "tax",
    ),
)

# +
SWIGGY_API_URL = "https://www.swiggy.com/dapi"
LATITUDE, LONGTITUDE = 27.17389166904579, 78.04206884387684


class ApiPaths:
    CSRF = f"{SWIGGY_API_URL}/restaurants/list/v5?lat={LATITUDE}&lng={LONGTITUDE}&page_type=DESKTOP_WEB_LISTING"
    ORDERS = f"{SWIGGY_API_URL}/order/all?order_id={{last_order_id}}"
    SEND_OTP = f"{SWIGGY_API_URL}/auth/sms-otp"
    VERIFY_OTP = f"{SWIGGY_API_URL}/auth/otp-verify"


HEADERS = {
    "referer": "https://www.swiggy.com/my-account",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "authority": "www.swiggy.com",
}
# -

session = requests.Session()


def get_csrf_token(session: requests.Session) -> Optional[str]:
    resp = session.get(ApiPaths.CSRF, headers=HEADERS)
    return resp.json()["csrfToken"] if resp.ok else None


# +
def send_otp(session: requests.Session, csrf_token: str, phone_number: str) -> bool:
    send_otp_data = {"mobile": phone_number, "_csrf": csrf_token}
    resp = session.post(ApiPaths.SEND_OTP, headers=HEADERS, data=send_otp_data)
    return resp.ok


def verify_otp(session: requests.Session, csrf_token: str, otp: str) -> bool:
    verify_otp_data = {"otp": otp, "_csrf": csrf_token}
    resp = session.post(ApiPaths.VERIFY_OTP, headers=HEADERS, data=verify_otp_data)
    return resp.ok


def do_otp_authflow(session: requests.Session) -> bool:
    csrf_token = get_csrf_token(session)

    if not csrf_token:
        return False

    return send_otp(session, csrf_token, input("Enter phone number: ")) and verify_otp(
        session, csrf_token, input("Enter OTP: ")
    )


# -

# ### OTP Authflow (Enter details here)

# +
authflow_result = do_otp_authflow(session)

if not authflow_result:
    raise Exception("OTP authorization failed!")


# -


def get_orders(session: requests.Session, last_order_id="") -> dict:
    response = session.get(
        ApiPaths.ORDERS.format(last_order_id=last_order_id), headers=HEADERS
    )

    return response.json()


# +
def parse_time(time: str) -> datetime:
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(time, DATETIME_FORMAT)


def parse_lat_lng(lat_lng: str) -> Tuple[float, float]:
    return tuple(float(co_ord) for co_ord in lat_lng.split(",", 2))


# -


def get_items_ordered(order: dict) -> List[OrderItem]:
    return [
        OrderItem(
            name=item["name"],
            is_veg=bool(int(item["is_veg"])),
            quantity=int(item["quantity"]),
            price=float(item["final_price"]),
        )
        for item in order["order_items"]
    ]


def get_all_orders(session: requests.Session) -> List[Order]:
    last_order_id = ""
    all_orders = []

    while True:
        orders = get_orders(session, last_order_id)["data"]["orders"]

        if len(orders) < 1:
            break

        all_orders += [
            Order(
                id_=order["order_id"],
                items=get_items_ordered(order),
                time_of_order=parse_time(order["order_time"]),
                restaurant_name=order["restaurant_name"],
                restaurant_cuisine=order["restaurant_cuisine"],
                total_price=order["order_total_with_tip"],
                delivery_time_in_seconds=int(order["delivery_time_in_seconds"]),
                restaurant_lat_lng=parse_lat_lng(order["restaurant_lat_lng"]),
                restaurant_customer_distance=float(
                    order["restaurant_customer_distance"]
                ),
                tax=order["order_tax"],
            )
            for order in orders
        ]

        last_order_id = orders[-1]["order_id"]

    return all_orders


all_orders = get_all_orders(session)

import plotly.graph_objects as go
from itertools import accumulate
from operator import add as ADD_OPERATOR
from collections import Counter

# ### Order counts over time

# +
time_of_orders = sorted([order.time_of_order for order in all_orders])
order_counts = [i + 1 for i in range(len(all_orders))]

figure = go.Figure([go.Scatter(x=time_of_orders, y=order_counts)])
figure.show()
# -

# ### Total amount spent over time

# +
orders = sorted([order for order in all_orders], key=lambda order: order.time_of_order)
time_of_orders = [order.time_of_order for order in orders]
order_prices = list(accumulate([order.total_price for order in orders], ADD_OPERATOR))


figure = go.Figure([go.Scatter(x=time_of_orders, y=order_prices)])
figure.show()
# -

# ### Top 10 restaurants orders were placed in

# +
restaurant_order_counts = Counter([order.restaurant_name for order in all_orders])
top_10_restaurants_ordered_from = restaurant_order_counts.most_common(10)
top_10_restaurants_total_spending = [
    sum(
        [
            order.total_price
            for order in all_orders
            if order.restaurant_name == restaurant
        ]
    )
    for restaurant, order_count in top_10_restaurants_ordered_from
]

fig = go.Figure(
    data=[
        go.Bar(
            x=[
                restaurant
                for restaurant, order_count in top_10_restaurants_ordered_from
            ],
            y=[
                order_count
                for restaurant, order_count in top_10_restaurants_ordered_from
            ],
            hovertext=[
                f"₹{spending}" for spending in top_10_restaurants_total_spending
            ],
        )
    ]
)
fig.show()
