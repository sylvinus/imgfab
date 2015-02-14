imgfab
======

Because your Facebook photos are so 2D!

How it works:

 - Facebook connect => List of images & descriptions from a user, saved as JSON
 - Download all the images in the directory, replace the URLs in the JSON file
 - `create_model.py`: creates a blender model from a directory
 - `upload_to_sketchfab.py`: uploads the blender model to http://sketchfab.com


TODO
====

 - JSON spec
 - Image downloader
 - Multiple files
 - Adapt plane size to the photo ratio
 - Multiple layouts
 - Background image
 - FB connect