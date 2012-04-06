# Updating Rascal to the latest control-freak Release

Release of Mar 29, 2012

The main changes in this release are:

  * Editor window can be resized
  * View image files in editor
  * File tree can be scrolled
  * Drag and drop files or folders in file tree
  * Drag file from desktop to file tree. Allowed types are image, html, css,
javascript and python
  * Create new folder
  * On Mac, Command-S saves file (in addition to Ctrl-S and the Save button)

There are also some new demos and the option of using the ACE editor instead
of CodeMirror.

To update to the latest release, proceed as follows, replacing NN with your Rascal's serial number:

  1. Log in to your Rascal:
  
        $ ssh root@rascalNN.local
        root@rascalNN.local's password:
  
  2. Change to the /var/ directory:
  
        [root@rascalNN:~]: cd /var/
  
  3. Rename the existing www/ directory:
  
        [root@rascalNN:/var]: mv www www_previous
  
  4. Clone the latest control-freak to the www/ directory:
  
        [root@rascalNN:/var]: git clone git://github.com/rascalmicro/control-freak.git www
        Cloning into www...
        ...
        Resolving deltas: 100% (582/582), done.

  5. Install CodeMirror:
  
        [root@rascalNN:/var]: cd www/
        [root@rascalNN:/var/www]: git submodule
        9d621390c80ac7cac6e9e3660162fd891a8c914e editor/static/codemirror2 (v2.22-56-g9d62139)
        [root@rascalNN:/var/www]: git submodule init
        Submodule 'editor/static/codemirror2' (git://github.com/marijnh/CodeMirror2.git) registered for path 'editor/static/codemirror2'
        [root@rascalNN:/var/www]: git submodule update
        Cloning into editor/static/codemirror2...
        ...
        Submodule path 'editor/static/codemirror2': checked out '9d621390c80ac7cac6e9e3660162fd891a8c914e'

  6. Restart both web servers:
  
        [root@rascalNN:/var/www]: cd /etc/uwsgi/
        [root@rascalNN:/etc/uwsgi]: touch editor.ini 
        [root@rascalNN:/etc/uwsgi]: touch public.ini 
        
At this point the editor should work and you should be able to view simple web pages:

        http://rascalNN.local/hello.html

### New Demos

**Hello** - hello world for Rascal (displays message, flashes LED). See [hello
world][1] for more info.

**Upload CF** - upload image files using Choose File dialog  
**Upload DD** - upload image files using drag and drop from desktop

> _- before running the above, use the Create Folder icon to create a
directory static/uploads/_

**Album** - upload image files using drag and drop and view as picture album

> _- before running album, use the Create Folder icon to create a directory
static/pictures/_

### ACE Editor

If you want to try the ACE Editor (see editor config page for details), you
need to do the following:

  1. Create a directory editor/static/ace/
  2. Copy the ACE build/ directory there (only the build directory is required)
  3. Tested with ACE 2011.08.02, Version 0.2.0.
  4. Choose between CodeMirror and ACE on the editor config page

### Other Demos

**email** - send email message via external SMTP server (requires ds_mail.py)

**scope** - simulated scope with UTC time, current temperature and LED status
(requires TMP102 temperature sensor connected to Rascal I2C/TWI bus and
ds_temp.py)

dsmall 6 Apr 2012

   [1]: http://blog.hlh.co.uk/2012/02/07/hello-world-2/