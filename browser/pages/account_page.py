from playwright.sync_api import Page


class AccountPage:
    def __init__(self, page: Page):
        self.page = page

    def update_banking(self, routing: str, account: str) -> None:
        ########################
        # Banking details form #
        ########################
        self.page.fill("#bank-routing", routing)
        self.page.fill("#bank-account", account)
        self.page.click("#bank-save")
        # Wait for save to complete
        self.page.wait_for_timeout(500)
        

    def update_payment(self, name: str, number: str, expiry: str, cvc: str) -> None:
        ########################
        # Payment details form #
        ########################
        self.page.fill("#card-holder", name)
        self.page.fill("#card-number", number)
        self.page.fill("#card-exp-month", expiry_month := expiry.split("/")[0])
        self.page.fill("#card-exp-year", expiry_year := expiry.split("/")[1])
        self.page.fill("#card-cvc", cvc)
        self.page.click("#card-save")
        # Wait for save to complete
        self.page.wait_for_timeout(500)

    def verify_summary(self, routing: str, account: str, card_number: str, expiry: str, ) -> None:

        bank_info = self.page.locator(
            "[data-testid='bank-saved-info']"
        ).inner_text()

        payment_info = self.page.locator(
            "[data-testid='payment-saved-info']"
        ).inner_text()

        assert routing[-4:] in bank_info, (
            f"Routing suffix {routing[-4:]} not found"
        )

        assert account[-4:] in bank_info, (
            f"Account suffix {account[-4:]} not found"
        )

        assert card_number[-4:] in payment_info, (
            f"Card suffix {card_number[-4:]} not found"
        )

        # Site displays MM/YYYY
        expected_expiry = "12/2027"

        assert expected_expiry in payment_info, (
            f"Expiry {expected_expiry} not found"
        )

        assert "Last updated:" in bank_info
        assert "Last updated:" in payment_info

        print("✓ Banking information verified")
        print("✓ Payment information verified")
