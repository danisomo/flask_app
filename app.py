from flask import Flask, escape, render_template, redirect, request
from elasticsearch import Elasticsearch
import urllib
import re

es = Elasticsearch('http://localhost:9200')

bbdd_selector=1
contador=0

app1_avg = Flask(__name__)

@app1_avg.route('/')
def bienvenido():
	return render_template('welcome.html')

@app1_avg.route('/graph')
def grafica():
	global contador
	contador=0
	return render_template("graficas.html")

@app1_avg.route('/main')
def index():
	global bbdd_selector
	global contador
	contador=contador+1
	if bbdd_selector:
		valor=0
		media=0
		flag_main=1
		res = es.search(index="test-index", body={'query':{'match_all':{}}})
		num_elementos=res['hits']['total']-1 # Hay uno menos de lo que devuelve
		for i in range(num_elementos):
			res = es.get(index="test-index", doc_type='cotizaciones_DJIA', id=i+1)
			valor=valor + float(res['_source']['cotiz_value'])
		if num_elementos==0:
			media=valor
		else:
			media= valor/num_elementos
			bbdd_selector=0
		print(contador)
		return render_template('mainpage.html', average = round(media, 2), bbdd = 'ElasticSearch', flag_main=1, mostrar=contador)
	else:
		data = urllib.request.urlopen("https://api.thingspeak.com/channels/919305/feeds.json?results")
		seleccion = repr(data.read())
		seleccion = seleccion[258:]
		data_filtered = re.findall('field1":"(.+?)"', seleccion) # Se obtiene lista de strings con valores de cotizaciones
		data_filtered = list(map(float, data_filtered)) # Convertir lista de strings en lista de floats
		media = sum(data_filtered) / float(len(data_filtered))
		bbdd_selector=1
		print(contador)
		return render_template('mainpage.html', average = round(media, 2), bbdd = 'ThingSpeak', flag_main=1, mostrar=contador)

@app1_avg.route('/consulta', methods=['POST'])
def consulta():
	umbral = float(request.form['umbral'])
	lista_valores=[]
	res = es.search(index="test-index", body={'query':{'match_all':{}}})
	num_elementos=res['hits']['total']-1 # Hay uno menos de lo que devuelve
	num_match=0
	for i in range(num_elementos, 0, -1): # range(m, n, p) empieza en m, acaba 1 antes de n y va de p en p
		res = es.get(index="test-index", doc_type='cotizaciones_DJIA', id=i)
		hora_actual=res['_source']['hour']		
		fecha_actual=res['_source']['date']
		valor_actual = float( res['_source']['cotiz_value'])
		if( valor_actual > umbral):
			if( num_match < 5):
				tupla=(valor_actual, fecha_actual, hora_actual)
				num_match=num_match+1
				lista_valores.append(tupla)
				if( num_match==5):
					return render_template('mainpage.html', thres = umbral, valores=lista_valores, flag_main=0, matches=num_match)
	return render_template('mainpage.html', thres = umbral, valores=lista_valores, flag_main=0, matches=num_match)

if __name__ == "__main__":
   app1_avg.run(host='0.0.0.0')