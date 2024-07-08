from django.shortcuts import render, redirect
from .models import SMSLog
from .forms import ComposeSMSForm
import serial
import time

def compose_sms(request):
    if request.method == 'POST':
        form = ComposeSMSForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            message = form.cleaned_data['message']
            print(f"Phone Number: {phone_number}")
            print(f"Message: {message}")
            try:
                # Attempt to send the SMS
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

                return redirect('sms:view_sms')

            except serial.SerialException as se:
                error_message = f"Serial port error: {se}"
                # Log the error message in the database with status failed
                SMSLog.objects.create(phone_number=phone_number, message=message, status='failed')
                return render(request, 'compose_sms.html', {'form': form, 'error_message': error_message})

            except Exception as e:
                error_message = str(e)
                # Log the error message in the database with status failed
                SMSLog.objects.create(phone_number=phone_number, message=message, status='failed')
                return render(request, 'compose_sms.html', {'form': form, 'error_message': error_message})
    else:
        form = ComposeSMSForm()
    return render(request, 'compose_sms.html', {'form': form})


def view_sms(request):
    sms_logs = SMSLog.objects.all().order_by('-created_at')
    for log in sms_logs:
        print(log.phone_number, log.message, log.status, log.created_at)
    return render(request, 'view_sms.html', {'sms_logs': sms_logs})
