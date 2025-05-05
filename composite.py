import os
import math
from PIL import Image
import itertools

def create_composite():
    output_dir = 'downloads/extracted/comps'
    os.makedirs(output_dir, exist_ok=True)
    
    # Paths
    left_dir = 'downloads/extracted/left'
    right_dir = 'downloads/extracted/right'
    calendar_path = 'downloads/calendar.png'
    home_path = 'home/home.png'

    BORDER_PADDING = 25
    
    # Get all image files from left and right directories
    left_images = [os.path.join(left_dir, f) for f in sorted(os.listdir(left_dir)) 
                  if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    right_images = [os.path.join(right_dir, f) for f in sorted(os.listdir(right_dir)) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Load the calendar and home images
    calendar_img = Image.open(calendar_path)
    home_img = Image.open(home_path)
    
    # First image is just the home image
    home_img.save(os.path.join(output_dir, '1.png'))
    
    # Create all possible combinations of left and right images (in groups of 2)
    image_count = 2  # Start numbering from 2 since 1 is home
    
    # Group left images into pairs (if odd, last group will have home.jpg)
    left_pairs = []
    for i in range(0, len(left_images), 2):
        if i + 1 < len(left_images):
            left_pairs.append([left_images[i], left_images[i+1]])
        else:
            left_pairs.append([left_images[i], home_path])
    
    # If left folder is empty, use home.jpg
    if not left_pairs:
        left_pairs.append([home_path, home_path])
    
    # Group right images into pairs (if odd, last group will have home.jpg)
    right_pairs = []
    for i in range(0, len(right_images), 2):
        if i + 1 < len(right_images):
            right_pairs.append([right_images[i], right_images[i+1]])
        else:
            right_pairs.append([right_images[i], home_path])
    
    # If right folder is empty, use home.jpg
    if not right_pairs:
        right_pairs.append([home_path, home_path])
    
    # Get calendar dimensions for reference
    calendar_width = calendar_img.width
    calendar_height = calendar_img.height
    
    # Calculate the ideal height for each side image (half of calendar height)
    side_height = calendar_height // 2

    lcm_count = math.lcm(len(left_pairs), len(right_pairs))
    left_repeat = lcm_count // len(left_pairs)
    right_repeat = lcm_count // len(right_pairs)

    # Create expanded arrays with repeated elements
    expanded_left_pairs = []
    for _ in range(left_repeat):
        expanded_left_pairs.extend(left_pairs)

    expanded_right_pairs = []
    for _ in range(right_repeat):
        expanded_right_pairs.extend(right_pairs)

    # Now both arrays have the same length (lcm_count)
    # Pair them up directly
    combinations = []
    for i in range(lcm_count):
        combinations.append((expanded_left_pairs[i], expanded_right_pairs[i]))
    
    # Generate all combinations of left and right pairs
    for left_pair, right_pair in combinations:
        # Create a new blank image
        # Width = left column + center column + right column
        composite_width = calendar_width * 3  # Equal width for all columns
        composite_height = calendar_height
        composite = Image.new('RGB', (composite_width, composite_height), 'white')
        
        # Place the calendar in the center
        calendar_x = calendar_width
        composite.paste(calendar_img, (calendar_x, 0))

        two_image_height_left = 0
        two_image_height_right = 0
        
        # Process and place left images
        for i, img_path in enumerate(left_pair):
            img = Image.open(img_path)
            # Resize while maintaining aspect ratio
            img_aspect = img.width / img.height
            side_width = calendar_width
            
            if img.height > img.width:  # Portrait
                # For portrait, fit by height
                new_height = side_height
                new_width = int(new_height * img_aspect)
                if new_width > side_width:
                    new_width = side_width
                    new_height = int(new_width / img_aspect)
            else:  # Landscape
                # For landscape, fit by width
                new_width = side_width
                new_height = int(new_width / img_aspect)
                if new_height > side_height:
                    new_height = side_height
                    new_width = int(new_height * img_aspect)
            two_image_height_left = two_image_height_left + new_height

        # Process and place left images
        for i, img_path in enumerate(left_pair):
            img = Image.open(img_path)
            # Resize while maintaining aspect ratio
            img_aspect = img.width / img.height
            side_width = calendar_width
            
            if img.height > img.width:  # Portrait
                # For portrait, fit by height
                new_height = side_height
                new_width = int(new_height * img_aspect)
                if new_width > side_width:
                    new_width = side_width
                    new_height = int(new_width / img_aspect)
            else:  # Landscape
                # For landscape, fit by width
                new_width = side_width
                new_height = int(new_width / img_aspect)
                if new_height > side_height:
                    new_height = side_height
                    new_width = int(new_height * img_aspect)
            
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)

            make_space = (calendar_height - two_image_height_left)//3
            
            # Calculate position (top image aligned to top, bottom image aligned to bottom)
            x_pos = BORDER_PADDING + (side_width - new_width) // 2
            y_pos = 0 + make_space if i == 0 else side_height - new_height - make_space  # Top for first image, bottom for second
            
            # Create a white background for this cell
            cell_bg = Image.new('RGB', (side_width, side_height), '#E3EDF5')
            # Paste the resized image onto the white background
            cell_bg.paste(resized_img, (x_pos, y_pos))
            # Paste the cell onto the composite
            composite.paste(cell_bg, (0, i * side_height))

        two_image_height_right = 0
        
        # Process and place right images
        for i, img_path in enumerate(right_pair):
            img = Image.open(img_path)
            # Resize while maintaining aspect ratio
            img_aspect = img.width / img.height
            side_width = calendar_width
            
            if img.height > img.width:  # Portrait
                # For portrait, fit by height
                new_height = side_height
                new_width = int(new_height * img_aspect)
                if new_width > side_width:
                    new_width = side_width
                    new_height = int(new_width / img_aspect)
            else:  # Landscape
                # For landscape, fit by width
                new_width = side_width
                new_height = int(new_width / img_aspect)
                if new_height > side_height:
                    new_height = side_height
                    new_width = int(new_height * img_aspect)
            two_image_height_right = two_image_height_right + new_height

        # Process and place right images
        for i, img_path in enumerate(right_pair):
            img = Image.open(img_path)
            # Resize while maintaining aspect ratio
            img_aspect = img.width / img.height
            side_width = calendar_width
            
            if img.height > img.width:  # Portrait
                # For portrait, fit by height
                new_height = side_height
                new_width = int(new_height * img_aspect)
                if new_width > side_width:
                    new_width = side_width
                    new_height = int(new_width / img_aspect)
            else:  # Landscape
                # For landscape, fit by width
                new_width = side_width
                new_height = int(new_width / img_aspect)
                if new_height > side_height:
                    new_height = side_height
                    new_width = int(new_height * img_aspect)
            
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)

            make_space = (calendar_height - two_image_height_right)//3
            
            # Calculate position (top image aligned to top, bottom image aligned to bottom)
            x_pos = (side_width - new_width) // 2 - BORDER_PADDING
            y_pos = 0 + make_space if i == 0 else side_height - new_height - make_space  # Top for first image, bottom for second

            # print(x_pos+25, y_pos)
            
            # Create a white background for this cell
            cell_bg = Image.new('RGB', (side_width, side_height), '#E3EDF5')
            # Paste the resized image onto the white background
            cell_bg.paste(resized_img, (x_pos, y_pos))
            # Paste the cell onto the composite
            composite.paste(cell_bg, (calendar_width * 2, i * side_height))
        
        # Save the composite image
        composite.save(os.path.join(output_dir, f'{image_count}.png'))
        image_count += 1
        # print(two_image_height_right)
        two_image_height_right = 0
        two_image_height_left = 0

    print(f"Generated {image_count-1} composite images in {output_dir}")
