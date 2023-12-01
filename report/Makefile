PANDOC_OPTIONS= -V geometry:"left=0.75in, top=0.75in, right=0.75in, bottom=2cm"
PWD=$(shell pwd)

rapport:
	npx @mermaid-js/mermaid-cli -i img/archi.mmd -o img/archi.png --scale 4
	pandoc -H conf.tex $(PANDOC_OPTIONS) header.md README.md -o report.pdf
.PHONY: rapport