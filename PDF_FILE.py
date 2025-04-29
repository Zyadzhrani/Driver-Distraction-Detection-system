import pdfkit
from bs4 import BeautifulSoup
from datetime import datetime
import os
import shutil
import psutil  

# Path to the wkhtmltopdf executable 
path_to_wkhtmltopdf = r"/usr/local/bin/wkhtmltopdf" 

# Create a pdfkit configuration object with the path to wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf=path_to_wkhtmltopdf)

# Open the HTML file
html_file = r"PDF.html"
with open(html_file, "r") as file:
    soup = BeautifulSoup(file, "lxml")

# Path to the text file
txt_file = r"destraction_save.txt"  # Path to the text file

# Function to find USB drives on the system
def get_usb_drives():
    usb_drives = []
    partitions = psutil.disk_partitions()
    for part in partitions:

        if 'media' in part.mountpoint.lower():  # Common mount point for USB drives
            usb_drives.append(part.mountpoint)
    return usb_drives


# Function to copy the file to each USB drive
def copy_file_to_usb(file_path):
    usb_drives = get_usb_drives()
    if usb_drives:
        for drive in usb_drives:
            # Define the destination path for the file on the USB drive
            destination = os.path.join(drive, os.path.basename(file_path))
            try:
                shutil.copy(file_path, destination)
                print(f"File successfully copied to {destination}")
            except Exception as e:
                print(f"Error copying to {drive}: {e}")
    else:
        print("No USB drives found.")

# Check if the text file exists
if not os.path.exists(txt_file):
    print("Text file not found. Please ensure the file exists.")
else:
    # Read data from the text file and parse it
    distraction_data = []

    try:
        with open(txt_file, "r") as file:
            lines = file.readlines()
            
            # Extract the start date and time from the first line
            date_line = lines[0].strip()  # The first line will be the date (YYYY-MM-DD HH:MM:SS)
            
            # Debug: Check the date format in the text file
            print(f"Start Date and Time from file: {date_line}")

            # Convert the date string to a datetime object and format it
            try:
                # Attempt to parse the start date and time from the file using the correct format
                start_date_object = datetime.strptime(date_line, "%Y-%m-%d %H:%M:%S")  # Correct parsing format
                start_date = start_date_object.strftime("%Y-%m-%d")  # Format the Start Date as YYYY-MM-DD
                start_time = start_date_object.strftime("%H:%M:%S")  # Format the Start Time as HH:MM:SS
            except ValueError:
                start_date = "Invalid Date"
                start_time = "Invalid Time"
                print(f"Error: The date format is incorrect. Expected format: 'YYYY-MM-DD HH:MM:SS'")

            # For End Date and End Time, use the current date and time
            end_date_object = datetime.now()
            end_date = end_date_object.strftime("%Y-%m-%d")  # Current date
            end_time = end_date_object.strftime("%H:%M:%S")  # Current time

            # Set the start and end dates/times in the HTML
            start_date_element = soup.find("span", {"id": "start-date"})
            if start_date_element:
                start_date_element.string = start_date  # Set the Start Date in the HTML
            
            start_time_element = soup.find("span", {"id": "start-time"})
            if start_time_element:
                start_time_element.string = start_time  # Set the Start Time in the HTML
            
            end_date_element = soup.find("span", {"id": "end-date"})
            if end_date_element:
                end_date_element.string = end_date  # Set the End Date in the HTML
            
            end_time_element = soup.find("span", {"id": "end-time"})
            if end_time_element:
                end_time_element.string = end_time  # Set the End Time in the HTML

            # Each subsequent row corresponds to a specific distraction type
            distraction_types = [
                "Holding mobile phone against his/her ear",
                "Talking to passengers",
                "Not holding the steering wheel",
                "Holding mobile phone in hands"
            ]
            
            # Make sure we have 4 lines in the txt file for distraction counts
            if len(lines) == 5:  # Including the date line, we expect 5 lines
                for i, line in enumerate(lines[1:]):  # Start from the second line
                    count = line.strip()  # Get the number from each line
                    distraction_data.append({"type": distraction_types[i], "count": count})

    except Exception as e:
        print(f"An error occurred while processing the text file: {e}")

    # Insert data into the Summary Table (tbody with id "summary-body")
    summary_body = soup.find("tbody", {"id": "summary-body"})
    if summary_body:
        summary_body.clear()  # Clear existing rows

        for distraction in distraction_data:
            row = soup.new_tag("tr")

            # Add the Distraction Type cell (this remains unchanged)
            td1 = soup.new_tag("td")
            td1.string = distraction["type"]
            row.append(td1)

            # Add the Number of Distractions cell (this will change dynamically)
            td2 = soup.new_tag("td")
            td2.string = f"{distraction['count']} Times"
            row.append(td2)

            # Append the row to the Summary Table body
            summary_body.append(row)

    # Save the modified HTML to a new file
    with open(html_file, "w") as file:
        file.write(str(soup))

    print("Distraction data and summary inserted into 'PDF.html'.")

    # Generate a PDF from the modified HTML with a static report name and A4 page size
    from datetime import datetime

	# Get current date and time
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")

# Create the filename with timestamp
    output_pdf = f"REPORT_{current_time}.pdf"


    # Set the PDF options for A4 size and other configurations
    options = {
        'page-size': 'A4',              # Ensure the PDF is A4 size
        'margin-top': '1mm',            # Set top margin
        'margin-right': '1mm',          # Set right margin
        'margin-bottom': '1mm',         # Set bottom margin
        'margin-left': '1mm',           # Set left margin
        'footer-center': '[page]',      # Add page number at the footer center
        'no-outline': None,             # Remove outline
        'zoom': '1.2',                  # Default zoom to 1.0
    }

    # Convert the updated HTML to a PDF and save it with the specified options
    pdfkit.from_file(html_file, output_pdf, configuration=config, options=options)

    print(f"Updated PDF file has been saved to {output_pdf}")

    # After saving the file, copy it to every USB drive
    copy_file_to_usb(output_pdf)

    # Remove the PDF after copying it to USB drives
    try:
        os.remove(txt_file)  # This will remove the PDF file from the original location
        print(f"Text file {txt_file} has been deleted.")
        log_file = "destraction_save.txt"
        if not os.path.exists(log_file):
         with open(log_file, "w") as f:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(now + "\n")
            f.write("0\n" * 4)
         print(f"Created and initialized log file: {log_file}")
    except Exception as e:
        print(f"Error deleting the txt file: {e}")
