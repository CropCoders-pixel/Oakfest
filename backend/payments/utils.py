import qrcode
import base64
from io import BytesIO

def generate_phonepe_qr(phone_number, amount):
    upi_id = f"{phone_number}@ybl"
    upi_url = f"upi://pay?pa={upi_id}&pn=Farmer&am={amount}&cu=INR&tn=Purchase"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {
        'qr_code': img_str,
        'upi_url': upi_url
    }
