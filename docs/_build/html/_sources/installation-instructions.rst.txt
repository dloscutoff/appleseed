
Installation and use
=========================

First things first: to run Appleseed code without installing anything, head over to `Try It Online`_.

If you want to use the REPL, though, you'll need to ``git clone`` a local copy of the repository.

In Bash or Git Bash::

   git clone https://github.com/dloscutoff/appleseed.git

Alternately, in Windows using Git GUI, right-click a folder and select Git GUI Here from the context menu. Choose Clone Existing Repository, enter ``https://github.com/dloscutoff/appleseed.git`` as the Source Location, and enter the path of a folder to create as the Target Directory. Click Clone to create your local copy.

If you're on Windows and don't have Python 3 installed, download and install it from `Python's website <https://www.python.org/downloads/>`_.

Now open a command shell, navigate to the directory Appleseed is in, and type ``./appleseed`` (Linux) or ``appleseed.py`` (Windows). You should see a welcome message and REPL prompt, something like this::

   Appleseed 0.0.3
   Type (help) for information
   Loaded library.asl
   asl> 

To run a file instead of the REPL, specify the filename as a command-line argument to the interpreter: ``./appleseed file.asl`` (Linux) or ``appleseed.py file.asl`` (Windows). Or, you can pipe code in on stdin: e.g., ``cat file.asl | ./appleseed`` (Linux) or ``type file.asl | appleseed.py`` (Windows).

.. _Try It Online: https://tio.run/##DcjBDYAgDAXQu1MUTjRxEDfwXNNvYlKBQOP6lXd80rthAhpRFDdNl@FpIyom76VCBR@q85p1fTzVE@UDZm2nsw3TlJk54gc