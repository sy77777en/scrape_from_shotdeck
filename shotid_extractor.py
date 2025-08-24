# import os
# import time
# import argparse
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
# from urllib.parse import quote
#
#
# class ShotDeckIDExtractor:
#     def __init__(self, username, password):
#         """Initialize the ShotDeck ID extractor with credentials."""
#         self.username = username
#         self.password = password
#         self.base_url = "https://shotdeck.com"
#         self.driver = None
#
#     def setup_driver(self):
#         """Set up and configure the Chrome WebDriver."""
#         chrome_options = Options()
#         # Uncomment the line below to run headless (no visible browser)
#         # chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--window-size=1920,1080")
#
#         # Initialize the WebDriver
#         self.driver = webdriver.Chrome(options=chrome_options)
#         self.driver.implicitly_wait(10)
#
#     def login(self):
#         """Log in to ShotDeck with the provided credentials."""
#         try:
#             # Navigate to login page
#             self.driver.get(f"{self.base_url}/welcome/login")
#
#             # Wait for the login form to load
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, "user"))
#             )
#
#             # Enter login credentials
#             self.driver.find_element(By.NAME, "user").send_keys(self.username)
#             self.driver.find_element(By.NAME, "pass").send_keys(self.password)
#
#             # Check "Keep me logged in" checkbox
#             stay_logged_in = self.driver.find_element(By.ID, "stayLoggedIn")
#             if not stay_logged_in.is_selected():
#                 stay_logged_in.click()
#
#             # Click the login button
#             self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
#
#             # Wait for login to complete and redirect
#             try:
#                 WebDriverWait(self.driver, 15).until(
#                     lambda driver: "welcome/home" in driver.current_url or
#                                    "browse/stills" in driver.current_url or
#                                    "dashboard" in driver.current_url
#                 )
#
#                 print(f"Successfully logged in! Current URL: {self.driver.current_url}")
#                 return True
#
#             except TimeoutException:
#                 print(f"Unexpected page after login. Current URL: {self.driver.current_url}")
#                 return False
#
#         except Exception as e:
#             print(f"Login failed: {e}")
#             return False
#
#     def search(self, query):
#         """Navigate to the search URL for the given query."""
#         # Handle comma-separated search terms
#         if ',' in query:
#             parts = [part.strip() for part in query.split(',')]
#             formatted_parts = []
#             for part in parts:
#                 formatted_parts.append(self._format_query_part(part))
#             formatted_query = '_'.join(formatted_parts)
#         else:
#             formatted_query = self._format_query_part(query)
#
#         print(f"Transforming query: '{query}' → '{formatted_query}'")
#
#         # Encode the search query for the URL
#         encoded_query = quote(formatted_query)
#         search_url = f"{self.base_url}/browse/stills#/s/{encoded_query}"
#
#         print(f"Navigating to search: {search_url}")
#         self.driver.get(search_url)
#
#         # Wait for page to load
#         time.sleep(5)
#
#         # Wait for search results to load
#         try:
#             WebDriverWait(self.driver, 30).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "outerimage"))
#             )
#             print("Search results loaded!")
#
#             # Count initial results
#             initial_images = self.driver.find_elements(By.CSS_SELECTOR, "div.outerimage")
#             print(f"Initial search returned {len(initial_images)} results.")
#
#             # Check if no results
#             if len(initial_images) == 0:
#                 no_results = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'No results')]")
#                 if no_results:
#                     print("WARNING: No search results found. Please check your search query.")
#                     return False
#             return True
#
#         except TimeoutException:
#             print("Warning: Search results took too long to load or no results found.")
#             return False
#
#     def _format_query_part(self, query_part):
#         """Format a single part of a query according to ShotDeck's requirements."""
#         # First, check if the query is already in ShotDeck format
#         if '"' in query_part or '_' in query_part:
#             return query_part
#
#         # Parse the natural language query
#         words = query_part.split()
#
#         if len(words) <= 1:
#             # Single word query, no special formatting needed
#             return query_part
#         else:
#             # Multi-word query - don't add quotes, just join with spaces
#             # ShotDeck will handle the spaces in the URL
#             return query_part
#
#     def scroll_and_load_all(self, max_scrolls=100, scroll_pause_time=1.5, no_change_limit=5, image_limit=None):
#         """Scroll down the page to trigger the loading of all images."""
#         last_height = self.driver.execute_script("return document.body.scrollHeight")
#         images_before = 0
#         scrolls = 0
#         no_change_count = 0
#
#         print("Scrolling to load all images...")
#
#         while scrolls < max_scrolls:
#             # Scroll down to bottom
#             self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#
#             # Wait for page to load new content
#             time.sleep(scroll_pause_time)
#
#             # Calculate new scroll height and compare with last scroll height
#             new_height = self.driver.execute_script("return document.body.scrollHeight")
#
#             # Count current images
#             images = self.driver.find_elements(By.CSS_SELECTOR, "div.outerimage")
#             print(f"Found {len(images)} images so far... (scroll {scrolls + 1}/{max_scrolls})")
#
#             # Check if we've reached the image limit
#             if image_limit and len(images) >= image_limit:
#                 print(f"Reached the image limit of {image_limit}. Stopping scrolling.")
#                 break
#
#             # Check if we've reached the end
#             if len(images) == images_before:
#                 no_change_count += 1
#                 print(f"No new images loaded. Consecutive count: {no_change_count}/{no_change_limit}")
#
#                 if no_change_count >= no_change_limit:
#                     print("No more images loading after multiple attempts, stopping scroll.")
#                     break
#             else:
#                 no_change_count = 0
#
#             # Also check if scroll height didn't change
#             if new_height == last_height:
#                 no_change_count += 1
#                 print(f"Page height didn't change. Consecutive count: {no_change_count}/{no_change_limit}")
#             else:
#                 last_height = new_height
#
#             # Try scroll jiggle to trigger more content
#             if no_change_count > 0 and no_change_count < no_change_limit:
#                 print("Trying scroll jiggle to trigger more content...")
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 400);")
#                 time.sleep(0.5)
#                 self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                 time.sleep(scroll_pause_time)
#
#             images_before = len(images)
#             scrolls += 1
#
#         print(f"Finished scrolling. Found {images_before} images in total.")
#
#     def extract_shot_ids(self, image_limit=None):
#         """Extract all SHOT_IDs from the loaded images."""
#         # Find all image elements
#         image_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.outerimage")
#
#         if not image_containers:
#             print("No images found.")
#             return []
#
#         # Apply limit if specified
#         if image_limit and len(image_containers) > image_limit:
#             print(f"Limiting extraction to {image_limit} images out of {len(image_containers)} found.")
#             image_containers = image_containers[:image_limit]
#         else:
#             print(f"Extracting SHOT_IDs from {len(image_containers)} images...")
#
#         shot_ids = []
#
#         for i, container in enumerate(image_containers):
#             try:
#                 # Get the shot ID from the container
#                 shot_id = container.get_attribute("data-shotid")
#                 if shot_id:
#                     shot_ids.append(shot_id)
#                     print(f"  {i + 1}: {shot_id}")
#                 else:
#                     print(f"  {i + 1}: No shot ID found")
#
#             except Exception as e:
#                 print(f"  Error processing image {i + 1}: {e}")
#
#         print(f"\nExtracted {len(shot_ids)} SHOT_IDs successfully!")
#         return shot_ids
#
#     def save_shot_ids(self, shot_ids, query, output_file=None):
#         """Save the SHOT_IDs to a file."""
#         if not output_file:
#             # Create filename based on query
#             sanitized_query = self._sanitize_for_filename(query)
#             output_file = f"shotdeck_ids_{sanitized_query}.txt"
#
#         try:
#             with open(output_file, 'w') as f:
#                 for shot_id in shot_ids:
#                     f.write(f"{shot_id}\n")
#             print(f"SHOT_IDs saved to: {output_file}")
#         except Exception as e:
#             print(f"Error saving SHOT_IDs to file: {e}")
#
#     def _sanitize_for_filename(self, name):
#         """Sanitize a string to be used as a filename."""
#         invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', ' ', ',']
#         for char in invalid_chars:
#             name = name.replace(char, '_')
#         return name.strip().strip('.')[:50]
#
#     def run(self, search_query, max_scrolls=100, image_limit=None, save_to_file=True):
#         """Run the full ID extraction process."""
#         try:
#             self.setup_driver()
#
#             # Step 1: Login to the site
#             print("Step 1: Logging in...")
#             login_success = self.login()
#             if not login_success:
#                 print("Login failed. Exiting.")
#                 return []
#
#             # Step 2: Navigate to search URL
#             print("Step 2: Navigating to search...")
#             time.sleep(2)
#             search_success = self.search(search_query)
#             if not search_success:
#                 print("Failed to load search results. Exiting.")
#                 return []
#
#             # Step 3: Scroll to load all images
#             print("Step 3: Scrolling to load images...")
#             if image_limit:
#                 print(f"Will stop scrolling after finding approximately {image_limit} images.")
#             self.scroll_and_load_all(max_scrolls=max_scrolls, image_limit=image_limit)
#
#             # Step 4: Extract SHOT_IDs
#             print("Step 4: Extracting SHOT_IDs...")
#             shot_ids = self.extract_shot_ids(image_limit=image_limit)
#
#             if not shot_ids:
#                 print("No SHOT_IDs found.")
#                 return []
#
#             # Step 5: Save to file if requested
#             if save_to_file:
#                 self.save_shot_ids(shot_ids, search_query)
#
#             print(f"ID extraction completed successfully! Found {len(shot_ids)} SHOT_IDs.")
#             return shot_ids
#
#         except Exception as e:
#             print(f"Error during extraction process: {e}")
#             return []
#
#         finally:
#             if self.driver:
#                 self.driver.quit()
#
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="ShotDeck SHOT_ID Extractor")
#     parser.add_argument("--username", "-u", required=True, help="ShotDeck account username/email")
#     parser.add_argument("--password", "-p", required=True, help="ShotDeck account password")
#     parser.add_argument("--query", "-q", required=True,
#                         help="Search query (e.g., 'brad pitt hands' or 'black and white, drink')")
#     parser.add_argument("--max-scrolls", "-m", type=int, default=100, help="Maximum number of scrolls to perform")
#     parser.add_argument("--limit", "-l", type=int, default=None, help="Maximum number of SHOT_IDs to extract")
#     parser.add_argument("--output", "-o", default=None, help="Output file for SHOT_IDs (optional)")
#     parser.add_argument("--no-save", action="store_true", help="Don't save SHOT_IDs to file, just print them")
#
#     args = parser.parse_args()
#
#     # Create extractor
#     extractor = ShotDeckIDExtractor(args.username, args.password)
#
#     # Run extraction
#     shot_ids = extractor.run(
#         args.query,
#         args.max_scrolls,
#         args.limit,
#         save_to_file=not args.no_save
#     )
#
#     # Print results
#     if shot_ids:
#         print(f"\nFound SHOT_IDs:")
#         for shot_id in shot_ids:
#             print(shot_id)


import os
import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import quote


class ShotDeckIDExtractor:
    def __init__(self, username, password):
        """Initialize the ShotDeck ID extractor with credentials."""
        self.username = username
        self.password = password
        self.base_url = "https://shotdeck.com"
        self.driver = None

    def setup_driver(self):
        """Set up and configure the Chrome WebDriver."""
        chrome_options = Options()
        # Uncomment the line below to run headless (no visible browser)
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")

        # Initialize the WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)

    def login(self):
        """Log in to ShotDeck with the provided credentials."""
        try:
            # Navigate to login page
            self.driver.get(f"{self.base_url}/welcome/login")

            # Wait for the login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "user"))
            )

            # Enter login credentials
            self.driver.find_element(By.NAME, "user").send_keys(self.username)
            self.driver.find_element(By.NAME, "pass").send_keys(self.password)

            # Check "Keep me logged in" checkbox
            stay_logged_in = self.driver.find_element(By.ID, "stayLoggedIn")
            if not stay_logged_in.is_selected():
                stay_logged_in.click()

            # Click the login button
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

            # Wait for login to complete and redirect
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: "welcome/home" in driver.current_url or
                                   "browse/stills" in driver.current_url or
                                   "dashboard" in driver.current_url
                )

                print(f"Successfully logged in! Current URL: {self.driver.current_url}")
                return True

            except TimeoutException:
                print(f"Unexpected page after login. Current URL: {self.driver.current_url}")
                return False

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def search(self, query):
        """Navigate to the search URL for the given query."""
        # Handle comma-separated search terms
        if ',' in query:
            parts = [part.strip() for part in query.split(',')]
            formatted_parts = []
            for part in parts:
                formatted_parts.append(self._format_query_part(part))
            formatted_query = '_'.join(formatted_parts)
        else:
            formatted_query = self._format_query_part(query)

        print(f"Transforming query: '{query}' → '{formatted_query}'")

        # Encode the search query for the URL
        encoded_query = quote(formatted_query)
        search_url = f"{self.base_url}/browse/stills#/s/{encoded_query}"

        print(f"Navigating to search: {search_url}")
        self.driver.get(search_url)

        # Wait for page to load
        time.sleep(5)

        # Wait for search results to load
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "outerimage"))
            )
            print("Search results loaded!")

            # Count initial results
            initial_images = self.driver.find_elements(By.CSS_SELECTOR, "div.outerimage")
            print(f"Initial search returned {len(initial_images)} results.")

            # Check if no results
            if len(initial_images) == 0:
                no_results = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'No results')]")
                if no_results:
                    print("WARNING: No search results found. Please check your search query.")
                    return False
            return True

        except TimeoutException:
            print("Warning: Search results took too long to load or no results found.")
            return False

    def _format_query_part(self, query_part):
        """Format a single part of a query according to ShotDeck's requirements."""
        # First, check if the query is already in ShotDeck format
        if '"' in query_part or '_' in query_part:
            return query_part

        # Parse the natural language query
        words = query_part.split()

        if len(words) <= 1:
            # Single word query, no special formatting needed
            return query_part
        else:
            # Multi-word query - don't add quotes, just join with spaces
            # ShotDeck will handle the spaces in the URL
            return query_part

    def scroll_and_load_all(self, max_scrolls=100, scroll_pause_time=1.5, no_change_limit=5, image_limit=None):
        """Scroll down the page to trigger the loading of all images."""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        images_before = 0
        scrolls = 0
        no_change_count = 0

        print("Scrolling to load all images...")

        while scrolls < max_scrolls:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for page to load new content
            time.sleep(scroll_pause_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # Count current images
            images = self.driver.find_elements(By.CSS_SELECTOR, "div.outerimage")
            print(f"Found {len(images)} images so far... (scroll {scrolls + 1}/{max_scrolls})")

            # Check if we've reached the image limit
            if image_limit and len(images) >= image_limit:
                print(f"Reached the image limit of {image_limit}. Stopping scrolling.")
                break

            # Check if we've reached the end
            if len(images) == images_before:
                no_change_count += 1
                print(f"No new images loaded. Consecutive count: {no_change_count}/{no_change_limit}")

                if no_change_count >= no_change_limit:
                    print("No more images loading after multiple attempts, stopping scroll.")
                    break
            else:
                no_change_count = 0

            # Also check if scroll height didn't change
            if new_height == last_height:
                no_change_count += 1
                print(f"Page height didn't change. Consecutive count: {no_change_count}/{no_change_limit}")
            else:
                last_height = new_height

            # Try scroll jiggle to trigger more content
            if no_change_count > 0 and no_change_count < no_change_limit:
                print("Trying scroll jiggle to trigger more content...")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 400);")
                time.sleep(0.5)
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)

            images_before = len(images)
            scrolls += 1

        print(f"Finished scrolling. Found {images_before} images in total.")

    def extract_shot_ids(self, image_limit=None):
        """Extract all SHOT_IDs from the loaded images."""
        # Find all image elements
        image_containers = self.driver.find_elements(By.CSS_SELECTOR, "div.outerimage")

        if not image_containers:
            print("No images found.")
            return []

        # Apply limit if specified
        if image_limit and len(image_containers) > image_limit:
            print(f"Limiting extraction to {image_limit} images out of {len(image_containers)} found.")
            image_containers = image_containers[:image_limit]
        else:
            print(f"Extracting SHOT_IDs from {len(image_containers)} images...")

        shot_ids = []

        for i, container in enumerate(image_containers):
            try:
                # Get the shot ID from the container
                shot_id = container.get_attribute("data-shotid")
                if shot_id:
                    shot_ids.append(shot_id)
                    print(f"  {i + 1}: {shot_id}")
                else:
                    print(f"  {i + 1}: No shot ID found")

            except Exception as e:
                print(f"  Error processing image {i + 1}: {e}")

        print(f"\nExtracted {len(shot_ids)} SHOT_IDs successfully!")
        return shot_ids

    def save_shot_ids(self, shot_ids, query, output_file=None):
        """Save the SHOT_IDs to a file."""
        if not output_file:
            # Create filename based on query
            sanitized_query = self._sanitize_for_filename(query)
            output_file = f"shotdeck_ids_{sanitized_query}.txt"

        try:
            with open(output_file, 'w') as f:
                for shot_id in shot_ids:
                    f.write(f"{shot_id}\n")
            print(f"SHOT_IDs saved to: {output_file}")
        except Exception as e:
            print(f"Error saving SHOT_IDs to file: {e}")

    def save_results_json(self, results_dict, file_path):
        """Save the results dictionary to a JSON file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results_dict, f, indent=2, ensure_ascii=False)
            print(f"Results saved to JSON: {file_path}")
            return True
        except Exception as e:
            print(f"Error saving JSON file: {e}")
            return False

    def _sanitize_for_filename(self, name):
        """Sanitize a string to be used as a filename."""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', ' ', ',']
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip().strip('.')[:50]

    def run_single_query(self, search_query, max_scrolls=100, image_limit=None):
        """Run extraction for a single query."""
        try:
            print(f"\n{'=' * 50}")
            print(f"Processing query: '{search_query}'")
            print(f"{'=' * 50}")

            # Step 1: Navigate to search URL
            search_success = self.search(search_query)
            if not search_success:
                print(f"Failed to load search results for query: '{search_query}'")
                return []

            # Step 2: Scroll to load images
            print("Scrolling to load images...")
            self.scroll_and_load_all(max_scrolls=max_scrolls, image_limit=image_limit)

            # Step 3: Extract SHOT_IDs
            print("Extracting SHOT_IDs...")
            shot_ids = self.extract_shot_ids(image_limit=image_limit)

            print(f"Completed query '{search_query}': Found {len(shot_ids)} SHOT_IDs")
            return shot_ids

        except Exception as e:
            print(f"Error processing query '{search_query}': {e}")
            return []

    def run_multiple_queries(self, keywords_list, total_image_limit=None, max_scrolls=100, output_path=None):
        """Run extraction for multiple keywords with a global image limit."""
        try:
            self.setup_driver()

            # Step 1: Login
            print("Step 1: Logging in...")
            login_success = self.login()
            if not login_success:
                print("Login failed. Exiting.")
                return {}

            time.sleep(2)

            results = {}
            total_images_collected = 0

            # Calculate per-query limit if total limit is specified
            if total_image_limit and len(keywords_list) > 0:
                per_query_limit = max(1, total_image_limit // len(keywords_list))
                print(f"Total image limit: {total_image_limit}")
                print(f"Per query limit: {per_query_limit}")
            else:
                per_query_limit = None
                print("No total image limit specified")

            # Process each keyword
            for i, keyword in enumerate(keywords_list, 1):
                print(f"\nProcessing keyword {i}/{len(keywords_list)}: '{keyword}'")

                # Check if we've reached the total limit
                if total_image_limit and total_images_collected >= total_image_limit:
                    print(f"Reached total image limit of {total_image_limit}. Stopping.")
                    break

                # Calculate remaining limit for this query
                if total_image_limit:
                    remaining_limit = total_image_limit - total_images_collected
                    current_query_limit = min(per_query_limit, remaining_limit) if per_query_limit else remaining_limit
                else:
                    current_query_limit = per_query_limit

                # Extract shot IDs for this keyword
                shot_ids = self.run_single_query(keyword, max_scrolls, current_query_limit)

                # Store results
                results[keyword] = {
                    'shot_ids': shot_ids,
                    'count': len(shot_ids)
                }

                total_images_collected += len(shot_ids)
                print(f"Total images collected so far: {total_images_collected}")

                # Small delay between queries
                if i < len(keywords_list):
                    time.sleep(3)

            # Add summary to results
            results['_summary'] = {
                'total_keywords_processed': len([k for k in results.keys() if k != '_summary']),
                'total_shot_ids_collected': total_images_collected,
                'image_limit_used': total_image_limit,
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }

            # Save to JSON if output path is provided
            if output_path:
                self.save_results_json(results, output_path)

            # Print summary
            print(f"\n{'=' * 60}")
            print("EXTRACTION SUMMARY")
            print(f"{'=' * 60}")
            for keyword, data in results.items():
                if keyword != '_summary':
                    print(f"'{keyword}': {data['count']} shot IDs")
            print(f"Total: {total_images_collected} shot IDs collected")
            print(f"{'=' * 60}")

            return results

        except Exception as e:
            print(f"Error during multi-query extraction: {e}")
            return {}

        finally:
            if self.driver:
                self.driver.quit()

    def run(self, search_query, max_scrolls=100, image_limit=None, save_to_file=True):
        """Run the full ID extraction process for a single query (backwards compatibility)."""
        try:
            self.setup_driver()

            # Step 1: Login to the site
            print("Step 1: Logging in...")
            login_success = self.login()
            if not login_success:
                print("Login failed. Exiting.")
                return []

            # Step 2: Navigate to search URL
            print("Step 2: Navigating to search...")
            time.sleep(2)
            search_success = self.search(search_query)
            if not search_success:
                print("Failed to load search results. Exiting.")
                return []

            # Step 3: Scroll to load all images
            print("Step 3: Scrolling to load images...")
            if image_limit:
                print(f"Will stop scrolling after finding approximately {image_limit} images.")
            self.scroll_and_load_all(max_scrolls=max_scrolls, image_limit=image_limit)

            # Step 4: Extract SHOT_IDs
            print("Step 4: Extracting SHOT_IDs...")
            shot_ids = self.extract_shot_ids(image_limit=image_limit)

            if not shot_ids:
                print("No SHOT_IDs found.")
                return []

            # Step 5: Save to file if requested
            if save_to_file:
                self.save_shot_ids(shot_ids, search_query)

            print(f"ID extraction completed successfully! Found {len(shot_ids)} SHOT_IDs.")
            return shot_ids

        except Exception as e:
            print(f"Error during extraction process: {e}")
            return []

        finally:
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShotDeck SHOT_ID Extractor")
    parser.add_argument("--username", "-u", required=True, help="ShotDeck account username/email")
    parser.add_argument("--password", "-p", required=True, help="ShotDeck account password")

    # Support both single query and multiple keywords
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", "-q", help="Single search query (e.g., 'brad pitt hands')")
    group.add_argument("--keywords", "-k", nargs='+',
                       help="List of keywords to search (e.g., 'sunset' 'ocean' 'mountains')")
    group.add_argument("--keywords-file", "-f", help="JSON file containing keywords")

    parser.add_argument("--max-scrolls", "-m", type=int, default=100, help="Maximum number of scrolls to perform")
    parser.add_argument("--limit", "-l", type=int, default=None,
                        help="Total maximum number of SHOT_IDs to extract (for all keywords)")
    parser.add_argument("--output", "-o", default=None,
                        help="Output file path for JSON results (required for multiple keywords)")
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save SHOT_IDs to file, just print them (single query only)")

    args = parser.parse_args()

    # Create extractor
    extractor = ShotDeckIDExtractor(args.username, args.password)

    # Handle different input modes
    if args.query:
        # Single query mode (backwards compatibility)
        shot_ids = extractor.run(
            args.query,
            args.max_scrolls,
            args.limit,
            save_to_file=not args.no_save
        )

        # Print results
        if shot_ids:
            print(f"\nFound SHOT_IDs:")
            for shot_id in shot_ids:
                print(shot_id)

    elif args.keywords:
        # Multiple keywords from command line
        if not args.output:
            print("Error: --output is required when using multiple keywords")
            exit(1)

        results = extractor.run_multiple_queries(
            args.keywords,
            args.limit,
            args.max_scrolls,
            args.output
        )

    elif args.keywords_file:
        # Multiple keywords from JSON file
        if not args.output:
            print("Error: --output is required when using keywords file")
            exit(1)

        try:
            with open(args.keywords_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Support different JSON structures
            if isinstance(data, list):
                # Simple array: ["keyword1", "keyword2", ...]
                keywords = data
            elif isinstance(data, dict) and 'keywords' in data:
                # Object with keywords array: {"keywords": ["keyword1", "keyword2", ...]}
                keywords = data['keywords']
            elif isinstance(data, dict):
                # Object with keys as keywords: {"keyword1": {}, "keyword2": {}, ...}
                keywords = list(data.keys())
            else:
                raise ValueError("Invalid JSON structure. Expected array of keywords or object with 'keywords' field.")

            # Filter out empty strings and ensure all are strings
            keywords = [str(k).strip() for k in keywords if str(k).strip()]

            if not keywords:
                print("Error: No valid keywords found in JSON file")
                exit(1)

            print(f"Loaded {len(keywords)} keywords from JSON file: {args.keywords_file}")
            print(f"Keywords: {keywords}")

            results = extractor.run_multiple_queries(
                keywords,
                args.limit,
                args.max_scrolls,
                args.output
            )

        except FileNotFoundError:
            print(f"Error: Keywords file not found: {args.keywords_file}")
            exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in keywords file: {e}")
            exit(1)
        except Exception as e:
            print(f"Error reading keywords file: {e}")
            exit(1)