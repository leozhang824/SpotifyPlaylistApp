#!/bin/bash
#
# Linux/Mac BASH script to build docker container
#
docker rmi finalproject-client
docker build -t finalproject-client .
