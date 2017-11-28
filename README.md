# mitrejse
Your Personalized Rejseplanen

## Run on Debian (python3)
apt-get install python3-webpy python3-dateutil python3-requests
git clone git@github.com:ribalda/mitrejse.git
cd mitrejse
python3 mitrejse.py
[Open localhost:8080 on your favorite browser]

## Docker run
git clone git@github.com:ribalda/mitrejse.git
docker build -t mitrejse .
docker run -p 8080:8080 -it --rm --name mitrejse mitrejse
[Open localhost:8080 on your favorite browser]

## crontab (python v2)
apt-get install python-webpy python-dateutil python-requests
cd ~
git clone git@github.com:ribalda/mitrejse.git
cd mitrejse
crontab -e
[add the following line]
@reboot /home/ricardo/mitrejse/init.sh

