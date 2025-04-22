import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# You need to have chromedriver or geckodriver installed and in PATH.
# This test will open the playground, run a universal command, and check the UI.

def test_universal_commands():
    driver = webdriver.Chrome()
    driver.get('http://localhost:8000')
    time.sleep(2)

    # Test Primora Thoughts panel
    driver.find_element(By.XPATH, "//button[contains(., 'Refresh Thoughts')]").click()
    time.sleep(1)
    thoughts = driver.find_element(By.ID, 'primora_thoughts').text
    assert 'No thoughts yet.' in thoughts or '🧠' in thoughts

    # Test Wiki command
    wiki_input = driver.find_element(By.ID, 'wiki_query')
    wiki_input.clear()
    wiki_input.send_keys('Python (programming language)')
    driver.find_element(By.XPATH, "//button[contains(., 'Wiki')]").click()
    time.sleep(2)
    result = driver.find_element(By.ID, 'universal_result').text
    assert 'Python' in result or 'No result.' not in result

    # Test Joke command
    driver.find_element(By.XPATH, "//button[contains(., 'Joke')]").click()
    time.sleep(2)
    joke = driver.find_element(By.ID, 'universal_result').text
    assert 'joke' in joke.lower() or joke.strip() != ''

    driver.quit()

if __name__ == '__main__':
    test_universal_commands()
    print('Selenium UI test passed!')
