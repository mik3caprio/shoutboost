# shoutboost

Submit, discover, curate, and promote breaking news videos across social platforms

DEVELOPER SETUP
===============

Install and set up git and Python 2.7.x at a minimum to get started. Using 
[Homebrew](http://brew.sh/) is highly recommended if you're developing on Mac 
OS; just run the Install Homebrew line at the site in the prior link. Read and 
follow any instructions Homebrew gives you during install, like installing the 
Xcode command line tools. Eventually you can run 

    $ brew doctor

And then you can install git and python (which should install pip)

    $ brew install git
    $ brew install python

Also recommend installing and running virtualenv for Python (you may also
need to install pip).

    $ pip install virtualenv

After you've installed git, you should follow the [instructions for setting up
an SSH key](https://help.github.com/articles/generating-ssh-keys/). Clone the 
repository when you're ready to get started.

    $ git clone [this repo]

Create a virtualenv outside of the git repo directory and run the source
command to activate it

    $ virtualenv sb_dev_env
    $ source sb_dev_env/bin/activate

Run the requirements.txt in the repository within your Python
virtualenv using:

    $ pip install -r requirements.txt

You can now run the application by entering the command

    $ python sample_app.py
