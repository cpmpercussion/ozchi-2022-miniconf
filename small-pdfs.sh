#!/bin/bash
for filename in *.pdf; 
do 
 gs \
 -sDEVICE=pdfwrite \
 -dCompatibilityLevel=1.4 \
 -dPDFSETTINGS=/prepress \
 -dNOPAUSE \
 -dQUIET \
 -dBATCH \
 -o "lbw${filename:0:4}.pdf" \
 ${filename}; 
done