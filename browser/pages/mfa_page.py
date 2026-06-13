class MFAPage:
    def __init__(self, page):
        self.page = page

    def verify(self, code: str = "1234") -> None:
        self.page.fill("input[data-input-otp='true']", code)
        self.page.wait_for_timeout(1000)

        self.page.click("button[type='submit']")

        self.page.wait_for_timeout(3000)

        print("Current URL:", self.page.url)
