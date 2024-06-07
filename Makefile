get-xmls:
	@python3 get_files.py --download
del-xmls:
	@python3 get_files.py --delete
get-members:
	@python3 fetch_metadata.py
db-init:
	@sqlite3 db/database.db < db/schema.sql
db-remove:
	@rm db/database.db
db-reset: db-remove db-init

.PHONY: db-init db-remove db-reset