#!/bin/bash
for filename in *.pdf; 
do 
 gs \
 -sDEVICE=jpeg \
 -dFirstPage=1 \
 -dLastPage=1 \
 -dJPEGQ=90 \
 -r200x200 \
 -o ${filename%.*}.jpg \
 ${filename};
done