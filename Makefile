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
del-all: del-xmls del-pdfs db-rm
.PHONY: db-rm del-pdfs del-all