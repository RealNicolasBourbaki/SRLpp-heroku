# SRLpp
Annotation tool for SRL++ (paper link here).

### Manual 

#### Before everything starts, make sure you have Python3 installed.

#### 1.Choose your working directory and downlod the code
-  1.1 Go to some directory where you desire to work on, let's call it ```[work_dir]``` for now.
```
cd [work_dir]
``` 
-  1.2 download this ```SRLpp-main``` directory from github in your ```[work_dir]```, remember to unzip the whole folder..

**(Important: because the current SRLpp annotation tool is frequently updated, in order to save your trouble with all the repetitive installation, I highly suggest that you clone the folder instead of directly downloading. This is a temporary solution during the development phase. But if you did clone it, please notice that the cloned folder is named "SRLpp" instead of "SRLpp-main")**

====================================================================


#### 2. Install (For Linux system)

We need to install the correct version of ```sqlite3```, ```graphviz``` and ```Django```: 

- 2.1 For people who already have ```sudo``` right:

```
sudo apt-get install sqlite3
sudo apt-get install graphviz
```

For ```sqlite3```, officially we are using version 3.29.0 but technically any version equal or later than 3.8.3 whould do. For GraphViz, we are using 2.47.0. If you are sure you have it already and can get it work perfectly, then just install Django:
```
cd [work_dir]/SRLpp-main
virtualenv -p python3 srlpp_venv
cd srlpp_venv
source bin/activate
python3 -m pip install Django==3.1.7
python3 -m pip install networkx==2.5
python3 -m pip install matplotlib==3.3.4
python3 -m pip install pydot==1.4.2
```

-  2.2 For people who do not have ```sudo``` right (Or you are just not sure):

```
cd [work_dir]/SRLpp-main
bash install.bash
```
This will create a virtual environment so your other projects will be safe, and install the correct version of ```sqlite3``` locally.
And you are done.


====================================================================

#### 3. Migrate the data base
After step2 you should have already created a virtual environment. if it is not activated, go there and activate it. If you are not sure if the virtual environment is already activate or not, do it anyways. It would not hurt.
```
cd [work_dir]/SRLpp-main/srlpp_venv
source bin/activate
```
Go to [work_dir]/SRLpp-main/SRLpp/, and run manage.py shell by doing:

-- The following extra lines are only for people coming from step 2.2:
```
cd [work_dir]/SRLpp-main/
WRK_DIR=$PWD
SITE_PKG=$WRK_DIR/site-packages

export PATH=$SITE_PKG/bin:$PATH
export LD_LIBRARY_PATH=$SITE_PKG/lib
```

-- The following lines are necessary for all people regardless what you did in step 2:
```
cd [work_dir]/SRLpp-main/SRLpp
python3 manage.py migrate
python3 manage.py shell
```
It should initialize an empty database and open a shell terminal for you.

Then go to ```[work_dir]/SRLpp-main/SRLpp/db/admin_manage_catalogue_entries.py```, copy the whole content of ```admin_manage_catalogue_entries.py```, and paste it in the shell terminal.

then type ```exit()``` to exit from this terminal.

And you have successfully migrated the data base and added all entries into it!

====================================================================


#### 4. Run the app
- 4.1 If you are from step 2.1:
```
cd [work_dir]/SRLpp-main
cd srlpp_venv
source bin/activate
cd [work_dir]/SRLpp-main/SRLpp
python3 manage.py runserver
```
Then open your browser, type in: ```http://127.0.0.1:8000```

And here you go

- 4.2 If you are from step 2.2:
```
cd [work_dir]/SRLpp-main
bash start.bash
```
Then open your browser, type in: ```http://127.0.0.1:8000```

And here you go

