# Django SSL
* add `os.environ['HTTPS'] = "on"` to wsgi
* add
```
# SSL settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

For local dev create keys according to this:
[http://blog.andyhunt.info/2011/11/26/apache-ssl-on-max-osx-lion-10-7/]

make sure the cert name is identical to your (virtual) server name

## OAuth
[https://django-oauth2-provider.readthedocs.org/en/latest/getting_started.html#installation]
add installed apps
and `urls.py`

# Apache Conf

```
<VirtualHost *:80>
LogLevel info

Alias /static/ /Users/schien/sites/env/WWW/static
#       DocumentRoot "/Users/schien/sites/env/greendoors/greendoors/"
ServerName dgd
ErrorLog "/Users/schien/sites/logs/dgd-error_log"
CustomLog "/Users/schien/sites/logs/dgd-access_log" common
<Directory "/Users/schien/sites/env/WWW/static">
           Order deny,allow
           Allow from all
</Directory>

LogLevel info

WSGIDaemonProcess dgd.server processes=2 threads=15 display-name=%{GROUP} python-path=/Users/schien/sites/env/greendoors/lib/python2.7/site-packages:/Users/schien/sites/env/greendoors/greendoors
WSGIProcessGroup dgd.server
WSGIScriptAlias / /Users/schien/sites/env/greendoors/greendoors/greendoors/wsgi.py

<Directory "/Users/schien/sites/env/greendoors/greendoors/greendoors/">
           <Files wsgi.py>
                  Order allow,deny
                  Allow from all
           </Files>
</Directory>

RewriteEngine On
# This will enable the Rewrite capabilities

RewriteCond %{HTTPS} !=on
# This checks to make sure the connection is not already HTTPS

RewriteRule ^/?(.*) https://%{SERVER_NAME}/$1 [R,L]
# This rule will redirect users from their original location, to the same location but using HTTPS.
# i.e.  http://www.example.com/foo/ to https://www.example.com/foo/
# The leading slash is made optional so that this will work either in httpd.conf
# or .htaccess context

</VirtualHost>

 <VirtualHost *:443>
 SSLEngine on
 SSLCipherSuite ALL:!ADH:!EXPORT56:RC4+RSA:+HIGH:+MEDIUM:+LOW:+SSLv2:+EXP:+eNULL
 SSLCertificateFile /private/etc/apache2/ssl/server.crt
 SSLCertificateKeyFile /private/etc/apache2/ssl/server.key
 ServerName dgd

 LogLevel info
 Alias /static/ /Users/schien/sites/env/WWW/static/

 ErrorLog "/Users/schien/sites/logs/dgd-error_log"
 CustomLog "/Users/schien/sites/logs/dgd-access_log" common
 <Directory /Users/schien/sites/env/WWW/static>
            Order deny,allow
            Allow from all
 </Directory>
 DocumentRoot "/Users/schien/sites/env/WWW"
 LogLevel info

 #WSGIDaemonProcess dgd.server.ssl processes=2 threads=15 display-name=%{GROUP} python-path=/Users/schien/sites/env/greendoors/lib/python2.7/site-packages:/Users/schien/sites/env/greendoors/greendoors
 WSGIProcessGroup dgd.server
 WSGIScriptAlias / /Users/schien/sites/env/greendoors/greendoors/greendoors/wsgi.py

 <Directory "/Users/schien/sites/env/greendoors/greendoors/greendoors/">
            <Files wsgi.py>
                   Order allow,deny
                   Allow from all
            </Files>
 </Directory>

 </VirtualHost>
```

# OAuth

## Client ID generation
Use the admin interface or the command line:
```Python
>>> from provider.oauth2.models import Client
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(id=1)
>>> c = Client(user=u, name="mysite client", client_type=1, url="http://ianalexandr.com")
>>> c.save()
>>> c.client_id
'd63f53a7a6cceba04db5'
>>> c.client_secret
'afe899288b9ac4127d57f2f12ac5a49d839364dc'

```

Then get an oauth token.
E.g.

curl -X POST -d "client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=password&username=YOUR_USERNAME&password=YOUR_PASSWORD" http://localhost:8000/oauth2/access_token/
curl -k -X POST -d "client_id=bfad28d8534d3b71eb88&client_secret=08c740d526a438b66cdd3adf30d06d85b42ee315&grant_type=password&username=XXXXXX&password=XXXXXXXXX&scope=write" https://dgd/oauth2/access_token

## REST FW Authentication

     'DEFAULT_AUTHENTICATION_CLASSES': (
         # for web auth
         'rest_framework.authentication.BasicAuthentication',
         # for oauth
         'rest_framework.authentication.OAuth2Authentication',
     ),

### Test on cmd line
```Bash
curl -k -H 'Accept: application/json; indent=4' -u UNAME:PASS https://dgd/api/v1/users/
```

or for OAuth:

```Bash
curl -k -v -H "Authorization: OAuth AUTHTOKEN" -H "Accept: application/json; indent=4" https://dgd/api/v1/users/
```



## AJAX Content Types
* For the access_token method the OAuth client looks for parameters in requets.POST. This is only filled with form data (i.e. of the form key=value&nextkey=nextValue....)
 Sending in JSON format  (ajax.contentType:'json') however, is made availabe in the request.body.
  Hence, you cannot use JSON by default.


## OAuth email
* create new  Client ID for installed applications
run
`python oauth2.py --generate_oauth2_token --client_id=<XXX> --client_secret=<XXX>`
from [https://code.google.com/p/google-mail-oauth2-tools/wiki/OAuth2DotPyRunThrough]

# Deployment

## Import measure categories
```Bash
./manage.py import_jsondata -f data/jsondata/measureCategories.json -m api.models.MeasureCategory
```

## Import house data from template
```Bash
./manage.py import_exceldata -f data/Template_v2.3.xlsx -m -b
```

## Import images
```Bash
./manage.py import_images -d data/img/unprocessed
```

### Example bristol2014
```Bash
./manage.py import_jsondata -f data/jsondata/measureCategories.json -m api.models.MeasureCategory

./manage.py loaddata api/fixtures/initdata_server.json

./manage.py import_jsondata -f data/jsondata/measureCategories.json -m bristol2014.models.MeasureCategory

./manage.py import_model_from_excel -f bristol2014/data/Template_v1.0.5.xlsx -a bristol2014 -m Area,Construction,Age,Time,Type

./manage.py import_template_data -f bristol2014/data/Template_v1.1.4.xlsx -m -g -a bristol2014 -b -c -e
```



# South
When starting with a new model run
```Bash
./manage.py schemamigration web --initial
```
to initialise migrations

Only then, run `syncdb`.

When this is complete perform migrations:
```Bash
./manage.py migrate
```

After changes have been made run:

```Bash
./manage.py schemamigration api --auto
```


# URLs

The API urls are versioned. Each version only needs to override those urls that change and import others from the default.

# Testing
For local testing of oauth2 token access functions, the server needs to run on https.
There is an app that does that [https://github.com/teddziuba/django-sslserver]


In order to create a custom certificate follow this guide [http://blog.andyhunt.info/2011/11/26/apache-ssl-on-max-osx-lion-10-7/]

Basically do:
```Bash
sudo ssh-keygen -f server.key

sudo openssl req -new -key server.key -out request.csr

sudo openssl x509 -req -days 365 -in request.csr -signkey server.key -out server.crt

```

Then run the local server:
```Bash
python manage.py runsslserver --certificate ../ssl_cert/server.crt --key ../ssl_cert/key.key
```

*Doesn't work*

Then accept the certificate permanently in your browser - or accept once per session.

# Data Templates
The excel template is imported through a management command. Check respective README.

# Deployment
1. Create DB 'greendoors' with user
2. `./manage.py syncdb`
3. `./manage.py migrate`
4. `import_jsondata -f data/jsondata/measureCategories.json -m api.models.MeasureCategory`
    to import MeasureCategory for each app:
    `./manage.py import_jsondata -f data/jsondata/measureCategories.json -m south_wiltshire_2014.models.MeasureCategory`
    `./manage.py import_jsondata -f data/jsondata/measureCategories.json -m frome2014.models.MeasureCategory`
    etc
5. `import_exceldata -f data/Template_v3.0.7_dev.xlsx -m -b -c -e -g`
    to import bristol data inclusive measures
    and set all closed
5.1 import images to bristol houses
    `import_images -d data/img/unprocessed`
6. `./manage.py import_frome_exceldata -f frome2014/data/Template_v1.1.3.xlsx -m -b -g`
    to import frome data, which depends on measurecateogries and measures already installed
