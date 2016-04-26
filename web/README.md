# Documentation Greendoors Phonegap


## Contents
[Setup](#setup)

[Building](#building)

[Development](#development)

## Setup

### Install NPM
Platform specific. On Ubuntu use apt-get, on OSX use homebrew.

### Install Cordova
Tested with v3.0.1
```Bash
sudo npm install -g cordova 3.0.1
```

### Create a new project
```Bash
cordova create greendoors-app
cd greendoors-app
```
Add a new device (similar with iOS)
```Bash
cordova platform add android
cordova build
```

### Install Barcode Scanner Plugin
```Bash
git clone https://github.com/dschien/BarcodeScanner.git plugins/com.phonegap.plugins.barcodescanner
```
#### Install Cordova Plugin Mgr
```Bash
npm install -g plugman 0.9.11
plugman --plugins_dir plugins --plugin com.phonegap.plugins.barcodescanner --platform android --project platforms/android
```

### Checkout project sources
```Bash
git clone https://github.com/dschien/greendoors-phone.git
```

### Configure Project
```
cd greendoors-phone
```

You need grunt for build and development

####
```Bash
npm install -G grunt
```

Then install the grunt requirements. Also, dependency management is done with bower, which is installed as well.
```Bash
npm install
```

## Building

The dev dir is full of files we don't need, so we copy the files we do need over to the `./../www` directory.

```Bash
grunt copy:build
```

Now we can build. (replace [platform] which one of android or iOS).
```Bash
cd ..
cordova build [platform]
```

Now try installing it.
```Bash
adb install -r platforms/android/bin/<project-name>-debug.apk
```

## Development

### Dependencies
Use bower to fetch new dependencies, then use bower-installer to copy them into the `js/lib` folder.
```Bash
bower install [lib name]
bower-installer
```

### Grunt watch
During coding, use JSLint to check JS syntax and compile handlebars. This automated with grunt.
Keep a shell open with
```Bash
grunt watch
```


