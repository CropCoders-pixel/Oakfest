from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import generate_phonepe_qr
from django.conf import settings
import razorpay

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@api_view(['POST'])
def create_order(request):
    amount = request.data.get('amount')
    if not amount:
        return Response({'error': 'Amount is required'}, status=400)

    if request.data.get('payment_method') == 'phonepe':
        farmer_phone = request.data.get('farmer_phone')
        if not farmer_phone:
            return Response({'error': 'Farmer phone number is required'}, status=400)
            
        qr_data = generate_phonepe_qr(farmer_phone, amount)
        return Response({
            'payment_method': 'phonepe',
            'qr_data': qr_data
        })
    else:
        try:
            order_amount = int(float(amount) * 100)  # Convert to paise
            order_currency = 'INR'
            order_receipt = 'order_' + str(request.user.id)
            
            order = client.order.create({
                'amount': order_amount,
                'currency': order_currency,
                'receipt': order_receipt
            })
            
            return Response({
                'payment_method': 'razorpay',
                'order_id': order['id'],
                'amount': order_amount,
                'currency': order_currency
            })
        except Exception as e:
            return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def verify_payment(request):
    try:
        payment_id = request.data.get('razorpay_payment_id')
        order_id = request.data.get('razorpay_order_id')
        signature = request.data.get('razorpay_signature')
        
        client.utility.verify_payment_signature({
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        })
        
        return Response({'status': 'Payment verified successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)
