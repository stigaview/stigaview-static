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

.PHONY: clean build copy_assets sitemap

all: build copy_assets sitemap

build:
	@$(RM) -rf $(OUT)
	@$(MKDIR) $(OUT)
	@$(PYTHON) -m stigaview_static -o $(OUT)/ products


copy_assets:
	@$(CP) -r public_html/* $(OUT)/

sitemap:
	@$(FIND) "$(OUT)/" -name "*.html" > "$(OUT)/sitemap.txt"
	@$(SED) -i "s#out#https://stigaview.com#" "$(OUT)/sitemap.txt"
	@$(SED) -i "s#/index.html##" "$(OUT)/sitemap.txt"

clean:
	@$(RM) -rf $(OUT)
