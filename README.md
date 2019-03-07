# Mitrejse (Min Rejse)
-Your Personalized Rejseplanen

## Run on Debian (python3)
```
python3 -m venv  env
source env/bin/activate
pip install -r requirements.txt
python3 main.py
```

##Run on GAE
```
gcloud app deploy
```

##Run on Docker
```
git clone https://github.com/ribalda/mitrejse.git
cd mitrejse
docker build -t mitrejse .
docker run -p 8080:8080 -it --rm --name mitrejse mitrejse
```
