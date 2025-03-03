import random
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import clipboard

username = "USERNAME"
password = "Iam@PASSWORD"

client = OpenAI(api_key="API_KEY", base_url="https://api.deepseek.com")
def login(driver):
    inputs = driver.find_elements(By.CLASS_NAME, "input__2o8B ")
    inputs[0].send_keys(username)
    inputs[1].send_keys(password)

    loginButton = driver.find_element(By.CLASS_NAME, "btn__3Y3g fancy-btn__2prB primary__lqsj light__3AfA btn__1z2C btn-md__M51O ")
    loginButton.click()


def type_code_line_by_line(driver, code):
    editor = driver.find_element(By.CLASS_NAME, "view-lines.monaco-mouse-cursor-text")
    editor.click()

    actions = ActionChains(driver)
    actions.key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).perform()
    actions.send_keys(Keys.DELETE).perform()

    lines = code.split('\n')
    current_indent = 0

    for line in lines:
        if line.strip() == "":
            continue
        # Calculate the desired indentation for this line
        desired_indent = len(line) - len(line.lstrip())

        # If Monaco added more indent than needed, backspace to adjust
        if desired_indent < current_indent:
            backspaces_needed = int((current_indent - desired_indent) / 4)
            for _ in range(backspaces_needed):
                actions.send_keys(Keys.BACK_SPACE)

        # Type the actual code line without leading spaces
        actions.send_keys(line.lstrip())
        actions.perform()

        actions.send_keys(Keys.ENTER)
        actions.perform()

        # Update the current indent level based on the next line's indentation
        current_indent = desired_indent

def get_links(file_path):
    with open(file_path, 'r') as file:
        links = file.readlines()

    cleaned_links = [line.split('. ')[-1].strip() for line in links]
    return cleaned_links


def save_links_to_file(links, file_name):
    with open(file_name, "a") as file:
        for link in links:
            file.write(link + "\n")


def generateCode(problem, layout, testing=False):
    if testing:
        return """class Solution:
    def findAllConcatenatedWordsInADict(self, words):
        def canForm(word):
            if word in memo:
                return memo[word]
            for i in range(1, len(word)):
                prefix = word[:i]
                suffix = word[i:]
                if prefix in wordSet and (suffix in wordSet or canForm(suffix)):
                    memo[word] = True
                    return True
            memo[word] = False
            return False

        wordSet = set(words)
        memo = {}
        result = []

        for word in words:
            if canForm(word):
                result.append(word)

        return result"""

    with open('prompt.txt', 'r') as file:
        prompt_template = file.read()
    final_prompt = prompt_template.replace("<PROBLEM>", problem).replace("<LAYOUT>", layout)
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {"role": "system", "content": "You are an expert Python developer."},
            {"role": "user", "content": final_prompt}
        ],
        stream=False
    )
    generated_code = response.choices[0].message.content.strip()
    if generated_code.startswith("```"):
        generated_code = generated_code.split("\n", 1)[-1].rsplit("```")[0]
    return generated_code.strip()


# Initialize the WebDriver
driver = webdriver.Chrome()
# Get the links from the file
links = get_links('problem_links.txt')
howMuch = 40
errorLinks = []
failed_links = []
processed_links = []
firstTime = True
# Iterate over each link
for link in links:
    try:
        driver.get(link)
        print(f"Navigating to: {link}")
        if firstTime:
            input("Enter after login.....")
        sleep(howMuch)
        new_element = driver.find_element(By.XPATH,
                                          "/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[4]/div/div[1]/div[3]")
        extracted_text = new_element.text

        code_editor_div = driver.find_element(By.CLASS_NAME, "view-lines.monaco-mouse-cursor-text")
        code_editor_div.click()

        actions = ActionChains(driver)
        actions.key_down(Keys.COMMAND).send_keys('a').send_keys('c').key_up(Keys.COMMAND).perform()

        copied_text = clipboard.paste()
        python_code = generateCode(extracted_text, copied_text, False)
        print(f"Code generated: \n{python_code}")

        type_code_line_by_line(driver, python_code)
        sleep(random.randint(5, 10))

        submit_button = driver.find_element(By.XPATH,
                                            "/html/body/div[1]/div[2]/div/div/div[3]/div/div/div[1]/div/div/div[2]/div/div[2]/div/div[3]/div[3]")
        submit_button.click()

        sleep(random.randint(7, 20))

        # Check if the submission result is "Accepted"
        try:
            accepted_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, """/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[11]/div/div/div/div[2]/div/div[1]/div[1]/div[1]/span"""))
            )
            if accepted_element.text == "Accepted":
                print(f"Solution Accepted for {link}")
            else:
                print(f"Solution Not Accepted for {link}")
                print("Adding to Failure List")
                failed_links.append(link)
        except Exception as e:
            print(f"Solution Not Accepted for {link}: {str(e)}")
            print("Adding to Failure List")
            failed_links.append(link)

        processed_links.append(link)
        howMuch = random.randint(7, 20)
        firstTime = False

        if len(processed_links) % 5 == 0:
            save_links_to_file(failed_links, 'failed_links.txt')
            failed_links = []

    except Exception as e:
        print(f"Error occurred while processing {link}: {str(e)}\n")
        failed_links.append(link)
        continue

# Final save
save_links_to_file(failed_links, 'failed_links.txt')

# Close the browser
driver.quit()