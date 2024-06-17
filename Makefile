get-xmls:
	@python3 get_xmls.py --download
del-xmls:
	@python3 get_xmls.py --delete
del-pdfs:
	rm -rf data/pdf/2024/*
get-pdfs:
	@python3 get_pdfs.py
db-rm:
	@rm db/database.db
process_pdfs:
    @python3 process_pdfs.py
del-all: del-xmls del-pdfs db-rm
get-data: get_xmls get_pdfs process_pdfs
.PHONY: db-rm del-pdfs del-all