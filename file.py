#coding=utf-8

import os
o_file = open ('/Users/jeedxm/BiYeSHeJi/file.txt','r')
r_file =o_file.read()
#print  r_file
o_file.close()

a =os.getcwd()
print a 
b= os.listdir(a)
for c in b:
	print c 
