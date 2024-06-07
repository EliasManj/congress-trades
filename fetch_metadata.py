import os
import get_files
import sqlite3
import db_engine

class Fetch:

    def __init__(self):
        self.db = db_engine.DbEngine('sqlite:///db/database.db')

    def process_persons(self):
        metadata = get_files.process_xml_files('data/xml')
        for file in metadata:
            for entry in metadata[file]:
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
            if filing.filing_type == 'P' or filing.filing_type == 'A':
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
        get_files.download_file(url, f"data/pdf/{year}/{doc}.pdf")


if __name__ == '__main__':

    fetch = Fetch()
    fetch.process_persons()
    fetch.fetch_filings()