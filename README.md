# Calo Data Analysis
This project analyzes payment history logs and generates various reports for accounting purposes. The solution is fully dockerized and can run on any machine without extra configuration.

# Table of Contents
Overview  
How to Use  
Implementation Details  
EDA Plots  
Output Folder Contains  
Time Spent  
Future Improvements  
Running the Solution Locally  
Technologies Used  
Contact  

## Overview
The Payment History Analysis tool processes transaction logs to provide insights into payment trends, identify outliers, and detect overdraft situations for subscribers. 
It generates various visualizations to help accounting teams understand subscriber behavior over time.

## How to Use
Pull the Docker Image  

To pull the Docker image from Docker Hub:

```sh
docker pull zaeemiqbal1/calo_data_analysis:latest
```
Run the Docker Container
Ensure you are in the directory where you want the output_directory to be created.

On Linux or macOS:
```sh
docker run -v $(pwd)/output_directory:/app/output_directory zaeemiqbal1/calo_data_analysis:latest
```
On Windows (using Command Prompt or PowerShell):
```sh
docker run -v %cd%/output_directory:/app/output_directory zaeemiqbal1/calo_data_analysis:latest
```
## Implementation Details

Python Version: 3.8  
Dependencies: Listed in requirements.txt  
Main Script: main.py  
Docker: Used to containerize the solution for easy deployment and execution on any machine  

## EDA Plots

The following plots are generated:  

Distribution of Transaction Amounts  
Distribution of Transaction Types  
Transactions Over Time  
Outliers in Transaction Amounts  
Subscriber-specific EDA  

## Output Folder Contains  
 
 EDA plots  
 Overdraft subscribers in a csv file  
 Preprocessed excel file that contains subscribers details extracted from the zip file  
 
## Time Spent   

Task 1 : 3 hours  
Task 2 : 12 hours  

## Future Improvements

Add more EDA plots  
Optimize performance for large datasets  
Implement logging for better debugging and monitoring  

## Install dependencies:
```sh
pip install -r requirements.txt
```
## Run the main script:
```sh
python main.py
```
## Technologies Used
Python  
Pandas  
Matplotlib  
Seaborn  
Docker  

## Contact  

For any issues or improvements, please contact m.zaeemiqbal@gmail.com.
