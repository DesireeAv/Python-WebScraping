from dotenv import load_dotenv
import os

from api.client import APIClient, APIError

BASE_URL = (
    "https://zvyhufnwclhcvmgtqxwp.supabase.co/functions/v1/api-v1"
)


def main():
    load_dotenv()

    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    client = APIClient(BASE_URL)

    try:
        print("Authenticating...")

        mfa_token = client.login(email, password)
        print("✓ MFA token received")

        client.verify_mfa(mfa_token, "1234")
        print("✓ Access token received")

        banking = client.update_banking(
            routing_number="021000021",
            account_number="1234567890",
        )

        print("\nBanking updated:")
        print(
            f"Routing: {banking['routing_masked']}"
        )
        print(
            f"Account: {banking['account_masked']}"
        )

        payment = client.update_payment(
            cardholder_name="Candidate Test",
            card_number="4242424242424242",
            exp_month=12,
            exp_year=2027,
            cvc="123",
        )

        print("\nPayment updated:")
        print(
            f"Brand: {payment['card_brand']}"
        )
        print(
            f"Last4: {payment['last4']}"
        )
        print(
            f"Expiry: {payment['exp_month']}/{payment['exp_year']}"
        )

        print("\n✓ Challenge completed successfully")

    except APIError as exc:
        print(f"\nERROR [{exc.status_code}]")
        print(exc.message)

        if exc.details:
            print(exc.details)



if __name__ == "__main__":
    main()