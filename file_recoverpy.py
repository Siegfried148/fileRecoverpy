#!/usr/bin/python
# -*- coding: utf-8 -*-
#Castro Rendón Virgilio
#File Recoverpy v1.0
from datetime import datetime #Será útil cuando se implemente la generación de reportes
import sys
import optparse
import os


#Cabeceras y "pies" de los diferentes tipos de archivo
#Si no tiene un footer, es nulo y el tamaño se determinará por un límite arbitrario
headers = {'jpg':['ff','d8','ff'],
	'jpeg':['ff','d8','ff'],
	'png':['89','50','4e','47'],
	'gif':['47','49','46','38'],
	'pdf':['25','50','44','46']}

footers = {'jpg':['ff','d9'],
	'jpeg':['ff','d9'],
	'png':None,
	'gif':['00','3b'],
	'pdf':['25','25','45','4f','46']}



#Sirve para imprimir en el error estándar y terminar el programa
def printError(msg):
	sys.stderr.write('Error:\t%s\n' % msg)
	sys.exit(1)


#Agrega las opciones que tiene el programa
def addOptions():
	parser = optparse.OptionParser()
	parser.add_option('-i','--input', dest='input', default=None, help='Forensic image to analyse')
	parser.add_option('-f','--format', dest='format', default='jpg,gif,png,pdf', help='File format to look for')
	parser.add_option('-l','--limit', dest='limit', default='1048576', help='Number of bytes per file. (If ft doesn\'t have a footer') #Límite si no hay footer. 1MB
	opts,args = parser.parse_args()
	if opts.input is None:		#Forzosamente se debe indicar una imagen forense
		printError('Specify an image to process')
	for f in opts.format.split(','):	#Valida qe los formatos especificados estén soportados
		if f not in ['jpg','jpeg','gif','png','pdf']: printError('Format not supported (%s)' % f)
	return opts


#Escribe los archivos en las respectivas carpetas, con nombre secuencial
def writeFile(ftype,number,data):
	with open('recovery/%s/file%s.%s' % (ftype,number,ftype),'wb') as out:
		out.write(data)
		print 'File file%s.%s has been extracted!' % (number,ftype)


#Busca los diferentes tipos de archivos en la imagen
def findFiles(image,formats,limit):
	with open(image,'rb') as im_f:
		for f in formats:
			c_file = 0	#Contador de archivos extraidos
			c_header = 0	#Contador para validar que se cubre correctamente el header
			c_footer = 0	#Contador para validar que se leyó correctamente el footer
			file = ''	#Cadena del archivo a extraer
			im_f.seek(0,0)	#Por cada formato, vuelve a leer el archivo desde el inicio
			header = headers[f]	#Almacena header y footer del formato actual
			footer = footers[f]
			while True:
				byte = str(im_f.read(1))	#Lee un byte y lo convierte a cadena para su manejo
				if not byte: break		#Rompe el ciclo si llega al final del archivo
				if c_header < len(header):	#Valida si el contador de la cabecera aún no llega al tamaño esperado
					if (byte == header[c_header].decode('hex')):	#Decodifica el byte de la cabecera actual y lo compara con el leido
						c_header += 1	#Si son iguales aumenta el contador y agrega el byte al archivo
						file += byte
					else:	#Si no se cumple la cabecera compeltamente, resetea contador y vacía archivo
						c_header = 0
						file = ''
				if c_header == len(header): #Entra aquí sólo si encontró la cabecera completa
					while True:	#A partir de aquí busca el resto del archivo
						byte = str(im_f.read(1))
						if not byte: break
						file += byte	#Lee un byte por vez y lo va agregando al archivo
						if footer is None:
							if len(file) > limit: break	#Rompe el ciclo si no hay un footer definido y alcanzó límite
						elif c_footer < len(footer):	#Valida que se encuentre el footer completo
							if (byte == footer[c_footer].decode('hex')):
								c_footer += 1
							else:
								c_footer = 0
							if c_footer == len(footer): break #Rompe el ciclo
					writeFile(f,c_file,file) #Escribe la cadena encontrada en nuevo archivo
					c_file += 1 #Como encontró un archivo, aumenta el contador
					c_header = 0 #Resetea valores para el siguiente archivo
					c_footer = 0
					file = ''


#Inicio del programa
if __name__ == '__main__':
	try:
		print '\t\tGNU File recoverpy V1.0'
		opts = addOptions() #Agrega opciones
		if not os.path.exists('recovery'): #Crea carpetas necesarias para almacenar archvos recuperados
			os.makedirs('recovery')
		formats = opts.format.split(',')
		for format in formats:
			if not os.path.exists('recovery/%s' % format):
				os.makedirs('recovery/%s' % format)
		findFiles(opts.input,formats,int(opts.limit))
	except IOError:
		printError('File does not exist')
	except Exception:
		printError('Unexpected error')
