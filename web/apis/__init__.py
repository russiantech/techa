

# Payment Helpers
import os
import random, string
import requests
import json
from typing import Optional

token = os.environ.get('FLWSECK') #production-key
#token = environ.get('FLWSECKT')
tx_ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
title='Russian Developers'
description = 'Advanced Courses'
redirect_url = '/callback'
logo = os.environ.get('LOGO')

def initiate_payment(
    tx_ref: str, amount: float, redirect_url: str, customer_email: str,  customer_name: Optional[str] = None, currency: Optional[str] = None, payment_options: Optional[str] = None,
    title: Optional[str] = None, description: Optional[str] = None, customer_phone_number: Optional[str] = None,
    ) -> str:
    """This is used to initiate standard payments. It takes in the arguments and returns the url to redirect users for payments """
    payment_url = "https://api.flutterwave.com/v3/payments"
    payload = json.dumps({
        "tx_ref": f"{tx_ref}",
        "amount": f"{amount}",
        "currency": f"{currency}".upper(),
        "redirect_url": f"{redirect_url}",
        "payment_options": payment_options,
        "customer": {
            "email": f"{customer_email}",
            "phonenumber": f"{customer_phone_number}",
            "name": f"{customer_name}"
        },
        "customizations": {
            "title": f"{title}",
            "description": f"{description}",
            "logo": f"{logo}"
        }
    })
    headers = { 'Authorization': f'Bearer {token}', 'Content-Type': 'application/json', }

    response = requests.request(method="POST", url=payment_url, headers=headers, data=payload)
    link = response.json()["data"]["link"]
    return link

def get_payment_details(txn_id: str) -> dict:
    """
    Takes the transaction_id from the request and returns the status info in json.
    It transaction_id is different from the transaction_ref so it should be grabbed from the request in the redirect url
    """
    url = f"https://api.flutterwave.com/v3/transactions/{txn_id}/verify"

    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return dict(response.json())

def trigger_mpesa_payment(tx_ref: str, amount: float, currency: str, phone_number: str, full_name: str,
                          email: Optional[str] = None) -> dict:
    """
    This will automatically trigger an MPESA payment in form of an STK Push from your customer. It will return a
    dictionary with details regarding the transaction. Flutterwave will also send the status to your webhook configured
    in the dashboard.
    """
    url = "https://api.flutterwave.com/v3/charges?type=mpesa"

    payload = json.dumps({
        "tx_ref": f"{tx_ref}",
        "amount": f"{amount}",
        "currency": f"{currency}".upper(),
        "email": f"{email}",
        "phone_number": f"{phone_number}",
        "fullname": f"{full_name}"
    })
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return dict(response.json())

def initiate_ussd_payment(tx_ref: str, account_bank: str, amount: float, email: str, phone_number: str, full_name: str) -> dict:
    """
    :param tx_ref: str
    :param account_bank: str
    :param amount: float
    :param email: str
    :param phone_number: str
    :param full_name: str
    :return: dict
    """
    url = "https://api.flutterwave.com/v3/charges?type=ussd"
    payload = json.dumps({
        "tx_ref": f"{tx_ref}",
        "account_bank": f"{account_bank}",
        "amount": f"{amount}",
        "currency": "NGN",
        "email": f"{email}",
        "phone_number": f"{phone_number}",
        "fullname": f"{full_name}"
    })
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    return dict(response.json())

def verify_bank_account_details(account_number: str, account_bank: str) -> dict:
    """
    Takes the customer's account number and bank code as args and returns a dict with data on the customer's account
    :param account_number: str
    :param account_bank: str
    :return: dict
    """

    url = "https://api.flutterwave.com/v3/accounts/resolve"

    payload = json.dumps({
        "account_number": f"{account_number}",
        "account_bank": f"{account_bank}"
    })
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    return dict(response.json())

def verify_card_details(card_bin: str) -> dict:
    """
    Returns a python dict with the info from querying the results.
    :param card_bin: str
    :return: dict
    """
    url = f"https://api.flutterwave.com/v3/card-bins/{card_bin}"

    payload = {}
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return dict(response.json())
