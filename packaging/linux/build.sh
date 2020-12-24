# Build a Wingman distribution on Unix.

# cd to project root
cd ../..

# clean up from previous builds
python setup.py clean
rm dist/*

# ensure resources are up to date
pyrcc5 src/resources.qrc -o src/wingman/resources.py

# create dummy files so that pip will delete the real things on uninstall
# unfortunately there's no way to do this for directories, so these will remain
cp src/default.cfg wingman.cfg
touch wingman.log

# actually build the distribution. Building a wheel breaks several options in
# setup.py which is why sdist is used
python setup.py sdist

# delete dummy files
rm -r wingman.cfg wingman.log
