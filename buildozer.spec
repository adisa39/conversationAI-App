[app]
# (str) Title of your application
title = ChatDocApp

# (str) Package name
package.name = chatdocapp

# (str) Package domain (unique identifier)
package.domain = org.yourdomain

# (str) Source code where the main.py live
source.dir = .

# (str) Source code directory (default: current directory)
source.include_exts = py,png,jpg,kv,atlas,env,pdf,sqlite3

# (list) Application requirements
# Here are the necessary libraries for Kivy, KivyMD, and other Python modules.
requirements = python3,kivy==2.2.1,kivymd==1.2.0,pyjnius,openai,langchain==0.2.1,langchain_community==0.2.1,python-dotenv==1.0.1,chromadb,pypdf,Requests==2.32.2,typing-extensions,pydantic,httpx,sniffio,httpcore,h11,anyio,distro

# (str) Icon of your application (256x256 png file)
#icon.filename = icons/app_icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (list) Permissions required by your application
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (str) Your application's entry point.
# This is the main Python file of your app.
entrypoint = main.py

# (list) Android archs to build for
# Supported values are: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = armeabi-v7a, arm64-v8a

# (str) Android packaging options
# Change this to "release" for production builds.
android.debug = 1

# (str) Android minimum SDK version
android.minapi = 21

# (str) Android SDK version used to compile the app
android.sdk = 31

# (str) Android NDK version used to compile the app
android.ndk = 25b

# (bool) Enable android logcat output during application run
logcat = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (str) Path to a custom build directory
# build_dir =

# (str) Presplash screen of your application (optional)
# presplash.filename =

# (str) Android presplash background color (for example #FFFFFF)
# presplash.color =

# (str) The .java files will be copied into this directory
# (default: src)
# android.additional_jars =

# (bool) Indicate if the build should include the icons in the package
# android.include_icons = True

# (str) The version number of your application
version = 0.1

# (list) View options in the application
# android.meta_data = {'android.max_aspect': '2.1'}

# (str) The name of the packaged application file (.apk)
# android.package_file_name =

# (str) Android application category
# android.category =

# (str) Android application description
# description =

# (str) Add custom arguments for buildozer
# buildozer.custom_args =

# (str) The main .py file for your application
main = main.py

# (str) Add any other source files needed in the final package
# source.include_patterns =

# (list) Additional source dirs to include in the package (not recursive)
# source.include_exts =

# (list) List of directories to be excluded from the package
# source.exclude_exts =

# (bool) Whether to copy the source files to the build directory before packaging
# copy_source = True

# (str) Kivy version used to package the app (required for buildozer)
kivy_version = 2.2.1

# (list) Android Java classes to be included in the final package
# java.classes =

# (list) Android .so files to be included in the final package
# android.add_libs_armeabi_v7a =

# (str) Signature information for signing the package (for release builds)
# key.store = mykeystore
# key.alias = mykeyalias
# key.store_pass = password
# key.alias_pass = password

# (bool) Enable fullscreen mode
fullscreen = 1

# (bool) Disable the title bar of the application window
window = 1

# (list) Compile the application using Kivy, KivyMD, and the specified Python version
android.python3 = True

# (bool) Include the SQLite3 module in the package
sqlite = True

# (str) Application platform options
# platform.android = True

# (str) Specify buildozer settings
# buildozer.spec =

# (bool) Force a clean build (delete build directory)
# clean_build = True

# (list) Additional Android dependencies
# android.dependencies =

# (str) The extra modules for the build process
# python.modules = 

# (str) Build tools for the application
# buildtools =

# (bool) Allow the application to run in debug mode
debug = True

# (str) Android application permissions
# permissions =

# (list) Android additional activities to be included in the package
# android.additional_activities =

# (list) Android services to be included in the package
# android.additional_services =

# (bool) Allow access to the internet
internet = True

# (str) Enable video for the package
# video = True

# (str) Additional files to be included in the package
# include_patterns =

# (str) Application crash report URL
# report_crash_url =

# (str) Enable logging for the package
# log =

# (list) List of Java classes to be included in the package
# classes =

# (str) Android application permissions
# android_permissions =

# (list) Additional Android modules to be included in the package
# android.modules =

# (str) Build options for the package
# build_options =

# (list) Python modules to be excluded from the package
# exclude_modules =

# (list) Python modules to be included in the package
# include_modules =

# (bool) Skip the compilation of certain modules
# skip_modules =

# (bool) Disable file monitoring for buildozer
# disable_filemon = True

