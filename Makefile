build:
	rm -rf out
	mkdir out
	python -m stigaview_static -o out products
	cp -r static out/static
