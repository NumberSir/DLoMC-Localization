# """TODO: Work in Progress"""
#
#
# from loguru._logger import Logger
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.wait import WebDriverWait
#
# from src.config import settings
# from src.log import logger
#
#
# class SubscribeStar:
#     def __init__(self, driver: webdriver):
#         self._base_url = "https://subscribestar.adult"
#         self._driver = driver
#         self._wait = WebDriverWait(self.driver, 10)
#         self._logger = logger.bind(project_name="SubscribeStar")
#
#     def _pass_age_confirm(self):
#         age_confirm_input = self.wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//input[@class='warning_xodal-dob_input']"))
#         )
#         age_confirm_input.clear()
#         age_confirm_input.click()
#         self.driver.execute_script(
#             "arguments[0].setAttribute('class', 'warning_xodal-dob_input is-set')",
#             age_confirm_input
#         )
#         self.logger.debug("Age comfirm script executed.")
#
#         age_confirm_button = self.driver.find_element(By.XPATH, "//button[@class='flat_button for-warning-18']")
#         age_confirm_button.click()
#         self.logger.success("Age successfully confirmed.")
#
#     def login(self):
#         url = f"{self.base_url}/mildasento"
#         self.driver.get(url)
#         self._pass_age_confirm()
#
#         self.driver.refresh()
#         login_button = self.wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//div[@class='top_bar-login']"))
#         )
#         login_button.click()
#         self.logger.debug("Login button clicked.")
#
#         email_input = self.wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//input[@name='email']"))
#         )
#         email_input.clear()
#         email_input.send_keys(settings.subscribestar.email)
#         self.logger.debug("Email input was sent.")
#         email_submit_button = self.wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//button[@class='arrow_button for-login']"))
#         )
#         email_submit_button.click()
#         self.logger.debug("Email submit button clicked.")
#
#         password_input = self.wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//input[@name='password']"))
#         )
#         password_input.clear()
#         password_input.send_keys(settings.subscribestar.password)
#         self.logger.debug("Password input was sent.")
#         login_submit_button = self.wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//button[@class='arrow_button for-login']"))
#         )
#         login_submit_button.click()
#         self.logger.debug("Password submit button clicked.")
#         self.driver.refresh()
#         self.logger.success(f"Logged in successfully as {settings.subscribestar.email}")
#
#     def get_pinned_post_url(self) -> str:
#         """pinned post contains published post url"""
#         url = f"{self.base_url}/mildasento"
#         self.driver.get(url)
#         pinned_post_id = self.wait.until(
#             EC.visibility_of_element_located((By.XPATH, "//div[@class='post-pin']/.."))
#         ).get_attribute("data-id")
#         self.logger.success(f"Pinned post id: {pinned_post_id}")
#         return f"{self.base_url}/posts/{pinned_post_id}"
#
#     def get_published_post_url(self, pinned_post_url: str) -> str:
#         """published post contains download link"""
#         self.driver.get(pinned_post_url)
#         public_post_url = self.wait.until(
#             EC.visibility_of_element_located(
#                 (By.XPATH, "//a[contains(@href, 'subscribestar') and contains(text(), '(PC)')]")
#             )
#         ).get_attribute("href")
#         self.logger.success(f"Public post url: {public_post_url}")
#         return public_post_url
#
#     def get_download_link(self, published_post_url: str) -> str:
#         """mega download link"""
#         self.driver.get(published_post_url)
#         download_link = self.wait.until(
#             EC.visibility_of_element_located(
#                 (By.XPATH, "//a[contains(text(), '(PC)') and contains(text(), 'Daily Lives of My Countryside')]")
#             )
#         ).get_attribute("data-href")
#         self.logger.success(f"Download link: {download_link}")
#         return download_link
#
#     def download(self, download_link: str):
#         self.driver.get(download_link)
#         download_button = self.wait.until(
#             EC.visibility_of_element_located(
#                 (By.XPATH, "//div[@class='mega-button positive js-default-download js-standard-download']")
#             )
#         )
#         download_button.click()
#         self.logger.debug("Download button clicked.")
#
#     @property
#     def base_url(self) -> str:
#         return self._base_url
#
#     @property
#     def driver(self) -> webdriver:
#         return self._driver
#
#     @property
#     def wait(self) -> WebDriverWait:
#         return self._wait
#
#     @property
#     def logger(self) -> Logger:
#         return self._logger
#
#
# __all__ = [
#     "SubscribeStar",
# ]
#
#
# if __name__ == '__main__':
#     options = webdriver.EdgeOptions()
#     options.add_experimental_option("detach", True)
#     options.add_experimental_option("prefs", {
#         "download.default_directory": (settings.filepath.root / settings.filepath.tmp).__str__()
#     })
#     driver = webdriver.Edge(options=options)
#     star = SubscribeStar(driver=driver)
#     star.login()
#     pinned_post_url = star.get_pinned_post_url()
#     public_post_url = star.get_published_post_url(pinned_post_url)
#     download_link = star.get_download_link(public_post_url)
