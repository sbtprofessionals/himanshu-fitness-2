from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render(request, 'index.html')

def payment(request):
    return render(request, 'payment-form.html')


def purchase_customer(request, slug):# plan_id, user, amount,discount,role):
    category = Categories.objects.all()

    plan = Plan.objects.get(plan_id =slug)
    dict_for_review = {
        'id' : plan.plan_id,
        'name': plan.plan_name,
        'amount': plan.plan_amount,
        'description_1': plan.description_1,
        'description_2': plan.description_2,
        'description_3': plan.description_3,
        'description_4': plan.description_4,
    }
    return render(request, 'website/forms/purchase_form_customer.html', {'plan': plan, 'plan_review': dict_for_review, 'category': category})

def purchase_membership(request, plan_id):

    if request.method == 'POST':

        if request.user.is_authenticated:
            is_vendor = request.POST.get('is_vendor')
            discount = request.POST.get('discount')
            plan = Plan.objects.get(plan_id = plan_id)
            customer = Customer()
            customer.user = request.user
            # customer.customer_id = models.
            #
            #
            #
            # (primary_key=True)
            customer.customer_name = request.POST.get('name')
            customer.last_name = 'Paliwal'
            customer.Address = request.POST.get('address')
            customer.city = request.POST.get('city')
            customer.state = request.POST.get('state')
            customer.zipcode = request.POST.get('zip_code')
            customer.EmailID = request.POST.get('email_id')
            customer.joining_date = timezone.datetime.now()
            customer.gender = 'Alpha Male'
            customer.extra_Info = 'got need a card to swipe'
            customer.Contact_Person = 'GEAZY'
            customer.customer_is_active = True
            customer.subscription_plan_taken = plan

            customer.save()
            user = User.objects.filter(id=request.user.id).first()
            phone = user.phone
            try:
                plan = Plan.objects.get(plan_id=plan_id)
            except:
                return HttpResponse('Please enter a valid Plan Id')

            try:
                discount = int(request.POST.get('discount'))
            except ValueError:
                return HttpResponse('Please select a valid discount value')

            user_amount= plan.plan_amount
            if discount != "" and discount != None:
                response_dict = discount_validation(plan_id, discount, user_amount, is_vendor)
                if response_dict['error'] != None:
                    return HttpResponse(response_dict['error'])
                amount = discount * plan.plan_amount
            else:
                amount = plan.plan_amount

            order_id = random.randint(1, 999999)
            email_id = request.POST.get('email_id')
            name = request.POST.get('name')
            address =request.POST.get('address')
            state =  request.POST.get('state')
            city = request.POST.get('city')
            zip_code = request.POST.get('zip_code')
            plan_id = plan.plan_id

            # Check if user not provide any discount value
            order = Order(name=name, user=user, phone=phone, address=address, city=city,
                            state=state, zip_code=zip_code, amount=amount, discount=discount,order_id=order_id, plan_id=plan, order_completed=False,role='customer')
            order.save()

            # sending details to paytm gateway in form of dict
            detail_dict = {
                "MID": parameters['merchant_id'],
                "WEBSITE": "WEBSTAGING",
                "INDUSTRY_TYPE_ID": "Retail",
                "CUST_ID": str(email_id),
                "CHANNEL_ID": "WEB",
                "ORDER_ID": str(order_id),
                "TXN_AMOUNT": str(amount),
                "CALLBACK_URL": f'{parameters["BASE_URL"]}/sbt/req_handler',
            }

            param_dict = detail_dict
            CheckSum.generateSignature
            param_dict['CHECKSUMHASH'] = CheckSum.generateSignature(
                detail_dict, parameters['merchant_key'])
            # print('.................', param_dict)
            return render(request, 'redirect.html', {'detail_dict': param_dict})

        return HttpResponse('Either amount or Discount not Matched')
    return render(request, 'checkout2.html', {'plan': plan})  # for checkout
    # except Exception as e:
    #     print("An Exception occur \n", e)
    #     return HttpResponse(e)


@csrf_exempt
def req_handler(request):
    if request.method == 'POST':
        response_dict = dict()
        form = request.POST
        role = {
        'customer': 'customer',
        'vendor': 'vendor',
            }
        # another if to handle if user load refresh
        is_order_exist = Order_Payment.objects.filter(order_id=form["ORDERID"]).exists()
        if is_order_exist == False:
            # FOR ALL VALUES
            for i in form.keys():
                response_dict[i] = form[i]
                if i == "CHECKSUMHASH":
                    response_check_sum = form[i]

            verify = CheckSum.verifySignature(response_dict, parameters['merchant_key'], response_check_sum)
            # response_dict["STATUS"] = "PENDING"
            if verify and response_dict["STATUS"] != "TXN_FAILURE" or response_dict["STATUS"] == "PENDING":
                order_payment = Order_Payment()
                usr = User
                # id = models.AutoField(primary_key = True)
                order = Order.objects.get(order_id=response_dict["ORDERID"])


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
                payment_status = Order_Payment.objects.get(
                    order_id=response_dict["ORDERID"])

                if order.role == 'customer':
                    user = order_payment.order_summary.user
                    user.is_customer_paid =True
                    user.customer_discount = order.discount
                    user.save()
                    customer = Customer.objects.filter(user=user).first()
                    customer.subscription_plan_taken = order_payment.order_summary.plan_id
                    customer.save()
                else:
                    user = order_payment.order_summary.user
                    user.is_vendor_paid = True
                    user.save()
                    vendor = Vendor.objects.filter(user=user).first()
                    vendor.registration_fee = order_payment.order_summary.plan_id
                    vendor.save()

                return render(request, 'ordersucess.html', {'payment': payment_status})
            else:
                Order.objects.filter(
                    order_id=response_dict["ORDERID"]).delete()
                return HttpResponse('Order is not Placed Because of some error. Please <a href="/sbt/">Try Again </a>')
        else:
            payment_status = Order_Payment.objects.get(
                order_id=form["ORDERID"])
            # Session should create when order is get successfull

            return HttpResponse('Your payment  failed')
    return HttpResponse('Invalid Request')


def order_status(request, slug):
    try:
        obj = Order_Payment.objects.get(order_id=slug)
        obj2 = obj.order_summary
        if obj2.user == request.user:
            paytmParams = dict()

            paytmParams["MID"] = parameters['merchant_id']
            paytmParams["ORDERID"] = slug

            checksum = CheckSum.generateSignature(paytmParams, parameters['merchant_key'])

            paytmParams["CHECKSUMHASH"] = checksum

            post_data = json.dumps(paytmParams)

            # for Staging
            url = "https://securegw-stage.paytm.in/order/status"

            # for Production
            # url = "https://securegw.paytm.in/order/status"

            response = requests.post(url, data=post_data, headers={
                                     "Content-type": "application/json"}).json()

            if response["STATUS"] == "TXN_SUCCESS":
                obj = Order_Payment.objects.get(order_id=slug)
                obj.status = response["STATUS"]
                obj.response_code = response["RESPCODE"]
                obj.response_message = response["RESPMSG"]
                obj.txn_date = response["TXNDATE"]
                obj.bank_name = response["BANKNAME"]
                obj.save()
                return HttpResponse("order success fully placed")

            return HttpResponse("order is still in pending state")

        elif request.user != None and request.user.is_authenticated:
            return HttpResponse("Please insert correct orderid")
        else:
            return HttpResponse('Please Login <a href="/sbt/login"> Here First</a>')
    except Exception as e:
        return HttpResponse(f"Requested Order Not Found - {e}")  # form to type in order id"""
