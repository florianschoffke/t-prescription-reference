# Reference Implementation for a Webservice

This repository should demonstrate the basic functionality of a webservice that can be used to receive prescription data which then is retrieved by a web client.

Each file represents an entity of the system:
* [Webserver with Endpoints](./webserver/t-server.py)
* [Webserver with Endpoints](./webserver/t-server.py)
* [Database Service](./webserver/t_database.py)
* [OAuth Service for Web ](./webserver/t-oatuh.py)

All of the information is simplified to only demonstrate the rough workflow.

## How to run

1. Enable execution of the scripts:
   - `chmod +x ./start_services.sh`
   - `chmod +x ./stop_services.sh`
2. Start all services by calling `./start_services.sh`
3. Open in Browser: `http://localhost:8000/`
4. Stop all services by calling `./stop_services.sh`