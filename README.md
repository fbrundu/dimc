# BIM Service Provider - Context layer

## Dependencies

* Python3
* CherryPy

## Start the service

    python3 dimc.py

## Setting the configuration file

The configuration file must be saved in the directory `conf/` as `conf.json`.

## Description

The service allows the following methods:

* GET

Currently, the following actions are implemented:

* ping
* pingthru
* getjson
* getifc
* getgbxml
* getrvt
* query

### Get buildings as JSON array

    http GET http://<service_uri>/dimc/getjson district=="<district_1>" ... district=="<district_N>"

Optional parameters are:

* `typology` - ["single", "multi", "other"]
* `heating` - ["district", "other"]

### Get buildings as zip of IFC files

    http GET http://<service_uri>/dimc/getifc district=="<district_1>" ... district=="<district_N>"

### Get buildings as zip of gbXML files

    http GET http://<service_uri>/dimc/getgbxml district=="<district_1>" ... district=="<district_N>"

### Get buildings as zip of rvt files

In this case, the user must provide also revit version (e.g. "2015").

    http GET http://<service_uri>/dimc/getrvt version=="<revit_version>" district=="<district_1>" ... district=="<district_N>"

### Query buildings database

    http GET http://<service_uri>/dimc/query qname=="<query_name>" district=="<district_1>" ... district=="<district_N>"

qname represents the name of the query. Currently, the following queries are implemented:

* `getnwalls` - to get the total number of walls in a building (optionally, the type of the walls to consider is passed with the parameter typeid)
* `getwindowsinwall` - to get the list of ids of the windows of a wall; the parameter wallid is required (the id of the hosting wall)
* `gethostingwall` - to get, given the id of a window (passed with the parameter windowid), the id of the hosting wall
* `getwalltypes` - to get a list of wall types
* `gettypology` - to get the building typology
* `getheatingsupply` - to get the type of heating supply
* `getageofconstruction` - to get the age of construction
* `getoccupancy` - to get the occupancy

### Query result

The following is an example of result for a query:

    {
        "r_ver": "<query result version>",
        "q_ts": "<ISO 8601 timestamp>",
        "q_desc": "<query description>",
        "q_par": {
            "<input_param_1>": "<input_param_1_value>",
            ...
            "<input_param_n>": "<input_param_n_value>"
        },
        "q_res": [
            {
                "b_id": "<building_1_id>",
                "b_res": [
                    "<result_1>",
                    ...
                    "<result_n>"
                ]
            },
            ...
            {
                "b_id": "<building_n_id>",
                "b_res": [
                    "<result_1>",
                    ...
                    "<result_n>"
                ]
            }
        ]
    }
