from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def main() -> None:
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    try:
        driver.get("https://example.com")
        print(driver.title)
        input("Press Enter to quit...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
