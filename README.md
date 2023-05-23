# aws-glue-orchestrate-snowflake-loads
Let us understand how we can use AWS Glue as an orchestrator for data transformation steps in snowflake.

Diagram below depicts a high-level approach of a sample use case having Glue as an orchestrator
![Reference Architecture](/resources/ReferenceArchitecture.PNG)

The requirement here would be to call the stored procedure within Snowflake from glue. 

To be able to call a stored procedure in Snowflake we need to use the Python shell. Here are the components that are needed to make the use-case work:
1) Wheel (.whl) or Egg (.egg) file for Snowflake python connector
2) Snowflake stored procedure
3) AWS Glue job

## Creating a Python Wheel or Python Egg file
A sample wheel file is available in this git repo under the path 
```
/wheel/snowflake_and_config_files_python-2.7.10-py3-none-any.whl
```
Let us understand the steps required to create a wheel/egg file.

First of all, set up a Virtual environment in your machine and activate it. https://docs.python.org/3/tutorial/venv.html. After activating the virtual environment, please follow the below steps.

### Step-1 – Create setup.py
First, we will have to create a setup.py file for our package. Make sure you have the latest setup tools and pip installed.
Create a new directory.
Create a setup.py file, like the code shown below and save the file.
Note: version could be changed by the user as per the requirements. For e.g., below is 2.7.10
```
from setuptools import setup, find_packages

setup(
    name = "snowflake-connector-python",
    version = "2.7.10", # or current Snowflake Python connector version
    packages = find_packages(),
)
```
### Step-2 - Get the dependencies
To get dependencies, we will have to create a requirements.txt file and run the following:
```
$ pip freeze > requirements.txt
```
Please make sure you have all the custom dependencies in requirements.txt like below:
snowflake-connector-python==2.4.6
snowflake-ingest==1.0.4

To install the dependencies, create a new directory for e.g., wheels: 
```
$ mkdir wheels
$ cd wheels
```
Install the .whl files in the current directory using the command below.
```
pip wheel -r ../requirements.txt
```
Create a zip of all the dependencies that will be uploaded along with the .whl file created in the next step. 
```
$ zip -r ../wheels.zip
```

### Step 3 - Create the .whl or .egg file
To create the .whl file run the following command:
```
python setup.py bdist_wheel
```
To create the .egg file run the following command:  
```
python setup.py bdist_egg
```
Please navigate to dist/ directory and you will find the files .whl or .egg file. This will create a wheel file for our package. Now we will have to upload into S3 to make sure when we are running the python shell, we are getting the Snowflake python connector dependencies.

## Stored procedure in Snowflake
A stored procedure is a group of SQL statements which could be used to automate a task that required multiple SQL statements and is performed many times.

A sample stored procedure can be created as mentioned below.
```
create or replace procedure demo_stored_proc()
returns varchar not null
language sql
as
begin  
  --Add your SQL statments here
  insert into stg_sales select * from sales_stream;
  return 'Rows Processed: ' || sqlrowcount;
end;
```
## AWS Glue Job
Steps to create a Glue python job through AWS management console are mentioned below along with the sample code to connect to snowflake and execute a stored procedure.

### Upload Wheel file to S3
- Search and open the S3 Console
- Create an S3 bucket for Glue related and folder for containing the files
- Add the .whl or .egg (whichever is being created in previous step) to the folder
- Also upload the wheels files zip to the same folder.

### Create a Glue Job
- Switch to the AWS Glue console to create a new job.
- Click on Jobs on the left panel under ETL
- Type: Python Shell (Version 3.6 or higher)
- Provide a name for the job
- Select an IAM role. Create a new IAM role if one doesn’t already exist and be sure to add all required Glue policies to this role
- Select the option for select A new script to be authored by you and give any valid name to the script under Script file name, use the sample code given below.
- For a Python Shell type glue job, there are only two available options for choosing DPU (Data processing Units), we can select either 0.0625 DPU or 1 DPU. By default, AWS Glue allocates 0.0625 DPU (1/16) to each Python shell job. A single DPU provides processing capacity that consists of 4 vCPUs of compute and 16 GB of memory as per this
1/16 DPU is good enough as the glue job simply has to make a call to the stored procedure in snowflake which will be executed within snowflake and will use snowflake compute capacity itself.

![Choose DPU](/resources/Glue_python_dpu.png)
- Scroll down to Python library path, mention the .whl file from S3 bucket with complete path here.
![Add wheel file path](/resources/Configurewheelpath.png)
- Under Job Parameters, add the Snowflake connection parameters and name of the stored procedure to be executed.
- Snowflake username and password should be stored and retrieved from secret manager. Rest all parameters can be added here as shown below.
- Save and run the job
![Add Job Parameters](/resources/GlueJobParams.png)

Use the sample script to test the integration between AWS Glue and your Snowflake account to execute a stored procedure. 
```
Sample script : /script/demo_script.py
```
This script assumes you have stored your account parameters using job parameters as shown in the screen above and credentials are stored in secret manager.

Glue jobs can be scheduled, or we can make them event based as well based on the business need. For running multiple procedures, either we can call them in a same Glue job or we can create different Glue jobs and manage their dependencies in a Glue workflow and schedule the workflow

## Summary
Though AWS Glue is an ETL tool and is not a full-fledged pipeline orchestrator tool, it can easily be used for orchestrating data transformation steps within snowflake in an ELT approach. It is easy to connect Snowflake through AWS Glue and execute a stored procedure, being a managed service, maintenance overhead is minimal and using python shell is cost effective as jobs are simply calling the stored procedure which actually runs on snowflake using snowflake compute.