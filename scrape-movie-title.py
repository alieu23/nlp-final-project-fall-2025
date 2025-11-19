from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def scrape_top_1000_with_selenium():
    """Scrape IMDb Top 1000 using Selenium to handle dynamic content"""

    print("=" * 60)
    print("IMDb Top 1000 Scraper with Selenium")
    print("=" * 60)
    print()

    # Setup Chrome options
    options = webdriver.ChromeOptions()
    # Uncomment the line below to run in headless mode (no browser window)
    # options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    print("Starting Chrome browser...")
    #driver = webdriver.Chrome(options=options)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Navigate to IMDb Top 1000
        url = "https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc"
        print(f"Loading: {url}")
        driver.get(url)

        # Wait for initial content to load
        print("Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.ipc-title__text"))
        )

        movies = set()
        load_more_clicks = 0
        max_clicks = 40  # 25 movies per page, 40 clicks should get 1000+

        print("\nStarting to collect movies...")
        print("-" * 60)

        while load_more_clicks < max_clicks:
            # Extract current movie titles
            title_elements = driver.find_elements(By.CSS_SELECTOR, "h3.ipc-title__text")

            for elem in title_elements:
                try:
                    text = elem.text.strip()
                    # Format is usually "1. Movie Title"
                    if text and ". " in text and text.split(".")[0].isdigit():
                        title = text.split(". ", 1)[1]
                        movies.add(title)
                except:
                    continue

            print(f"Collected: {len(movies)} unique movies (after {load_more_clicks} clicks)")

            # Try to find and click the "50 more" button
            try:
                # Scroll to bottom to make button visible
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

                # Look for the load more button
                load_more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ipc-see-more__button"))
                )

                # Click the button
                driver.execute_script("arguments[0].click();", load_more_button)
                load_more_clicks += 1

                # Wait for new content to load
                time.sleep(2)

            except TimeoutException:
                print("\n✓ No more 'Load More' button found - reached the end!")
                break
            except NoSuchElementException:
                print("\n✓ Finished loading all available movies!")
                break
            except Exception as e:
                print(f"\n⚠ Error clicking button: {e}")
                break

        # Final collection of any remaining titles
        title_elements = driver.find_elements(By.CSS_SELECTOR, "h3.ipc-title__text")
        for elem in title_elements:
            try:
                text = elem.text.strip()
                if text and ". " in text and text.split(".")[0].isdigit():
                    title = text.split(". ", 1)[1]
                    movies.add(title)
            except:
                continue

        print("\n" + "=" * 60)
        print(f"COMPLETED: Collected {len(movies)} unique movies")
        print("=" * 60)

        return sorted(movies)

    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        return []

    finally:
        print("\nClosing browser...")
        driver.quit()


def save_to_file(movies, filename="imdb_top_movies.txt"):
    """Save movies to a text file"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for i, movie in enumerate(movies, 1):
                f.write(f"{i}. {movie}\n")
        print(f"\n✓ Saved to {filename}")
    except Exception as e:
        print(f"\n✗ Error saving file: {e}")


def main():
    # Scrape the movies
    movies = scrape_top_1000_with_selenium()

    if movies:
        print("\n" + "=" * 60)
        print("Movie List:")
        print("-" * 60)
        for i, movie in enumerate(movies, 1):
            print(f"{i:4d}. {movie}")

        # Ask if user wants to save to file
        print("\n" + "=" * 60)
        save_to_file(movies)
    else:
        print("\n✗ No movies were collected")
        print("\nTroubleshooting:")
        print("  1. Make sure ChromeDriver is installed and in PATH")
        print("  2. Check your Chrome browser version matches ChromeDriver")
        print("  3. Try disabling headless mode to see what's happening")
        print("  4. Check your internet connection")


if __name__ == "__main__":
    main()