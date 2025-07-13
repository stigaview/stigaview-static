RM = rm
MKDIR = mkdir
PYTHON = python
CP = cp
FIND = find

UNAME := $(shell uname)
ifeq ($(UNAME), Darwin)
SED = gsed
else
SED = sed
endif

OUT = out

.PHONY: all clean build copy_assets minify_static sitemap

all: build copy_assets minify_static sitemap

build:
	@$(RM) -rf $(OUT)
	@$(MKDIR) $(OUT)
	@$(PYTHON) -m stigaview_static -o $(OUT)/ products

copy_assets:
	@$(CP) -r public_html/* $(OUT)/

minify_static:
	@$(PYTHON) utils/minify.py --output_path $(OUT)/

sitemap:
	@$(FIND) "$(OUT)/" -name "*.html" > "$(OUT)/sitemap.txt"
	@$(SED) -i "s#out#https://stigaview.com#" "$(OUT)/sitemap.txt"
	@$(SED) -i "s#/index.html##" "$(OUT)/sitemap.txt"

clean:
	@$(RM) -rf $(OUT)
