import os
import get_xmls
import db_engine
import yaml
import xml.etree.ElementTree as ET

class PdfDownloader:

    def __init__(self, config):
        self.db = db_engine.DbEngine('sqlite:///db/database.db')
        self.config = config

    def process_xml_files(self):
        directory = self.config['xml_directory']
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

    def process_persons(self):
        metadata = self.process_xml_files()
        person_filter = self.config['members']
        for file in metadata:
            for entry in metadata[file]:
                if entry['Last'].lower() in person_filter:
                    person = self.db.session.query(db_engine.Person).filter_by(firstname=entry['First'], lastname=entry["Last"], prefix=entry['Prefix']).first()
                    if person is None:
                        person = db_engine.Person(prefix=entry['Prefix'], lastname=entry['Last'], firstname=entry['First'], suffix=entry['Suffix'])
                        self.db.session.add(person)
                        self.db.session.commit()
                    filing = self.db.session.query(db_engine.Filling).filter_by(person_id=person.id, filing_date=entry['FilingDate'], docid=entry['DocID']).first()
                    if filing is None:
                        filing = db_engine.Filling(person_id=person.id, filing_type=entry['FilingType'], state_dst=entry['StateDst'], year=entry['Year'], filing_date=entry['FilingDate'], docid=entry['DocID'])
                        self.db.session.add(filing)
                        self.db.session.commit()

    def fetch_filings(self):
        filings = self.db.session.query(db_engine.Filling).all()
        for filing in filings:
            if filing.filing_type == 'P':
                self.download_filling_pdf(filing)

    def row_to_dict(self, row):
        return {col[0]: row[i] for i, col in enumerate(self.cursor.description)}
    
    def check_if_person(self, person):
        query = f"SELECT id FROM persons WHERE"
        conditions = []
        values = []
        for key, value in person.items():
            if value is None:
                conditions.append(f"{key.lower()} IS NULL")
            else:
                conditions.append(f"{key.lower()} = ?")
                values.append(value)
        query += " AND ".join(conditions)
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def download_filling_pdf(self, filing):
        year = filing.year
        doc =  filing.docid
        filing_type = filing.filing_type
        if filing_type == 'P':
            url = f"https://disclosures-clerk.house.gov/public_disc/ptr-pdfs/{year}/{doc}.pdf"
        else:
            url = f"https://disclosures-clerk.house.gov/public_disc/financial-pdfs/{year}/{doc}.pdf"
        get_xmls.download_file(url, f"data/pdf/{year}/{doc}.pdf")


if __name__ == '__main__':

    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    
    fetch = PdfDownloader(config)
    fetch.process_persons()
    fetch.fetch_filings()