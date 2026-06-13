class LoginPage:
    def __init__(self, page):
        self.page = page

    def login(self, email: str, password: str) -> None:
        self.page.fill("#email", email)
        self.page.fill("#password", password)
        self.page.click("button[type='submit']")

        self.page.wait_for_timeout(1000)

        print("Current URL:", self.page.url)
