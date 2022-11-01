RosterSniper Development Environment Setup
Utilised by Three Muskeeters+1 for development in Fall2022

Please ensure you have Python 3.8 (or higher), and Git installed before continuing.

First. This guide is divided into several "Checkpoints" based upon key areas of the process.
If you are stuck, double check you have done everything in prior categories.

## `Git & Local Repository Setup`

Open open Git and navigate to your preferred repo storage location.
```
cd "preferred\project\storage\location"
```
Please do not create a new folder titled "RosterSniper" to store the project in. If you have not used `git clone` before,
it will automatically create a new folder with the same name as the github repo. 
Furthermore, it is highly recommended you do not store your repo inside of OneDrive, or any other cloud service.
It may be acceptable for smaller projects, but speaking from the experience of Joseph, suddenly dumping 40k files onto 
your OneDrive (most coming from the libraries), is not fun to deal with the aftermath of.

Regardless, once you have navigated to the preferred folder, in Git:
```
git clone "repoURL"
cd rostersniper
git init
```

## Venv Setup

If you have PyCharm Community Edition, opening the main RosterSniper folder as a project should have it automatically create a venv.
If not, open command prompt:
```
cd "YOUR/STORAGE/PATH/RosterSniper/"
python -m "PATH/TO/STORAGE/RosterSniper/venv"
```
This should create a new venv folder.

## PyCharm Setup

Pycharm Community Edition can be utilized as the command prompt for the venv, but it requires some ExecutionPolicy changes for the scripts to work.
Skip to `LOCALHOST SETUP` if you prefer the standard command console.

Open PyCharm, then the Terminal tab at the bottom.
You should notice it saying something along the lines of
".\RosterSniper\venv\Scripts\activate.ps1 cannot be loaded because running scripts is disabled on this system."

```
Get-ExecutionPolicy -List
```
This will show the current executionpolicies, it should be undefined for all unless you've edited them before.

Now, if you can deal with doing this everytime you open PyCharm:
```
Set-ExecutionPolicy -Scope Process unrestricted
.\venv\Scripts\activate.ps1
```
This will allow the script to run once and then reset the policies upon closing the program.

If you want it to automatically run every single time you open PyCharm,
I would highly recommend checking out https:/go.microsoft.com/fwlink/?LinkID=135170 first.
However, if you don't care about potential issues that may or may not be present:
```
Set-ExecutionPolicy -Scope CurrentUser unrestricted
Set-ExecutionPolicy -Scope CurrentUser undefined (to undo it)
```

## LOCALHOST SETUP

Activate the venv then navigate to the main rostersniper folder:
```
python pip install -r requirements.txt
cd django_project
python manage.py migrate
python manage.py loaddata --app core schools.json
python manage.py update_terms
python manage.py update_sections
```
The update_sections command will take a minute, but once it is done:
```
python manage.py runserver
```
Open your preferred browser, url localhost:8000
