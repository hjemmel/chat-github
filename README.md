chat-github
===========

Chat for Github

### pre-requisites
	
+ install, configure and active virtualenv
+ xcode installed, go (command + ,) -> Download -> Components. Verify if Command line Tools is installed, if not install.

dependencies:

	django==1.4
	unipath==0.2.1
	psycopg2
	django-social-auth
	pygithub
	South==0.7.5
	django-nose
	git+https://github.com/jandersonfc/django-tastypie.git
	django-jenkins
	pep8
	pyflakes

install dependencies using pip:

	pip install -r requirements.txt

### Custom Command dblocal

execute command syncdb to create tables of modules and in case of chat are using South, so execute migrate and schemamigrations

	python manage.py dblocal

### Set Dev environment

runserver using settings.dev (sqlite and github application of test)

	python manage.py runserver --settings=settings.dev

or set environment variables 

	export DJANGO_ENV=DEV

and execute only command runserver

	python manage.py runserver


### Uglifying file javascripts

to uglify the files javascripts is necessary:

install node.js (http://nodejs.org/)

install plugin of require in node
	
	npm install -g requirejs

execute in root the project(via terminal):

	r.js -o public/js/app/app.build.min.js 

done.

	
