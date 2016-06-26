sdist: doc
	python setup.py sdist

clean: doc-clean
	@echo Removing binary files...
	@rm -f `find feedgen -name '*.pyc'`
	@rm -f `find feedgen -name '*.pyo'`
	@echo Removing source distribution files...
	@rm -rf dist/
	@rm -f MANIFEST
	@rm -f tmp_Atomfeed.xml tmp_Rssfeed.xml

doc: doc-clean doc-html doc-man doc-latexpdf

doc-clean:
	@echo Removing docs...
	@make -C doc clean
	@rm -rf docs

doc-html:
	@echo 'Generating HTML'
	@make -C doc html
	@mkdir -p docs/html
	@echo 'Copying html to into docs dir'
	@cp doc/_build/html/*.html docs/html/
	@cp doc/_build/html/*.js docs/html/
	@cp -r doc/_build/html/_static/ docs/html/

doc-man:
	@echo 'Generating manpage'
	@make -C doc man
	@mkdir -p docs/man
	@echo 'Copying manpage to into docs dir'
	@cp doc/_build/man/*.1 docs/man/

doc-latexpdf:
	@echo 'Generating pdf'
	@make -C doc latexpdf
	@mkdir -p docs/pdf
	@echo 'Copying pdf to into docs dir'
	@cp doc/_build/latex/*.pdf docs/pdf/

publish: sdist
	python setup.py register sdist upload

test:
	python -m unittest feedgen.tests.test_feed
	python -m unittest feedgen.tests.test_entry
	python -m feedgen rss > /dev/null
	python -m feedgen podcast > /dev/null
	@rm -f tmp_Atomfeed.xml tmp_Rssfeed.xml
