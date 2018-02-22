FROM continuumio/anaconda3
MAINTAINER "Davy Cielen"

#create files
RUN apt-get update && apt-get install -y python-pip python-dev && apt-get clean
#update pip
ADD requirements.txt  /home/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /home/requirements.txt


#packages
#RUN pip install pandas
#RUN pip install requests
#RUN pip install  --upgrade google-cloud-bigquery
#RUN pip install --upgrade pandas-gbq
#RUN pip install lxml
#RUN pip install beautifulsoup4
