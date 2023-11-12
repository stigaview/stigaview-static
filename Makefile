RM = rm
MKDIR = mkdir
PYTHON = python
CP = cp
FIND = find
SED = sed
MYPY = mypy

OUT = out

all: build sitemap

build:
	@$(RM) -rf out
	@$(MKDIR) out
	@$(PYTHON) -m stigaview_static -o $(OUT)/ products
	@$(CP) -r public_html/* $(OUT)/

sitemap:
	@$(FIND) "$(OUT)/" -name "*.html" > "$(OUT)/sitemap.txt"
	@$(SED) -i "s#out#https://stigaview.com#" "$(OUT)/sitemap.txt"
	@$(SED) -i "s#/index.html##" "$(OUT)/sitemap.txt"

test:
	@$(MYPY) -m stigaview_static
