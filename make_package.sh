#!/bin/bash

cd ./gContactOOo/
zip -0 gContactOOo.zip mimetype
zip -r gContactOOo.zip *
cd ..

mv ./gContactOOo/gContactOOo.zip ./gContactOOo.oxt
