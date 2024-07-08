import serial
import time
from .models import SMSLog

def send_notification(phone_number, message):
    """
    Sends an SMS notification to the specified phone number with the given message.
    """
    try:
        ser = serial.Serial('COM3', 9600, timeout=1)
        time.sleep(2)
        ser.write(b'AT\r')
        time.sleep(1)
        ser.write(b'AT+CMGF=1\r')
        time.sleep(1)
        ser.write(b'AT+CMGS="' + phone_number.encode() + b'"\r')
        time.sleep(1)
        ser.write(message.encode() + chr(26).encode())
        time.sleep(3)
        ser.close()

        # Log the successful message in the database with status success
        SMSLog.objects.create(phone_number=phone_number, message=message, status='success')
        return True, 'SMS sent successfully'

    except serial.SerialException as se:
        error_message = f"Serial port error: {se}"
        SMSLog.objects.create(phone_number=phone_number, message=message, status='failed')
        return False, error_message

    except Exception as e:
        error_message = str(e)
        SMSLog.objects.create(phone_number=phone_number, message=message, status='failed')
        return False, error_message
