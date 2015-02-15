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

Host your own instance on Heroku!
=================================


```
# Create an heroku app with this
$ heroku apps:create

# Add your API keys
$ heroku config:set SKETCHFAB_API_KEY=x SOCIAL_AUTH_FACEBOOK_KEY=x SOCIAL_AUTH_FACEBOOK_SECRET=x
$ heroku config:set BLENDER_PATH=build/blender-2.73a-linux-glibc211-x86_64/blender-softwaregl
# Add MongoDB & Redis (for storage & task queue)
$ heroku addons:add rediscloud
$ heroku addons:add mongolab
```

To test locally you can pull the config variables:

```
export MONGOLAB_URI=`heroku config:get MONGOLAB_URI`
export REDISCLOUD_URL=`heroku config:get REDISCLOUD_URL`
export SKETCHFAB_API_KEY=`heroku config:get SKETCHFAB_API_KEY`
export SOCIAL_AUTH_FACEBOOK_KEY=`heroku config:get SOCIAL_AUTH_FACEBOOK_KEY`
export SOCIAL_AUTH_FACEBOOK_SECRET=`heroku config:get SOCIAL_AUTH_FACEBOOK_SECRET`
```