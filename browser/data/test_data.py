# Test data — simulation only, never use real financial data
# Banking: 9-digit routing, 4–17 digit account number
BANK_ROUTING = "021000021"   # 9 digits (ABA format)
BANK_ACCOUNT = "123456789"   # 9 digits (within 4–17 range)

# Payment: Luhn-valid card (Visa test number), future expiry, 3-digit CVC
CARD_NAME = "Test User"
CARD_NUMBER = "4111111111111111"   # Luhn-valid Visa test number
CARD_EXPIRY = "12/2027"              # Future expiry
CARD_CVC = "123"
