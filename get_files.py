import yaml, requests, zipfile, os, glob, shutil, argparse
import xml.etree.ElementTree as ET

def load_config():
    with open('config.yaml', 'r') as file:
        data = yaml.safe_load(file)
    return data

def download_file(url, save_path):
    # Send a HTTP request to the URL
    response = requests.get(url)
    
    # Raise an exception if there was an error in the request
    response.raise_for_status()

    directory = os.path.dirname(save_path)
    
    # Create the directories if they don't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Open the file in write-binary mode and write the response content
    with open(save_path, 'wb') as file:
        file.write(response.content)

def unzip_file(zip_path, extract_to):
    # Open the zip file in read mode
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all the contents into the specified directory
        zip_ref.extractall(extract_to)

def delete_non_xml_files(directory):
    # Get a list of all files in the directory
    files = glob.glob(os.path.join(directory, '*'))
    
    for file in files:
        # Check if the file does not end with .xml
        if not file.endswith('.xml'):
            # Remove the file
            os.remove(file)
            print(f"Deleted {file}")

def process_xml_files(directory):
    result = {}
    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        dict_list = []
        file_path = os.path.join(directory, filename)
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for member in root:
            # Process each member element (print for example)
            item = {child.tag: child.text for child in member}
            if item['FilingType'] == 'A' or item['FilingType'] == 'P':
                dict_list.append(item)
        result[filename] = dict_list
    return result

def delete_all_files_in_directory(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path):
        print(f"The directory {directory_path} does not exist.")
        return

    # Iterate over all the files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        
        try:
            # Check if it is a file and remove it
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # If it is a directory, remove it and its contents
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    print(f"All files in {directory_path} have been deleted.")


def get_files(config):
    # download zip files
    years = config['years']
    zip_folder = config['zip_path']
    data_folder = config['data_path']
    file = config['url']
    os.makedirs(zip_folder, exist_ok=True)
    os.makedirs(data_folder, exist_ok=True)
    for year in years:
        url = file.format(YEAR=year)
        zip_file = f"{zip_folder}/{year}FD.zip"
        download_file(url, zip_file)
        unzip_file(zip_file, data_folder)
    delete_non_xml_files(data_folder)

def main():

    config = load_config()
    zip_folder = config['zip_path']
    data_folder = config['data_path']

    parser = argparse.ArgumentParser(description="Process some parameters.")
    parser.add_argument('--delete', action='store_true', help="Call function1")
    parser.add_argument('--download', action='store_true', help="Call function2")
    
    args = parser.parse_args()
    
    if args.delete:
        delete_all_files_in_directory(data_folder)
        delete_all_files_in_directory(zip_folder)
    else:
        get_files(config)

if __name__ == '__main__':
    main()
