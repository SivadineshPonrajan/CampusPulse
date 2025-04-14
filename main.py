import os
import json
import shutil
import zipfile
import subprocess
from downloader import download_folder
from hhcalendar import download_calendar
from composite import create_composite

import sys
import signal
import time
import threading
import select
import termios
import tty
import glob

exit_flag = False
restart_flag = False

config_file = "config.json"

destination_folder = "downloads"
# Download Path
download_dir = os.path.join(os.getcwd(), destination_folder)
expected_folders = {"left", "right"}

# =====================================================================================

def clear_contents(download_dir):
	if os.path.exists(download_dir):
	    for filename in os.listdir(download_dir):
	        file_path = os.path.join(download_dir, filename)
	        try:
	            if os.path.isfile(file_path) or os.path.islink(file_path):
	                os.unlink(file_path)  # Delete file or symlink
	            elif os.path.isdir(file_path):
	                shutil.rmtree(file_path)  # Delete folder
	        except Exception as e:
	            print(f"Failed to delete {file_path}. Reason: {e}")
	    print("All contents deleted from '"+download_dir+"' folder.")
	else:
	    print("'downloads' folder does not exist.")

# =====================================================================================

def unzip_n_check(download_dir):
	zip_files = [f for f in os.listdir(download_dir) if f.lower().endswith('.zip')]
	if not zip_files:
	    print("No zip file found in the downloads folder.")
	    exit()
	zip_path = os.path.join(download_dir, zip_files[0])
	extract_path = os.path.join(download_dir, "extracted")

	if os.path.exists(extract_path):
		shutil.rmtree(extract_path)
	os.makedirs(extract_path, exist_ok=True)

	with zipfile.ZipFile(zip_path, 'r') as zip_ref:
	    zip_ref.extractall(extract_path)
	    print(f"Extracted a file")

	# Check if a single folder was extracted
	top_items = os.listdir(extract_path)
	if len(top_items) == 1:
		single_item_path = os.path.join(extract_path, top_items[0])
		if os.path.isdir(single_item_path):
		    # Move contents of the folder up one level
		    for item in os.listdir(single_item_path):
		        shutil.move(os.path.join(single_item_path, item), extract_path)
		    shutil.rmtree(single_item_path)
		    print("Flattened zip structure to remove top-level folder.")

	found_folders = set()
	for item in os.listdir(extract_path):
	    item_path = os.path.join(extract_path, item)
	    if os.path.isdir(item_path):
	        found_folders.add(item.lower())

	if expected_folders.issubset(found_folders):
	    print("Folder structure is valid in the drive")
	    os.remove(zip_path)
	else:
	    print(f"Folder structure is not valid in the drive")

# =====================================================================================

# Convert PDF
def convert_pdf_to_png(filepath):
    if not os.path.isfile(filepath):
        print(f"File not found: {filepath}")
        return 0

    filename = os.path.splitext(os.path.basename(filepath))[0]
    output_prefix = os.path.join(os.path.dirname(filepath), filename)

    command = ["pdftoppm", "-png", filepath, output_prefix]

    try:
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return 1
    except subprocess.CalledProcessError:
        return 0

# =====================================================================================
# =====================================================================================

def get_valid_files(folder_path):
    valid_extensions = {'.png', '.jpg', '.jpeg', '.pdf'}
    valid_files = []
    if not os.path.exists(folder_path):
        return valid_files
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            if ext.lower() in valid_extensions:
                valid_files.append(file_path)
    return valid_files

# =====================================================================================

def convert_all_pdfs(folder_path):
    converted_count = 0
    pdf_files = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.lower().endswith('.pdf'):
            pdf_files.append(file_path)
    for pdf_path in pdf_files:
        if not os.path.isfile(pdf_path):
            print(f"File not found: {pdf_path}")
            continue
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_prefix = os.path.join(os.path.dirname(pdf_path), filename)
        command = ["pdftoppm", "-png", pdf_path, output_prefix]
        try:
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            converted_count += 1
            print(f"Converted a pdf")
        except subprocess.CalledProcessError:
            print(f"Failed to convert: {pdf_path}")
    return converted_count, pdf_files

# =====================================================================================

def rename_files_sequentially(folder_path):
    valid_extensions = {'.png', '.jpg', '.jpeg'}
    files_to_rename = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            if ext.lower() in valid_extensions:
                files_to_rename.append((file_path, ext.lower()))
    files_to_rename.sort(key=lambda x: os.path.getctime(x[0]))
    for index, (file_path, ext) in enumerate(files_to_rename, start=1):
        new_name = os.path.join(folder_path, f"{index}{ext}")
        if file_path != new_name:
            # If the target file already exists, remove it first
            if os.path.exists(new_name):
                os.remove(new_name)
            os.rename(file_path, new_name)
            print(f"Renamed: {os.path.basename(file_path)} -> {index}{ext}")
    return len(files_to_rename)

# =====================================================================================

def delete_invalid_files(folder_path):
    valid_extensions = {'.png', '.jpg', '.jpeg'}
    deleted_count = 0
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            if ext.lower() not in valid_extensions:
                os.remove(file_path)
                print(f"Deleted invalid file: {file_path}")
                deleted_count += 1
    return deleted_count

# =====================================================================================

def process_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return
    converted_count, pdf_files = convert_all_pdfs(folder_path)
    print(f"Converted PDF file to PNG")
    renamed_count = rename_files_sequentially(folder_path)
    print(f"Renamed image file")
    for pdf_path in pdf_files:
        os.remove(pdf_path)
        print(f"Deleted a PDF after conversion")
    deleted_count = delete_invalid_files(folder_path)
    print(f"Deleted additional invalid file")

# =====================================================================================

def process_extracted_folders():
    """Process both left and right folders in the extracted directory."""
    extract_path = os.path.join(download_dir, "extracted")
    if not os.path.exists(extract_path):
        print("Extracted folder does not exist.")
        return
    
    # Process left folder if it exists
    left_folder = os.path.join(extract_path, "left")
    if os.path.exists(left_folder) and os.path.isdir(left_folder):
        process_folder(left_folder)
    else:
        print("Left folder not found in extracted directory")
    
    # Process right folder if it exists
    right_folder = os.path.join(extract_path, "Right")  # Note: capital 'R' based on the tree structure
    if os.path.exists(right_folder) and os.path.isdir(right_folder):
        process_folder(right_folder)
    else:
        print("Right folder not found in extracted directory")

# =====================================================================================
exit_flag = False
restart_flag = False

def get_screen_resolution():
    try:
        result = subprocess.run(['xrandr'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if '*' in line:
                resolution = line.split()[0]
                width, height = map(int, resolution.split('x'))
                return (width, height)
    except (subprocess.SubprocessError, ValueError, IndexError, FileNotFoundError):
        print("Failed to detect screen resolution, using default 1024x768")
    return (1024, 768)

def setup_keyboard():
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        # Set the terminal to raw mode
        tty.setraw(fd)
        return fd, old_settings
    except (termios.error, OSError, AttributeError, ValueError):
        return None, None

def restore_keyboard(fd, old_settings):
    if fd is not None and old_settings is not None:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            pass

def check_for_input(fd):
    global exit_flag, restart_flag
    while not exit_flag and not restart_flag:
        try:
            r, _, _ = select.select([fd], [], [], 0.5)
            if r:
                char = sys.stdin.read(1)
                if char.lower() == 'q':
                    print("Quit command received")
                    exit_flag = True
                    break
                elif char.lower() == 'r':
                    print("Restart command received")
                    restart_flag = True
                    break
        except (select.error, OSError, ValueError):
            break
        time.sleep(0.1)  # Small sleep to reduce CPU usage

def signal_handler(sig, frame):
    global exit_flag
    print(f"Received signal {sig}, exiting...")
    exit_flag = True

def playslides(image_dir, screen_resolution=None, t_slide=30):
    png_files = glob.glob(os.path.join(image_dir, "*.png"))
    if not png_files:
        print("No PNG files found in the specified directory.")
        return None
    
    # Get screen resolution if not provided
    if screen_resolution is None:
        screen_resolution = get_screen_resolution()
    
    print(f"Starting slideshow with resolution {screen_resolution[0]}x{screen_resolution[1]}")
    cmd = [
        "feh",
        "-F",              # Fullscreen mode
        "-Y",              # Hide mouse cursor
        "-N",              # No filename display
        "--auto-zoom",     # Auto zoom to fit screen
        "--slideshow-delay", t_slide,  # 2-second delay between slides
        image_dir
    ]
    
    try:
        process = subprocess.Popen(cmd)
        print(f"Slideshow process started with PID {process.pid}")
        return process
    except FileNotFoundError:
        print("Failed to start 'feh'. Make sure it's installed (apt install feh)")
        return None
    except Exception as e:
        print(f"Error starting slideshow: {e}")
        return None

def cleanup(slideshow_process=None):
    """Cleanup function for terminating slideshow process"""
    print("Cleaning up resources...")
    if slideshow_process and slideshow_process.poll() is None:
        try:
            slideshow_process.terminate()
            time.sleep(0.5)
            if slideshow_process.poll() is None:
                slideshow_process.kill()
            print("Slideshow process terminated")
        except Exception as e:
            print(f"Error killing slideshow process: {e}")
# =====================================================================================


if __name__ == '__main__':
	# global exit_flag, restart_flag
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGTERM, signal_handler)
	while True:
		# Reset flags at the beginning of each run
		exit_flag = False
		restart_flag = False

		# Clear Existing files
		clear_contents(download_dir)
		# download files from home-url
		check = download_folder("home-url", config_file, destination_folder)
		unzip_n_check(download_dir)
		# download calendar
		download_calendar("calendar-url", config_file, destination_folder)
		process_extracted_folders()
		create_composite()
		break

		t_slide = 30

		with open(config_file, 'r') as f:
    		config = json.load(f)
    	t_slide = int(config.get("Slide-timing", 30)) 

		screen_resolution = get_screen_resolution()
		fd, old_settings = setup_keyboard()
		slideshow_process = None
		keyboard_thread = None
		if fd is not None:
		    keyboard_thread = threading.Thread(target=check_for_input, args=(fd,))
		    keyboard_thread.daemon = True
		    keyboard_thread.start()
		    print("Slideshow started. Press 'q' to quit or 'r' to restart")
		else:
		    print("Not running in a terminal - keyboard controls disabled")
		try:
		    slideshow_process = playslides(destination_folder+"/extracted/comps/", screen_resolution, t_slide)
		    while not exit_flag and not restart_flag:
		        time.sleep(0.5)
		        if slideshow_process and slideshow_process.poll() is not None:
		            print("Slideshow process has ended")
		            break
		finally:
		    cleanup(slideshow_process)
		    restore_keyboard(fd, old_settings)
		    if keyboard_thread and keyboard_thread.is_alive():
		        keyboard_thread.join(timeout=1.0)
		if exit_flag:
		    print("Exiting slideshow application")
		    break
		if restart_flag:
		    print("Restarting slideshow application")
		    continue