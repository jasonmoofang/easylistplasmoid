#!/bin/bash

plasmapkg -r pyhello
rm fetch.zip
zip -r fetch.zip .
plasmapkg -i fetch.zip