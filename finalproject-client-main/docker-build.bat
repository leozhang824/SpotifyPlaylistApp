@echo off
REM
REM Windows BATCH script to build docker container
REM
@echo on
docker rmi finalproject-client
docker build -t finalproject-client .
