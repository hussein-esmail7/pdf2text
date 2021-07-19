
'''
pdf.py
Hussein esmail
Created: 2021 02 21
Updated: 2021 07 18
Description: This program can convert text from a PDF to text.
'''

import sys                  # Used to exit the program
import os                   # Used to change directories
from pathlib import Path    # Used to 'touch' output file
import time                 # Used to count how long the program takes
import subprocess           # Used to install libraries if they're not already
import pkg_resources        # Used to check which libraries are installed
import json                 # Used to import configs used for writing to files            

"""
Dependencies:
    - Poppler --> https://poppler.freedesktop.org
        - Installation:
            macOS: brew install poppler
            apt-get install poppler-utils
            conda install -c conda-forge poppler
"""

TYPES_INPUT             = ["pdf", "png", "jpg"]
TYPES_OUTPUT            = ['Console', '.txt (Text Document)', '.md (Markdown)']
MSG_ASK_FILE            = "Which file would you like to convert? "
MSG_ASK_DIR             = "What directory is your pdf file in: "
MSG_ASK_OUTPUT_TYPE     = "What output file type do you want: "
MSG_ERR_DIR_DNE         = "It looks like that directory doesn't exist..."
MSG_CONVERTING          = "Converting pdf pages..."
MSG_DONE                = "File done writing."
MSG_OUTPUT_FILE_NAME    = "Output file is: "
TEMP_IMAGE_TYPE         = ".jpg"
TEMP_IMAGE_TYPE_FORMAT  = "JPEG"
PDF_LANG                = "eng"
JSON_FILE_NAME          = "styling.json"

def check_install(lib_install):
    # Checks if all necessary packages are installed. If not, install them.
    if lib_install not in {pkg.key for pkg in pkg_resources.working_set}:
        python = sys.executable
        print(f"You didn't have the {lib_install} library, but I'm installing it for you...")
        subprocess.check_call([python, '-m', 'pip', 'install', lib_install], stdout=subprocess.DEVNULL)
        print(f"{lib_install} installed.")


def check_filename(front, extension):
    output_filename_count = 1
    to_return = ""
    while True:
        if to_return + extension not in os.listdir():
            to_return += extension
            break
        else:
            if to_return + " (" + str(output_filename_count) + ")" + extension not in os.listdir():
                to_return = to_return + " (" + str(output_filename_count) + ")" + extension
                break
            else:
                output_filename_count += 1
    return to_return

def main():
    check_install("pdf2image")
    check_install("pillow")         # Note: Pillow is the PIL library
    check_install("pytesseract")
    check_install("pick")
    
    # These are here in case they weren't already installed
    from pdf2image import convert_from_path     # Used to convert pdf to images
    from PIL import Image                       # Used to open image for pytesseract
    from pytesseract import image_to_string     # Converts image to text
    from pick import pick                       # Used to ask the user the output file type

    page_num            = 1     # Page counter
    convertable_files   = []    # Files that are in the directory that can be converted    
    output_text         = []    # Text that will go in the output document(s)
    
    # Import JSON data
    data = json.load(open(JSON_FILE_NAME,)) # Returns JSON object as a dictionary
    
    while True: # Ask user for the directory of the pdf file. Keeps asking until it gets a valid one
        directory = input(MSG_ASK_DIR)
        try:
            if os.path.isdir(directory):    # If the directory exists
                os.chdir(directory)
                for i in os.listdir():
                    if i.split(".")[-1] in TYPES_INPUT:
                        convertable_files.append(i)
                break                       # Do not ask for the directory again (since a valid one was given)
            else:                           # If the directory does not exist, keep asking
                convertable_files = []
        except:
            print(MSG_ERR_DIR_DNE)
    
    pdf_name, _ = pick(convertable_files, MSG_ASK_FILE)
    output_option, _ = pick(TYPES_OUTPUT, MSG_ASK_OUTPUT_TYPE)
    # All items that are not "Console" must follow this format for code to work:
    # ".<filetype> <other stuff...>" (emphasis on the dot as first character and the space)

    print(MSG_CONVERTING)
    pages = convert_from_path(pdf_name, dpi=500) # userpw="" # If the pdf requires a password, input it here in the function
    start_time = time.time()                        # Track start time of the PDF
    for page in pages:                              # For every page in the PDF
        i_start_time = time.time()                  # Start time of this page
        temp_filename = ".out" + str(page_num) + TEMP_IMAGE_TYPE # Temporary file name for image
        page.save(temp_filename, TEMP_IMAGE_TYPE_FORMAT)            # Save file temporarily so pytesseract can access it
        image_text = image_to_string(Image.open(temp_filename), lang=PDF_LANG)
        os.remove(temp_filename)                    # Get rid of the temp file immediately
        output_text.append(image_text)
        if output_option == "Console": # Print in the loop rather than after all at once.
            print(output_text[-1])
        i_end_time = time.time()
        print(f"Done {page_num}/{len(pages)} pages (took {round(i_end_time - i_start_time, 1)}s).")
        page_num += 1

    # Find a fine name that is not in use. If it's console then no need because you wouldn't need to make a file then
    if output_option != "Console": # Write to file
        output_type = output_option.split(" ")[0]
        output_filename = check_filename("output", output_type)
        print(MSG_OUTPUT_FILE_NAME + output_filename)
        Path(output_filename).touch() # 'touch' the file
        output_text = [i.replace("\n\n", "\n") for i in output_text]    # Personal preference

        with open(output_filename, "w") as f:
            f.write(f"{data['header_document'][output_type]}{output_filename}\n")
            for i in range(len(output_text)):
                f.write(f"{data['header_page'][output_type]} {i+1}\n")
                blankline_written = False
                page_lines = output_text[i].split("\n")
                for line in page_lines: # For all the lines on that page
                    if line.strip() == "" and not blankline_written:
                        blankline_written = True
                        f.write("\n")
                    elif line.strip() != "":
                        blankline_written = False
                        f.write(line.strip() + "\n")
        end_time = time.time()
        print(f"Took {round(end_time - start_time, 1)}s total.")
        print(MSG_DONE)
    sys.exit()

if __name__ == "__main__":
    check_install() 
    main()