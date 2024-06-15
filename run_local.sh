source ~/.virtualenvs/warp/bin/activate

export FLASK_APP=warp
export FLASK_ENV=development
export WARP_DATABASE=postgresql://warp:warp@localhost:5432/warp

# run the app
flask run # -h 10.25.41.75
