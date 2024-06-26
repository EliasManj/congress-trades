import pdfplumber
import re
import os
import yaml
import db_engine
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

column_names = re.compile(r'ID Owner Asset Transaction Date Notification Amount Cap.\nType Date Gains >\n\$200\?')
separator = re.compile(r'\nF S: New\n(?:L: .*\n|D: .*\n|C: .*\n|S O: .*\n)*')
stock_pattern = r'^(?:JT|SP)?(.+?)\s+(S \(partial\)|S|P)\s+'
date_pattern = r'(\d{2}/\d{2}/\d{4})'
amount_pattern = r'\$(\d{1,3}(?:,\d{3})(?:,\d{3})?)'
amount_pattern_asset = r'(\$\d{1,3}(?:,\d{3})(?:,\d{3})?)'
ticker_pattern = r'\((\w+)\)'

def printls(array):
    print('[')
    for item in array:
        print(item)
    print(']')
    print()

def has_table(page):
    text = page.extract_text()
    return column_names.search(text)
    
def get_extract(page):
    text = page.extract_text()
    result = column_names.search(text)
    if result: 
        # Get the end position of the matched text
        start_position = result.end()
        # Slice the text from the end position of the matched text to the end of the string
        remaining_text = text[start_position:].strip()    
        return remaining_text

def pages_with_tables(pdf):
    return [index for index, page in enumerate(pdf.pages) if has_table(page)]

def get_filings_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page for page in pdf.pages if has_table(page)]
        all_text = ""
        for page in pages:
            important_text = get_extract(page)
            all_text += important_text + "\n"
        cleaned_text = all_text.replace('\x00', '')
        return cleaned_text
    
def parse_string(s, filing):
    # Extract stock and type
    stock_type_match = re.search(stock_pattern, s)
    if not stock_type_match:
        return None
    
    stock = stock_type_match.group(1).strip()
    stock = re.sub(amount_pattern_asset,'',stock)
    
    type_ = stock_type_match.group(2).strip()
    
    # Extract dates
    date_matches = re.findall(date_pattern, s)
    if len(date_matches) < 2:
        return None
    
    date = date_matches[0]
    notification_date = date_matches[1]
    
    # Extract amount
    amount_matches = re.findall(amount_pattern, s)
    if not amount_matches:
        return None
    
    sorted_amounts = sorted(amount_matches, key=lambda x: int(x.replace(',', '')))

    # check if purchase is stock or option
    
    if '[OP]' in stock:
        security = 'OP'
        stock = stock.replace('[OP]', '')
    elif '[ST]' in stock:
        security = 'ST'
        stock = stock.replace('[ST]', '')
    elif '[AB]' in stock:
        security = 'AB'
        stock = stock.replace('[AB]', '')
    else:
        security = 'ST'

    match = re.search(ticker_pattern, stock)

    ticker = match.group(1) if match else None
    
    return {'stock': stock,  'ticker': ticker, 'security': security, 'type': type_, 'date': date, 'notification_date': notification_date, 'min_amount': sorted_amounts[0], 'max_amount': sorted_amounts[1], 'filing': filing}

def parse_list1(array):
    array = array[:-1]
    processed_list = []
    for item in array:
        lines = item.split('\n')
        if ('[ST]' in lines[-1] or '[OP]' in lines[-1] or '[AB]' in lines[-1]) and len(lines) > 1:
            last_line = ""
            while len(lines) > 1:
                last_line += lines.pop()
            # Find the position of the first date (assumed to be in the format MM/DD/YYYY)
            match = re.search(r' S \(partial\) | P | S ', lines[0])
            if match:
                first_date_pos = match.start()
                lines[0] = lines[0][:first_date_pos] + last_line + ' ' + lines[0][first_date_pos:]
        processed_list.append('\n'.join(lines))
    return processed_list

def convert_to_dict(array, filing):
    return [parse_string(item, filing) for item in array]
    
def get_pdf_purchases(file):
    file_name = os.path.splitext(os.path.basename(file))[0]
    text = get_filings_from_pdf(file)
    result = re.split(separator, text)
    parsed1 = parse_list1(result)
    parsed2 = convert_to_dict(parsed1, file_name)
    for item in parsed2:
        if item is None:
            print("item is None")
    return parsed2

def list_files(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)
    return file_paths

def insert_purchases_to_db(purchases, db):
    for index, purchase in enumerate(purchases):
        if purchase is None:
            continue
        exists = db.session.query(db_engine.Transaction).filter_by(asset=purchase['stock'], transaction_date=purchase['date'], min_amount=purchase['min_amount'], max_amount=purchase['max_amount'], docid=purchase['filing']).first()
        if not exists:
            db_purchase = db_engine.Transaction(asset=purchase['stock'], security=purchase['security'], transaction_type=purchase['type'], transaction_date=purchase['date'], notification_date=purchase['notification_date'], min_amount=purchase['min_amount'], max_amount=purchase['max_amount'], docid=purchase['filing'], ticker=purchase['ticker'])
            db.session.add(db_purchase)
            db.session.commit()

if __name__ == "__main__":
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    db = db_engine.DbEngine(config['db'])
    pdf_path = f'{config["data"]["dir"]}/pdf'
    pdf_files = list_files(pdf_path)
    purchases = []
    for file in pdf_files:
        print(file)
        purchases.extend(get_pdf_purchases(file))
    insert_purchases_to_db(purchases, db)
    
        