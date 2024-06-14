from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd

# Set up the Chrome driver
chrome_options = Options()
# Comment out the headless option to see the browser window
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

# Open the webpage
driver.get("https://www.sciencedirect.com/journal/aace-clinical-case-reports/issues")

# Function to click an element using WebDriverWait
def click_element(driver, element):
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(element)
    )
    driver.execute_script("arguments[0].scrollIntoView();", element)
    element.click()

try:
    # Locate the accordion panels
    accordion_panels = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".accordion-panel"))
    )
    print(f"Found {len(accordion_panels)} accordion panels.")
    all_hrefs = []
    for index, panel in enumerate(accordion_panels):
        print(f"Processing panel {index + 1}")
        # Find the button inside each panel and check its aria-expanded attribute
        button = panel.find_element(By.TAG_NAME, "button")
        aria_expanded = button.get_attribute('aria-expanded')
        print(f"Button aria-expanded attribute is: {aria_expanded}")
        if aria_expanded == "false":
            print(f"Clicking button with ID: {button.get_attribute('id')}")
            try:
                # Try clicking the button using normal click
                click_element(driver, (By.TAG_NAME, "button"))
            except:
                print("Normal click didn't work, trying JavaScript click")
                # If normal click doesn't work, use JavaScript click
                driver.execute_script("arguments[0].click();", button)

        # Give some time for the content to load after clicking the button
        WebDriverWait(driver, 2).until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'issue-item')]"))
        )

        # Locate the div elements with class issue-item using XPath
        issue_items = panel.find_elements(By.XPATH, "//*[contains(@class, 'issue-item')]")

        for item in issue_items:
            # Create the folder

            href = item.get_attribute('href')
            print(item.text)  # Print the text content of each issue item
            if href is not None:
                all_hrefs.append(href)

            # Optionally, navigate to each href collected
    for href in all_hrefs:
        print(f"Navigating to: {href}")

        # Split the URL by the '/' delimiter
        parts = href.split('/')

        # Assign specific parts to variables
        protocol = parts[0]  # 'https:'
        empty_string = parts[1]  # ''
        domain = parts[2]  # 'www.sciencedirect.com'
        journal = parts[3]  # 'journal'
        journal_name = parts[4]  # 'aace-clinical-case-reports'
        volume = parts[5]  # 'vol'
        volume_number = parts[6]  # '6'
        issue = parts[7]  # 'issue'
        issue_number = parts[8]  # '4'

        # Print the assigned parts
        print(f"Protocol: {protocol}")
        print(f"Empty String: {empty_string}")
        print(f"Domain: {domain}")
        print(f"Journal: {journal}")
        print(f"Journal Name: {journal_name}")
        print(f"Volume: {volume}")
        print(f"Volume Number: {volume_number}")
        print(f"Issue: {issue}")
        print(f"Issue Number: {issue_number}")

        base_folder_path = "D:/python/"
        folder_path = f"{base_folder_path}{volume}-{volume_number}"
        try:
            os.makedirs(folder_path, exist_ok=True)
            print(f'Folder created at: {folder_path}')
        except Exception as e:
            print(f'Error creating folder at: {folder_path}, Error: {e}')
        driver.get(href)
        try:
            # Use the corrected XPath expression to find the elements

            Page2sections = driver.find_elements(By.XPATH,
                                                 "//li[contains(@class, 'js-article-list-item') and contains(@class, "
                                                 "'article-item') and contains(@class, 'u-padding-xs-top') and "
                                                 "contains(@class, 'u-margin-l-bottom')]")
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@class, 'js-article-list-item') and contains(@class, "
                                                 "'article-item') and contains(@class, 'u-padding-xs-top') and "
                                                 "contains(@class, 'u-margin-l-bottom')]"))
            )
            print(f"Found {len(Page2sections)} article items.")

            jurnalname = []
            jurnalauthor = []

            for Page2section in Page2sections:
                # Use relative XPath expressions
                name_element = Page2section.find_element(By.XPATH, ".//dl/dt/h3")
                author_element = Page2section.find_element(By.XPATH, ".//dl/dd")

                name_text = name_element.text if name_element else 'N/A'
                author_text = author_element.text if author_element else 'N/A'

                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, ".//dl/dt/h3"))
                )

                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, ".//dl/dd"))
                )

                jurnalname.append(name_text)
                jurnalauthor.append(author_text)

            df = pd.DataFrame({'JurnalName': jurnalname, 'JurnalAuthor': jurnalauthor})

            df['JurnalList'] = df['JurnalName'] + " - " + df['JurnalAuthor']

            df = df[['JurnalList']]
            # Save the DataFrame to a CSV file
            file_path = os.path.join(folder_path, f'{issue}-{issue_number}.csv')
            df.to_csv(file_path, index=False)
            print(f'File saved at: {file_path}')

        except:
            pass

        # Add your logic here to interact with the page if needed
        # Optionally, wait for elements to load if necessary

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the driver
    driver.quit()


