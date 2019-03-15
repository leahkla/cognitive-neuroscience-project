# Video Annotation Tool
This is a web app for measuring and analysing emotional reactions to videos.

While watching videos, people can indicate their emotional valence. In a seperate view for researchers, the answers people give can be analysed.

This software was written as part of the course _Data Science Project_ at the University of Helsinki in spring 2019.

## Installing required packages

With pip:

```
$ pip install -r requirements.txt
```

or with Anaconda:

```
$ conda install --yes --file requirements.txt
```

MongoDB is required by the app and needs to be installed separately. [Here](https://docs.mongodb.com/manual/administration/install-community/) are further instructions. MongoDB should be accessible at its default port when running.

## Running the app

Make sure MongoDB is running on your machine.

Then, to start the app, run: (see below for development/debugging mode)

```
$ export FLASK_APP=video_annotator.py

$ flask run
```
----------------
If you want to run the app in development mode, run this before starting the app:

```
$ export FLASK_ENV=development
```
(replace ``development`` with ``production`` for production mode)

If you want to switch debugging on, run this before starting the app:
```
$ export FLASK_DEBUG=true
```
(replace ``true`` with ``false`` to switch off debugging)

## Authors
* [Pihla Toivanen](https://github.com/UMTti)
* [Lea K](https://github.com/xtabentun)
* [Llode](https://github.com/Llode)
* [Moritz Lange](https://github.com/moritzlange)

## License
Published under the MIT license.
