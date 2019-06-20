# Catalog project 

Welcome to my fully functioning catalog app, sans a working style sheet, but since I'm really late and in jeopardy of finishing this nano-degree I'll submit!

The Catalog application displays a list of Categories, Items for each category, allows for adding and editing items, and uses authentication to protect pages. 

This program was run using Virtual Box, Vagrant, SQLAlchemy, Flask

1) Installing Virtual Box
VirtualBox is the software that actually runs the virtual machine. You can download virtualbox at the following   https://www.virtualbox.org/wiki/Download_Old_Builds_5_1
Install the _platform package_ for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

2) Installing Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. Download it from this link:https://www.vagrantup.com/downloads.html

**Windows users:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

If Vagrant is successfully installed, you will be able to run 'vagrant --version' in your terminal to see the version number.

3) Place the files from the zipped project file into your /vagrant directory.
You should have a /templates directory with all the form files.
You shoudl also have a /static directory with styles.css.


4) Start the virtual Machine
From your terminal, inside the **vagrant** subdirectory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. 
When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM!

5) Database
The zipped project files indcludes the database catalogapp.db
The database can be recreated running "python databasesetup.py", this creates catalogapp database file.
The initial categories, a user, and one item can be created by running "python adddefaultcategory.py"

6) Run the program
Once you have Virtual Box, Vagrant running, the VM downloaded and started, and the data created, you can run the run the python program. 
To run the program use: "python application.py"

7) User Authentication
Please test Authentication using the following two Facebook test accounts.  After logging in with one account and makeing updates and logging out of the catalog app you may need to go to facebook and log out of the test account before logging in to the second test account.

Samantha Alcggddfbgcgc Sharpeberg 
facebook_id: 100037744627373 
logon/email: ovcndfbfvm_1559769344@tfbnw.net 
password: udacity1

Linda Alcgfbhgghdia Smithsen 
facebook_id: 100037628778491 
logon/email: dhslhhrbpt_1559922921@tfbnw.net 
password: udacity2

8) Editing content
Create, Delete and Edit are protected by login, Delete and Edit are checked so that only the user that created the item can Delete/Edit the item.

9) Styles
Sorry, I can't figure out why my stylesheet isn't working!

10) Pages
Show categories - /catalog or /
Show items for category - /catalog/<int:category_id>/items
Show an item - /catalog/<int:item_id>
Create new item - /catalog/item/new
Delete an item - /catalog/<int:item_id>/delete
Edit an item - /catalog/<int:item_id>/edit

11) JSON endpoints
/catalog.json - displays all the categories and all the items
/catalog/item/#/JSON - returns a single item
/catalog/category/#/JSON - returns a single category





