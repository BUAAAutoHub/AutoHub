rm -f db.sqlite3
rm -rf myApp/migrations/*
rm -rf userRepos/*
touch myApp/migrations/__init__.py
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py rebuilddb
