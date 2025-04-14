import os
import json
import textwrap
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageDraw, ImageFont

def get_calendar(calendar_url, destination):
    # Configuration
    ASPECT_RATIO = (4, 6)  # Width:Height ratio of 4:6
    IMAGE_WIDTH = 800  # Base width in pixels
    IMAGE_HEIGHT = int(IMAGE_WIDTH * ASPECT_RATIO[1] / ASPECT_RATIO[0])  # Height calculated from aspect ratio

    # Selenium setup to scrape events
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Comment out for debug
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(calendar_url)

    # Wait for events to load
    driver.implicitly_wait(5)

    try:
        # Wait a short time for the dialog to appear (adjust timeout as needed)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "env-modal-dialog__dialog"))
        )
        
        # Dialog is present, find and click the "Accept necessary cookies" button
        try:
            # First try to find by exact button text
            accept_button = driver.find_element(By.XPATH, 
                "//button[contains(text(), 'Accept necessary cookies')]")
            accept_button.click()
            print("Clicked 'Accept necessary cookies' button")
        except NoSuchElementException:
            # If not found, try alternative selectors that might work
            try:
                # Try finding by partial text match
                accept_button = driver.find_element(By.XPATH, 
                    "//button[contains(text(), 'Accept necessary')]")
                accept_button.click()
                print("Clicked button with partial 'Accept necessary' text")
            except NoSuchElementException:
                # As a last resort, try to find any button in the dialog
                dialog = driver.find_element(By.CLASS_NAME, "env-modal-dialog__dialog")
                buttons = dialog.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if "necessary" in button.text.lower():
                        button.click()
                        print(f"Clicked cookie button with text: {button.text}")
                        break
                
        # Wait for the dialog to disappear
        WebDriverWait(driver, 5).until_not(
            EC.presence_of_element_located((By.CLASS_NAME, "env-modal-dialog__dialog"))
        )
        
    except:
        # No dialog found or it didn't appear in time, continue with scraping
        print("No cookie consent dialog detected")

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    events = []

    # Collect event data
    for item in soup.select(".hh-calendar-content"):
        date_day = item.select_one(".hh-calendar-date-day").text.strip()
        date_month = item.select_one(".hh-calendar-date-month").text.strip()
        title = item.select_one(".hh-calendar-heading").text.strip()
        desc = item.select_one(".hh-calendar-text").text.strip()

        # Parsing date as datetime object
        event_date = f"{date_day.upper()} {date_month}".upper()
        
        # Build the event dictionary
        events.append({
            "title": title,
            "date": event_date,
            "description": desc
        })

    driver.quit()

    def create_calendar_image(events, output_path="downloads/calendar.png"):
        """Create a calendar image with event listings in portrait orientation with 4:6 aspect ratio"""
        
        # Create base image with light blue background (matching the image)
        img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), color='#E3EDF5')
        draw = ImageDraw.Draw(img)
        fname = ""
        
        # Try to load fonts - use default if specific fonts not available
        try:
            fname = "Helvetica-Bold"
            title_font = ImageFont.truetype(fname, 30) 
            event_title_font = ImageFont.truetype(fname, 20)
            date_font = ImageFont.truetype(fname, 22)
            desc_font = ImageFont.truetype(fname.replace("-Bold", ""), 14)
        except IOError:
            try:
                fname = "Arial Bold"
                title_font = ImageFont.truetype(fname, 30)
                event_title_font = ImageFont.truetype(fname, 20)
                date_font = ImageFont.truetype(fname, 22)
                desc_font = ImageFont.truetype(fname.replace(" Bold", ""), 14)
            except IOError:
                # Fallback to default font
                title_font = ImageFont.load_default()
                event_title_font = ImageFont.load_default()
                date_font = ImageFont.load_default()
                time_font = ImageFont.load_default()
                desc_font = ImageFont.load_default()
                fname = ImageFont.load_default()
        
        # Draw title with proper positioning
        calendar_w = draw.textlength("CALENDAR", font=title_font)
        draw.text(((IMAGE_WIDTH - calendar_w) // 2, 30), "CALENDAR", fill="#000814", font=title_font)
        
        # Calculate spacing for events - adjust based on number of events
        start_y = 80
        event_height = 140  # Base height for each event
        event_spacing = 20  # Space between events
        
        # Draw each event (maximum 8)
        for i, event in enumerate(events[:8]):
            y_pos = start_y + i * (event_height + event_spacing)
            
            # Create a rounded rectangle for the entire event card
            card_width = IMAGE_WIDTH - 80  # 40px margin on each side
            card_height = event_height
            card_radius = 20  # Rounded corner radius
            
            # Draw white rounded rectangle for the card
            draw_rounded_rectangle(draw, (40, y_pos, 40 + card_width, y_pos + card_height), 
                                  radius=card_radius, fill='#FFFFFF')
            
            date_text = event['date']
            
            # Create colored date/time box on the left
            box_width = 150
            box_height = card_height
            box_colors = ['#A8D0E6', '#D8B7DD']
            box_color = box_colors[i % len(box_colors)]
            
            # Draw rounded rectangle for date box (only rounded on left side)
            draw_rounded_rectangle(draw, 
                                  (40, y_pos, 40 + box_width, y_pos + box_height),
                                  radius=card_radius, fill=box_color, 
                                  corners=(True, False, True, False))  # Only round left corners
            
            # Draw date text centered in the box
            # date_w = draw.textlength(date_text, font=date_font)
            # date_h = draw.textheight(date_text, font=date_font)
            text_bbox = draw.textbbox((0, 0), date_text, font=date_font)
            date_w = text_bbox[2] - text_bbox[0]  # Width of the text
            date_h = text_bbox[3] - text_bbox[1]  # Height of the text
            date_x = 40 + (box_width - date_w) // 2
            draw.text((date_x, y_pos - 3 + (box_height-date_h)//2), date_text, fill="#2D3748", font=date_font)
            
            # Event details section - to the right of the date/time box
            details_x = 40 + box_width + 20  # Start of event details
            details_width = card_width - box_width - 40  # Width available for details
            
            # Draw event title
            if 'title' in event and event['title']:
                title_y = y_pos + 20
                max_width = details_width
                wrapped_text = textwrap.fill(event['title'], width=max_width // 10)  # Approximate width
                lines = wrapped_text.split('\n')[:2]
                wrapped_text = '\n'.join(lines)
                draw.text((details_x, title_y), wrapped_text, fill="#1A202C", font=event_title_font)
            
            # Draw event description with text wrapping
            if 'description' in event and event['description']:
                desc_y = y_pos + 55 + (wrapped_text.count("\n")*25)
                
                # Wrap text to fit in the available space
                max_width = details_width
                wrapped_text = textwrap.fill(event['description'], width=max_width // 7)  # Approximate width
                
                # Limit to just 2 lines to save space
                lines = wrapped_text.split('\n')[:2]
                wrapped_text = '\n'.join(lines)
                
                draw.text((details_x, desc_y), wrapped_text, fill="#4A5568", font=desc_font)

            # if 'location' in event and event['location'] and event['location'] != "None":
            #     loc_y = y_pos + 85
            #     draw.text((details_x, loc_y), event['location'], fill="#718096", font=desc_font)
        
        # Save the image
        img.save(output_path)
        print(f"Calendar image saved as {output_path} ({IMAGE_WIDTH}x{IMAGE_HEIGHT} pixels)")
        return img

    def draw_rounded_rectangle(draw, xy, radius=10, fill=None, outline=None, width=1, corners=(True, True, True, True)):
        x1, y1, x2, y2 = xy
        width = max(width, 1)  # Make sure width is at least 1
        
        # If the radius is too large, adjust it
        radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
        
        # Draw four corners
        if corners[0]:  # top-left
            draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill, outline=outline, width=width)
        else:
            draw.rectangle([x1, y1, x1 + radius, y1 + radius], fill=fill, outline=outline, width=width)
            
        if corners[1]:  # top-right
            draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 0, fill=fill, outline=outline, width=width)
        else:
            draw.rectangle([x2 - radius, y1, x2, y1 + radius], fill=fill, outline=outline, width=width)
            
        if corners[2]:  # bottom-right
            draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill, outline=outline, width=width)
        else:
            draw.rectangle([x2 - radius, y2 - radius, x2, y2], fill=fill, outline=outline, width=width)
            
        if corners[3]:  # bottom-left
            draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill, outline=outline, width=width)
        else:
            draw.rectangle([x1, y2 - radius, x1 + radius, y2], fill=fill, outline=outline, width=width)
        
        # Draw connecting rectangles
        draw.rectangle([x1 + radius, y1, x2 - radius, y1 + radius], fill=fill, outline=fill)  # top
        draw.rectangle([x1, y1 + radius, x1 + radius, y2 - radius], fill=fill, outline=fill)  # left
        draw.rectangle([x2 - radius, y1 + radius, x2, y2 - radius], fill=fill, outline=fill)  # right
        draw.rectangle([x1 + radius, y2 - radius, x2 - radius, y2], fill=fill, outline=fill)  # bottom
        
        # Fill in the center
        draw.rectangle([x1 + radius, y1 + radius, x2 - radius, y2 - radius], fill=fill, outline=fill)

    # Pass the events to the calendar image function
    create_calendar_image(events, destination+"/calendar.png")

def download_calendar(key="calendar-url", json_file="config.json", destination="downloads"):
    download_dir = os.path.join(os.getcwd(), destination)
    os.makedirs(download_dir, exist_ok=True)
    try:
        with open(json_file) as f:
            config = json.load(f)
            calendar_url = config.get(key, "")
            get_calendar(calendar_url, destination)
            return 1
            if not calendar_url:
                print(f"Error: calendar-url not found in config.json")
                return 0
    except Exception as e:
        print(f"Error loading config: {e}")
        return 0

download_calendar("calendar-url", "testconfig.json", "downloads")
