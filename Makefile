get-xmls:
	@python3 get_xmls.py --download
del-xmls:
	@python3 get_xmls.py --delete
del-pdfs:
	rm -rf data/pdf/2024/*
get-pdfs:
	@python3 get_pdfs.py
db-init:
	@sqlite3 db/database.db < db/schema.sql
db-remove:
	@rm db/database.db
db-reset: db-remove db-init
del-all: del-xmls del-pdfs db-reset

.PHONY: db-init db-remove db-reset del-pdfs del-all