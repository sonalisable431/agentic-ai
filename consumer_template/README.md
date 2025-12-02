
# Competitive Data Consumer: EDU

## Details are available at https://signetjewelers.atlassian.net/wiki/spaces/IT/pages/2097250316/Competitive+Data+Consumer+EDU

#### To be updated

### Setup

#### Perequisites

1) Intall Node JS on your local machine
2) VS Code or any other similar IDE
3) Install SAM CLI
4) Install Docker(OS specfic)
5) Ensure you run ecs/Integration-Platform-Api in parallel and copy the API endpoint to use in below lambda

#### AWS set up

1) Ensure you have access to AWS DevOps account (481270058004) where we are maintaining the code library code artifact(repo:esi-integration-lib-test, domain:signet-esi)
2) go to <https://d-9a672aecfb.awsapps.com/start/#/>
3) copy credentials from signet-aws-devops-test(signet-devops-codeartifact programmatic access)
4) Ensure you have configured the aws_access_key_id, aws_secret_access_key & aws_session_token in aws/.credential file
5) Ensure you have configured region as us-east-2 in you aws config file

#### Installation

1) Clone the repository to your local machine ```git clone https://github.com/Signet-sd/esi-edl-api.git```
2) Navigate to esi-edl-api/cd compData_company_consumer
3) Check config.ts for the configurations that are accessed from .env file using ```process.env.*``` and update ```template.yaml``` file with required enviroment variable configuration in the src dir.
4) Intall the application dependices (Node Modules) ```npm i```

### Building the application

1) Ensure you have access to AWS Dev account (481270058004)
2) Ensure you have configured the aws_access_key_id, aws_secret_access_key & aws_session_token in aws/.credential file.
 a) go to <https://d-9a672aecfb.awsapps.com/start/#/>
 b) copy credentials from signet-aws-esi-dev(signet-developer-rw programmatic access)
3) Ensure you have configured region as us-east-2 in you aws config file
4) To build the application ```npm run dev```
5) To run the sam application ```sam local start-api```

**output:**
<http://127.0.0.1:3000/debatch-init>

Use postman or api tools to test this url

## Environment Variables

<!-- The following environment variables can be set on the Elastic Container Service (ECS) container to configure the application properly.  -->

### Mandatory Environment Variables that are needed to boot the application otherwise there are maybe some runtime errors

|**Name**|**Description**|**Default Value**|
|--|--|--|
|NODE_ENVIRONMENT|Which environment configuration should be loaded (development, test, stage or production)|development|
|ESI_TRACKER_API_URL|The ESI tracker REST API URL|update with copied API Endpoint from Perequisites|
|AD_SECRET_ID|The Azure credential to generate OAuth Token|---|
