import uuid
import base64

def generate_unique_loan_ref_id():
    # Generate UUID and encode it to base64
    unique_id = uuid.uuid4().hex[:10]
   # encoded_id = base64.b64encode(unique_id).decode('utf-8')

    # Remove non-alphanumeric characters and truncate to desired length
    #clean_id = ''.join(char for char in encoded_id if char.isalnum())[:15]

    return unique_id

