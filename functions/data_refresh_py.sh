#!/usr/bin/env bash
source /opt/$VENV_NAME/bin/activate 

rm -rf ./python/data_refresh_py_files
rm ./python/data_refresh_py.html
quarto render ./python/data_refresh_py.qmd --to html

rm -rf docs/data_refresh_python/
mkdir docs/data_refresh_python
cp ./python/data_refresh_py.html ./docs/data_refresh_python/
cp -R ./python/data_refresh_py_files ./docs/data_refresh_python/

echo "Finish"
p=$(pwd)
git config --global --add safe.directory $p



if [[ "$(git status --porcelain)" != "" ]]; then
    quarto render python/index.qmd
    cp python/index.html docs/index.html
    rm -rf docs/index_files
    cp -R python/index_files/ docs/
    rm python/index.html
    rm -rf python/index_files
    git config --global user.name $USER_NAME
    git config --global user.email $USER_EMAIL
    git add csv/*
    git add metadata/*
    git add docs/*
    git commit -m "Auto update of the data"
    git push origin main
else
echo "Nothing to commit..."
fi