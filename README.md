!-----------------------------------------------
! Network Provisioning System
!-----------------------------------------------

1) Download and install docker for your system
    - Go to http://store.docker.com/
    - Create yourself an account
    - Download Community Edition (CE)
    - Install the docker software on your workstation
	
2) Build the provisioning containers
    - Navigate to the unpacked folder from cli
	- cd provisioning
    - Type 'docker-compose build' to build the docker environment
    - Type 'docker-compose up -d' to start the containers
	- Type 'docker-compose down' to stop and destory the containers
	
3) Notes
    - csv files will be stored in the 'csv' directory
	- config templates will be stored in the 'jinja2' directory
	- configs will be stored in the 'configs' directory
	- Files will be overwritten without warning (uploading and config generation). Please use caution.
	
4) Usage
    - The template generator combines CSV files and Jinja2 templates to create config files in bulk.
	- The headers (first line) in the csv file will be used as variables in the jinja2 templates
	- Variables in the jinja2 templates are defined by double brackets:  {{ variable_name }}
	- At least one header must be 'filename'
	
	
