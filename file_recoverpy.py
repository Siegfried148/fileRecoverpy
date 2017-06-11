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


#Busca los diferentes tipos de archivos en la imagen
def findFiles(image,formats,limit):
	with open(image,'rb') as im_f:
		c_header = 0 #Contador para validar que se cubre correctamente el header
		c_footer = 0 #Contador para validar que se leyó correctamente el footer
		c_file = 0 #Contador de archivos extraidos
		file = '' #Cadena del archivo a extraer
		for f in formats:
			im_f.seek(0,0)
			header = headers[f]
			footer = footers[f]
			while True:
				byte = str(im_f.read(1))
				if not byte: break
				if c_header < len(header):
					if (byte == header[c_header].decode('hex')):
						c_header += 1
						file += byte
					else:
						c_header = 0
						file = ''
				if c_header == len(header):
					print file
					while True:
						byte = str(im_f.read(1))
						if not byte: break
						file += byte
						if footer is None:
							if len(file) > limit: break
						elif c_footer < len(footer):
							if (byte == footer[c_footer].decode('hex')):
								c_footer += 1
							else:
								c_footer = 0
							if c_footer == len(footer): break
					writeFile(f,c_file,file)
					c_file += 1
					c_header = 0
					c_footer = 0
					file = ''

#Inicio del programa
if __name__ == '__main__':
	try:
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
