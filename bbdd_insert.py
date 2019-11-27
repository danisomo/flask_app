from bs4 import BeautifulSoup
import requests
import re
import time
import urllib.request
from elasticsearch import Elasticsearch

es = Elasticsearch('http://localhost:9200')
url = 'https://quotes.wsj.com/index/DJIA'
i=1

while True:
    # Make an HTTP request to get HTML content via the specific URL.
    response = requests.get(url)
    soup = BeautifulSoup(response.content,"html.parser")
    span = str(soup.find('span', {'id':'quote_val'}))
    cotizacion=span[21:29]
    span2 = str(soup.find('span', {'id':'quote_dateTime'}))
    hora=span2[50:58]
    fecha=span2[62:70]
    print(cotizacion, hora, fecha)

    # Introducir datos en Thingspeak
    url2 = "https://api.thingspeak.com/update?api_key=OKO3M7X2NTX6BSRT&field1=%s" \
    % (cotizacion)
    datos = urllib.request.urlopen(url2)
    datos.close()

    # Introducir datos en elasticsearch

    # Creación de diccionario generado con los datos extraídos de la página web
    doc={
    "cotiz_value": cotizacion,
    "hour": hora,
    "date": fecha,
    }

    # Inserto el diccionario generado con los datos extraídos de la página web (i es el id del documento)
    res = es.index(index='test-index', doc_type='cotizaciones_DJIA', id=i, body=doc)

    # Imprimo dato del id almacenado correspondiente
    res = es.get(index="test-index", doc_type='cotizaciones_DJIA', id=i)

    i=i+1
    time.sleep(10)