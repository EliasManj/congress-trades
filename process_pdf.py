import pdfplumber
import re
import os
import pandas as pd
import yaml
import db_engine

column_names = re.compile(r'ID Owner Asset Transaction Date Notification Amount Cap.\nType Date Gains >\n\$200\?')
separator = re.compile(r'\nF S: New\n(?:D: .*\n)?(?:S O: .*\n)?(?:D: .*\n)?(?:C: .*\n)?')    
stock_pattern = r'^(?:JT|SP)?(.+?)\s+(S \(partial\)|S|P)\s+'
date_pattern = r'(\d{2}/\d{2}/\d{4})'
amount_pattern = r'\$(\d{1,3}(?:,\d{3})(?:,\d{3})?)'
amount_pattern_asset = r'(\$\d{1,3}(?:,\d{3})(?:,\d{3})?)'

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
    
    
    return (stock, type_, date, notification_date, amount_matches[0], amount_matches[1], filing)

def parse_list1(array):
    array = array[:-1]
    processed_list = []
    for item in array:
        lines = item.split('\n')
        if ('[ST]' in lines[-1] or '[OP]' in lines[-1]) and len(lines) > 1:
            last_line = lines.pop()
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
    print(text)
    result = re.split(separator, text)
    parsed1 = parse_list1(result)
    parsed2 = convert_to_dict(parsed1, file_name)
    return parsed2

def pdf_purchases_to_df(purchases):
    return pd.DataFrame(purchases, columns=['Stock', 'Type', 'Date', 'Notification Date', 'Amount', 'Filing'])

def list_files(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)
    return file_paths

def insert_purchases_to_db(purchases, db):
    for purchase in purchases:
        exists = db.session.query(db_engine.Transaction).filter_by(asset=purchase[0], transaction_date=purchase[2], min_amount=purchase[4], max_amount=purchase[5], docid=purchase[6]).first()
        if not exists:
            db_purchase = db_engine.Transaction(asset=purchase[0], transaction_type=purchase[1], transaction_date=purchase[2], notification_date=purchase[3], min_amount=purchase[4], max_amount=purchase[5], docid=purchase[6])
            db.session.add(db_purchase)
            db.session.commit()

if __name__ == "__main__":
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    db = db_engine.DbEngine(config['db'])
    pdf_path = config['pdf_directory']
    pdf_files = list_files(pdf_path)
    purchases = []
    for file in pdf_files:
        purchases.extend(get_pdf_purchases(file))
    insert_purchases_to_db(purchases, db)
    
        