import re
def generate_secure_client_key(full_name, phone_last_4):
    clean_name = re.sub(r'[^a-z0-9]', '', full_name.lower().strip())
    clean_phone = re.sub(r'\D', '', str(phone_last_4))[-4:]
    return f"{clean_name}_{clean_phone}_2026"