PANDOC_OPTIONS= -V geometry:"left=0.75in, top=0.75in, right=0.75in, bottom=2cm"
PWD=$(shell pwd)

rapport:
	cd rapport && pandoc -H conf.tex $(PANDOC_OPTIONS) report.md -o report.pdf
.PHONY: rapport