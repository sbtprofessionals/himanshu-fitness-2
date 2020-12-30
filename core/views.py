from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.urls import reverse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from .models import MemeberShipPayment, MemeberShipRequest
from .paytm import CheckSum
from django.core.mail import send_mail
import random
import json
import requests
MID = "VdMxPH61970223458566"  # MERCHANT ID
MKEY = "1xw4WBSD%bD@ODkL"  # MERCHANT KEY

def index(request):
    obj = MemeberShipRequest.objects.all()

    print('............',obj)
    # MemeberShipRequest.objects.all().delete()
    return render(request, 'index.html')

def payment(request):
    return render(request, 'payment-form.html',{'plan_id':0})



def purchase_membership(request, plan_id):
    try:
        if request.method == 'GET':
            return HttpResponse({'soome sort of error'})

        name = 'test'#request.POST.get('name')
        phno = '8708046736'#request.POST.get('phno')
        email = 'test@test.com'#request.POST.get('email')
        order_id = str(random.randint(0,9999))
        obj = MemeberShipRequest(name = name, phone=phno, email=email, order_id=order_id)
        obj.save()
        # sending details to paytm gateway in form of dict
        detail_dict = {
            "MID": MID,
            "WEBSITE": "WEBSTAGING",
            "INDUSTRY_TYPE_ID": "Retail",
            "CUST_ID": str(email),
            "CHANNEL_ID": "WEB",
            "ORDER_ID": order_id,
            "TXN_AMOUNT": "1234",
            "CALLBACK_URL": f'http://127.0.0.1:8000/paytm_request_handler',
        }   
        param_dict = detail_dict
        CheckSum.generateSignature
        param_dict['CHECKSUMHASH'] = CheckSum.generateSignature(
        detail_dict, MKEY)

        return render(request, 'redirect.html', {'detail_dict': param_dict})
    except:
        return HttpResponse('An UnExpected Error Occured')

@csrf_exempt
def req_handler(request):
    if request.method == 'POST':
        response_dict = dict()
        form = request.POST
        # another if to handle if user load refresh
        is_order_exist = MemeberShipPayment.objects.filter(order_id=form["ORDERID"]).exists()
        if is_order_exist == False:
            # FOR ALL VALUES
            for i in form.keys():
                response_dict[i] = form[i]
                if i == "CHECKSUMHASH":
                    response_check_sum = form[i]

            verify = CheckSum.verifySignature(response_dict, MKEY, response_check_sum)
            # response_dict["STATUS"] = "PENDING"

            if(verify and response_dict["STATUS"] != "TXN_FAILURE") or (verify and response_dict["STATUS"] == "PENDING"):
                order_payment = MemeberShipPayment()
                # id = models.AutoField(primary_key = True)
                order = MemeberShipRequest.objects.get(order_id=response_dict["ORDERID"])

                order_payment.order_summary = order
                # paytm responses
                order_payment.currency = response_dict["CURRENCY"]
                order_payment.gateway_name = response_dict["GATEWAYNAME"]
                # Txn Success
                order_payment.response_message = response_dict["RESPMSG"]
                # order_payment.bank_name = response_dict["BANKNAME"] # WALLET
                # PPI
                order_payment.Payment_mode = response_dict["PAYMENTMODE"]
                # MID = models.CharField(max_length=8) # VdMxPH61970223458566
                order_payment.response_code = response_dict["RESPCODE"]  # 01
                # 20200905111212800110168406201874634
                order_payment.txn_id = response_dict["TXNID"]
                # 2400.00
                order_payment.txn_amount = response_dict["TXNAMOUNT"]
                order_payment.order_id = response_dict["ORDERID"]  # 6556
                order_payment.status = response_dict["STATUS"]  # TXN_SUCCESS
                # 63209779
                order_payment.bank_txn_id = response_dict["BANKTXNID"]
                # 2020-09-05 18:51:59.0
                order_payment.txn_date = response_dict["TXNDATE"]
                # order_payment.refund_amount =  #  0.00
                order_payment.save()
                order_id=response_dict["ORDERID"]
                return HttpResponse({f'Order Successfully Placed. <a href="{reverse("home")}">Go back to home</a>'})
            else:
                MemeberShipRequest.objects.filter(
                    order_id=response_dict["ORDERID"]).delete()
                print(MemeberShipRequest.objects.all())
                return HttpResponse(f'Order is not Placed Because of some error. Please <a href="{reverse("payment")}">Try Again </a>')
        else:
            return HttpResponse(f'''Already Placed Order, check your order by typing your Id here 
                                <form method="POST" action="{reverse('order-status')}">
                                    <input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">
                                    Enter Here<input name="order-id"></input>
                                    <button>Submit</button>
                                </form>
                                ''')
    return HttpResponse('Invalid Request')


def order_status(request):
    try:
        if request.method =='POST':
            slug = request.POST.get('order-id')
            if MemeberShipRequest.objects.filter(order_id = slug).exists():
                paytmParams = dict()
                
                paytmParams["MID"] = MID
                paytmParams["ORDERID"] = slug
                
                checksum = CheckSum.generateSignature(paytmParams, MKEY)

                paytmParams["CHECKSUMHASH"] = checksum

                post_data = json.dumps(paytmParams)

                # for Staging
                url = "https://securegw-stage.paytm.in/order/status"

                # for Production
                # url = "https://securegw.paytm.in/order/status"

                response = requests.post(url, data=post_data, headers={
                                            "Content-type": "application/json"}).json()
                
                if response["STATUS"] == "TXN_SUCCESS":
                    obj = MemeberShipPayment.objects.get(order_id=slug)
                    obj.status = response["STATUS"]
                    obj.response_code = response["RESPCODE"]
                    obj.response_message = response["RESPMSG"]
                    obj.txn_date = response["TXNDATE"]
                    obj.bank_name = response["BANKNAME"]
                    obj.save()
                    return HttpResponse(f"order success fully placed")
                return HttpResponse("order is still in pending state")
            return HttpResponse("Invalid Request")
        return render(request ,'form.html')
    except Exception as e:
        return HttpResponse(f"Requested Order Not Found")


def contact_via_mail(request):
    if request.method == 'POST':
        if request.is_ajax():

            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            description = request.POST.get('description')
            
            send_mail(
                    subject=subject,
                    message=f'from : {email} name : {name}<br>, {description}',
                    from_email="rk7305758@gmail.com",
                    recipient_list=["paliwalap7@gmail.com",],
                    fail_silently=False,
                )
            return JsonResponse({'status': 'OK'})
    return JsonResponse({'status':'An Error Occured !'})