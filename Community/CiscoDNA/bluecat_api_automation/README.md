# Cisco DNA Integration Automation Test

> This component contains the tests for Cisco DNA Workflow
Requirements: Python 3.7

## How to start
1. Clone Cisco DNA source code
   ```
	git clone git@gitlab.bluecatlabs.net:professional-services/ps-stat/cisco_dna.git
	- gzip cisco_dna folder
	# tar -zcvf cisco_dna.tar.gz cisco_dna/
    ```
2. Install virtual_bam libs
	```
	pip install -r virtual_pam/requirement.txt
	```

3. Start virtual_bam
	```
	- Set IP=0.0.0.0, port: 7000
	virtual_bam# python run_app.py
	```

4. Using docker to start gateway and set BAM_IP=<ip_virtual_bam:7000>
	```
	chmod -R o=rwx /home/bluecat
	sudo docker run -d -p 80:8000 -p 443:44300 -v /home/bluecat:/bluecat_gateway/ -v /home/bluecat:/logs/ -e BAM_IP=<ip_virtual_bam:7000> --name bluecat_gateway quay.io/bluecat/gateway:18.10.2
	```

5. Import ipam workflow to gateway
	```
	- Install lib: 
	# sudo docker exec bluecat_gateway pip install netaddr --user
	- Restart gateway: 
	# sudo docker container restart bluecat_gateway
	- Login gateway GUI uses account: nquocthai/admin
	- Import cisco_dna.tar.gz workflow
	# sudo docker container restart bluecat_gateway
	- Set permissions for ipam workflows 
	```

6. Setup env for automation
	```
	# virtualenv venv
	# source venv/bin/activate
	# pip install -r requirement.txt
	```

7. Run automation test
	```
	bluecat_api_automation#  robot -P ./Libs -i api -d Results Tests
	```

    Where
            "-P ./Libs"   path of Extended Library
            "-d Results"  path of the folder will contain Report Outputs
            "Tests"       folder contains test suites

## Project Structure
    Folder_Working
        |- Api                  # Contains Apis keyword
        |- Libs                 # Library directory (defined custom libraries here)
        |- Common               # Contains Robot Resource that related to REST API
            |- APIs
        |- Tests                
            |- Data             # Contains All Test Suite files as well as test data for each components
            |- Suites           # Contains Input Data files for Testsuites/Testcases
                |- Get_View_Api.robot
                |- Create_Pool_Api.robot
                |- ............
        |- Results              # Contains Test results
        |- config.yaml          # Contains config value like: GATEWAY_URL, USERNAME, PASSWORD
