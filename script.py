from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
import sys

chrome_options = Options()
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
driver.implicitly_wait(10)

def run():
  load_dotenv()
  release_name = sys.argv[1]
  file_path = sys.argv[2]
  
  url = os.getenv('URL')
  login = os.getenv('LOGIN')
  password = os.getenv('PASSWORD')

  driver.get(url)

  login_input = driver.find_element(By.XPATH, "//input[@type='email']")
  login_input.send_keys(login)

  password_input = driver.find_element(By.XPATH, "//input[@type='password']")
  password_input.send_keys(password + Keys.ENTER)

  welcome_popup = driver.find_elements(By.XPATH, "//button[contains(@class,'plus-welcome-modal__close')]")
  if len(welcome_popup) > 0:
    welcome_popup[0].click()

  add_release_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Добавить выпуск')]")
  add_release_button.click()

  file_input = driver.find_element(By.XPATH, "//input[@type='file' and @id='episodeFile']")
  file_input.send_keys(file_path)

  load_file_button = driver.find_element(By.XPATH, "//button[contains(@class, 'upload-episode-popup__upload-button')]")
  load_file_button.click()

  release_name_input = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'Заголовок выпуска')]")
  release_name_input.send_keys(release_name)


  wait = WebDriverWait(driver, 60)
  wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'episode-uploade-notify')]/span[contains(text(),'Загружено')]")))
  
  release_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Опубликовать')]/..")
  driver.execute_script("arguments[0].click();", release_button)

if __name__ == "__main__":
  run()
  driver.quit()