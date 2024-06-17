#!/usr/bin/env bash
source /opt/$VENV_NAME/bin/activate 

rm -rf ./functions/data_refresh_py_files
rm ./functions/data_refresh_py.html
quarto render ./functions/data_refresh_py.qmd --to html

rm -rf docs/data_refresh/
mkdir docs/data_refresh
cp ./functions/data_refresh_py.html ./docs/data_refresh/
cp -R ./functions/data_refresh_py_files ./docs/data_refresh/

echo "Finish"
p=$(pwd)
git config --global --add safe.directory $p


# Render the Quarto dashboard
if [[ "$(git status --porcelain)" != "" ]]; then
    quarto render functions/index.qmd
    cp functions/index.html docs/index.html
    rm -rf docs/index_files
    cp -R functions/index_files/ docs/
    rm functions/index.html
    rm -rf functions/index_files
    git config --global user.name $USER_NAME
    git config --global user.email $USER_EMAIL
    git add data/*
    git add docs/*
    git commit -m "Auto update of the data"
    git push origin main
else
echo "Nothing to commit..."
fi