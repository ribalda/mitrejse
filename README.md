# mitrejse
Personalized Rejseplanen

## Run on Debian
apt-get install python-webpy python-dateutil python-requests
cd ~
git clone git@github.com:ribalda/mitrejse.git
cd mitrejse
python mitrejse.py
[Open localhost:8080 on your favorite browser]

## crontab (once previous step works)
crontab -e
[add the following line]
@reboot /home/ricardo/mitrejse/init.sh

## Docker run
git clone git@github.com:ribalda/mitrejse.git
docker build -t mitrejse .
docker run -p 8080:8080 -it --rm --name mitrejse mitrejse
[Open localhost:8080 on your favorite browser]

