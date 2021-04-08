# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 12:31:23 2021

@author: Abigail Ríos Guzmán
"""
# ======================== IMPORTS ========================
from TextTools import silabizer,TextSimplifier
# ======================== IMPORTS ========================

# File handling for reading
f = open("test.txt", "r")
text = f.readlines()
f.close()

sil = silabizer() # Silabizer instance
txtSim = TextSimplifier(sil, text)

text = txtSim.replaceText()
options = txtSim.getOptions()
print(txtSim.wordsChanged)

# File handling for writing
f = open("test.txt", "w")
f.write(text + '\n\n' + options)
f.close()