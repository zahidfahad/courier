import string
import random
from django.conf import settings

from sslcommerz_lib import SSLCOMMERZ
from accounting.models import WalletModel
from django.db.models import Sum
from django.shortcuts import render, HttpResponseRedirect, reverse


def unique_trangection_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def sslcommerz_payment_gateway(request, amount, unique_id):
    user_id = request.user.id
    unique_id = unique_id.replace('#', '')
    name = request.user.first_name + ' ' + request.user.last_name
    settings = {'store_id': 'essen606bf39191551',
                'store_pass': 'essen606bf39191551@ssl', 'issandbox': True}
    sslcommez = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = unique_trangection_id_generator()
    post_body['success_url'] = 'http://127.0.0.1:8000/success/payments/' + str(user_id) + '/' + unique_id + '/'
    post_body['fail_url'] = 'http://127.0.0.1:8000/failed/payments/'
    post_body['cancel_url'] = 'http://127.0.0.1:8000/create-order/'
    post_body['ipn_url'] = ''
    post_body['emi_option'] = 0
    post_body['cus_name'] = name
    post_body['cus_email'] = 'request.data["email"]'
    post_body['cus_phone'] = 'request.data["phone"]'
    post_body['cus_add1'] = 'request.data["address"]'
    post_body['cus_city'] = 'request.data["address"]'
    post_body['cus_country'] = 'Bangladesh'
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"

    # OPTIONAL PARAMETERS
    post_body['value_a'] = name

    response = sslcommez.createSession(post_body)
    return 'https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY=' + response["sessionkey"]


def sslcommerz_wallet_gateway(request, amount):
    user_id = request.user.id
    name = request.user.first_name + ' ' + request.user.last_name
    settings = {'store_id': 'essen606bf39191551',
                'store_pass': 'essen606bf39191551@ssl', 'issandbox': True}
    scs_url = 'http://127.0.0.1:8000/add/success/' + str(user_id) + '/'
    sslcommez = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = unique_trangection_id_generator()
    post_body['success_url'] = scs_url
    post_body['fail_url'] = 'http://127.0.0.1:8000/failed/add/'
    post_body['cancel_url'] = 'http://127.0.0.1:8000/add/to/wallet/'
    post_body['ipn_url'] = 'http://127.0.0.1:8000/add/to/wallet/'
    post_body['emi_option'] = 0
    post_body['cus_name'] = name
    post_body['cus_email'] = 'request.data["email"]'
    post_body['cus_phone'] = 'request.data["phone"]'
    post_body['cus_add1'] = 'request.data["address"]'
    post_body['cus_city'] = 'request.data["address"]'
    post_body['cus_country'] = 'Bangladesh'
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"

    # OPTIONAL PARAMETERS
    post_body['value_a'] = name

    response = sslcommez.createSession(post_body)
    return 'https://sandbox.sslcommerz.com/gwprocess/v4/gw.php?Q=pay&SESSIONKEY=' + response["sessionkey"]


# def ssl_commerz_IPN():
#     settings = {'store_id': 'essen606bf39191551',
#                 'store_pass': 'essen606bf39191551@ssl', 'issandbox': True}
#
#     sslcommez = SSLCOMMERZ(settings)
#     post_body = {}
#     post_body['tran_id'] = '5E121A0D01F92'
#     post_body['val_id'] = '200105225826116qFnATY9sHIwo'
#     post_body['amount'] = "10.00"
#     post_body['card_type'] = "VISA-Dutch Bangla"
#     post_body['store_amount'] = "9.75"
#     post_body['card_no'] = "418117XXXXXX6675"
#     post_body['bank_tran_id'] = "200105225825DBgSoRGLvczhFjj"
#     post_body['status'] = "VALID"
#     post_body['tran_date'] = "2020-01-05 22:58:21"
#     post_body['currency'] = "BDT"
#     post_body['card_issuer'] = "TRUST BANK, LTD."
#     post_body['card_brand'] = "VISA"
#     post_body['card_issuer_country'] = "Bangladesh"
#     post_body['card_issuer_country_code'] = "BD"
#     post_body['store_id'] = "test_testemi"
#     post_body['verify_sign'] = "d42fab70ae0bcbda5280e7baffef60b0"
#     post_body[
#         'verify_key'] = "amount,bank_tran_id,base_fair,card_brand,card_issuer,card_issuer_country,card_issuer_country_code,card_no,card_type,currency,currency_amount,currency_rate,currency_type,risk_level,risk_title,status,store_amount,store_id,tran_date,tran_id,val_id,value_a,value_b,value_c,value_d"
#     post_body['verify_sign_sha2'] = "02c0417ff467c109006382d56eedccecd68382e47245266e7b47abbb3d43976e"
#     post_body['currency_type'] = "BDT"
#     post_body['currency_amount'] = "10.00"
#     post_body['currency_rate'] = "1.0000"
#     post_body['base_fair'] = "0.00"
#     post_body['value_a'] = ""
#     post_body['value_b'] = ""
#     post_body['value_c'] = ""
#     post_body['value_d'] = ""
#     post_body['risk_level'] = "0"
#     post_body['risk_title'] = "Safe"
#     response = sslcommez.hash_validate_ipn(post_body)
#     print(response)


def refund_api(bank, amount, remark):

    settings = {'store_id': 'essen606bf39191551', 'store_pass': 'essen606bf39191551@ssl', 'issandbox': True}
    sslcommez = SSLCOMMERZ(settings)

    bank_tran_id = bank
    refund_amount = amount
    refund_remarks = remark
    response = sslcommez.init_refund(bank_tran_id, refund_amount, refund_remarks)
    print(response)
