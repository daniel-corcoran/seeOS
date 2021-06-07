/modules/readme.txt
Written by Dan C on Thu, Jun 3 2021

Welcome to modules

Modules is a subdirectory of seeOS that contains the general system fuctions,
differentiated by their general purpose (you can see that in the file names).

For example, LED.py contains functions to do LED stuff. buzzer.py contains buzzer stuff
camera.py contains camera stuff.

In my opinion, camera.py is the most interesting file here so please check that out if
you're just curious about the code.

By the way, modules are called by the boot.py program during startup and remain loaded
during the entire OS runtime. This is opposed to the program class, which can be loaded and unloaded
as a dynamic python module. Nope, these bad boys can't leave (and that's the way it should be!)

There's a lot of room for improvement here as I haven't had time to give them all the attention they
deserve, but if you're looking for something to do...

switch.py - How do we switch the application without restrarting the device? This is critical.
camera.py - How do we mantain concurrency between the applications and the camera, in real-time
fasion?

