sdist: doc
	python setup.py sdist

bdist_wheel: doc
	python setup.py bdist_wheel

clean: doc-clean
	@echo Removing binary files...
	@rm -f `find feedgen -name '*.pyc'`
	@rm -f `find feedgen -name '*.pyo'`
	@rm -rf feedgen.egg-info/ build/
	@echo Removing source distribution files...
	@rm -rf dist/
	@rm -f MANIFEST
	@rm -f tmp_Atomfeed.xml tmp_Rssfeed.xml

doc: doc-clean doc-html doc-man

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
	@cp -r doc/_build/html/ext/ docs/html/

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

publish:
	twine upload dist/*

test:
	coverage run --source=feedgen -m unittest discover -s tests
	flake8 $$(find setup.py tests feedgen -name '*.py')
	bandit -r feedgen
