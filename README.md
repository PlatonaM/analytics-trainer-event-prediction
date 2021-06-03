## analytics-trainer-event-prediction

Creates machine learning models from training data retrieved from [analytics-csv-provider](https://github.com/PlatonaM/analytics-csv-provider) and provided configurations.
Models, and corresponding metadata as well as configurations are provided via an HTTP API.

### Configuration

`CONF_LOGGER_LEVEL`: Set logging level to `info`, `warning`, `error`, `critical` or `debug`.

`CONF_STORAGE_DB_PATH`: Set database path.

`CONF_STORAGE_DATA_CACHE_PATH`: Set path for temporary files.

`CONF_JOBS_MAX_NUM`: Set maximum number of parallel jobs.

`CONF_JOBS_CHECK`: Control how often the trainer checks if new jobs are available.

`CONF_JOBS_SKD_DELAY`: Control how often jobs for training models are scheduled.

`CONF_DATA_API_URL`: URL of analytics-csv-provider API.

`CONF_DATA_MAX_AGE`: Set how long training data will be cached.


### Data Structures

#### Job resource

    {
        "id": <string>,
        "created": <string>,
        "status": "<string>",
        "model_id": <string>,
        "reason": <string>
    }


#### Model resource

    {
        "id": <string>,
        "created": <string>,
        "config": {
            "sampling_frequency": <string>,
            "imputations_technique_str": <string>,
            "imputation_technique_num": <string>,
            "ts_fresh_window_length": <number>,
            "ts_fresh_window_end": <number>,
            "ts_fresh_minimal_features": <boolean>,
            "balance_ratio": <number>,
            "random_state": [<number>],
            "cv": <number>,
            "oversampling_method": <boolean>,
            "target_col": <string>,
            "target_errorCode": <number>,
            "scaler": <string>,
            "ml_algorithm": <string>
        }
        "columns": <object>,
        "data": <string>,
        "default_values": <object>,
        "service_id": <string>,
        "time_field": <string>
    }

#### Model request

    {
        "service_id": null,                             # REQUIRED
        "ml_config": {
            "sampling_frequency": [<string>],
            "imputations_technique_str": [<string>],
            "imputation_technique_num": [<string>],
            "ts_fresh_window_length": [<number>],
            "ts_fresh_window_end": [<number>],
            "ts_fresh_minimal_features": [<boolean>],
            "balance_ratio": [<number>],
            "random_state": [[<number>]],
            "cv": [<number>],
            "oversampling_method": [<boolean>],
            "target_col": [<string>],                     # REQUIRED
            "target_errorCode": [<number>],               # REQUIRED
            "scaler": [<string>],
            "ml_algorithm": [<string>]
        }
    }

#### Model request response

    {
        "available": <object>,
        "pending": <object>
    }

#### Job request

    {
        "model_id": <string>
    }

### API

#### /models

**GET**

_List IDs of all model resources._

    # Example    
    
    curl http://<host>/models
    [
        "def7d53676a6035bd6121bdb72a444fed6aba676cb246d4d2467eb0318574425",
        "eedef895da368d1a38caeb2be88777b481425a6112ebf21970ff1df502faddec"
    ]

**POST**

_Send a model request to create model resources per configuration variant. Model IDs are generated from the source_id, and the configuration variant._

    # Example
    # Providing two values for "target_errorCode" yields two configuration variants and thus two models.

    cat new_model_request.json
    {
        "service_id": "urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d",
        "ml_config": {
            "target_col": [
                "module_2_errorcode"
            ],
            "target_errorCode": [
                1051,
                1202
            ]
        }
    }

    curl \
    -d @new_model_request.json \
    -H `Content-Type: application/json` \
    -X POST http://<host>/models

    # Response with two model IDs

    {
        "available": [
            "def7d53676a6035bd6121bdb72a444fed6aba676cb246d4d2467eb0318574425",
            "eedef895da368d1a38caeb2be88777b481425a6112ebf21970ff1df502faddec"
        ],
        "pending": []
    }

#### /models/{model_id}

**GET**

_Retrieve a model resource._

    # Example    
    
    curl http://<host>/models/def7d53676a6035bd6121bdb72a444fed6aba676cb246d4d2467eb0318574425
    {
        "id": "def7d53676a6035bd6121bdb72a444fed6aba676cb246d4d2467eb0318574425",
        "created": "2021-05-07T10:21:26.150618Z",
        "config": {
            "sampling_frequency": "5S",
            "imputations_technique_str": "pad",
            "imputation_technique_num": "pad",
            "ts_fresh_window_length": 30,
            "ts_fresh_window_end": 30,
            "ts_fresh_minimal_features": true,
            "balance_ratio": 0.5,
            "random_state": [
                0
            ],
            "cv": 5,
            "oversampling_method": false,
            "target_col": "module_2_errorcode",
            "target_errorCode": 1051,
            "scaler": "StandardScaler",
            "ml_algorithm": "RandomForestClassifier"
        },
        "columns": [
            "time",
            "location_ec-generator_gesamtwirkleistung",
            "location_ec-gesamt_gesamtwirkleistung",
            "location_ec-prozess_gesamtwirkleistung",
            "location_ec-roboter_gesamtwirkleistung",
            "location_roboter-ausgabe_gesamtwirkleistung",
            "location_roboter-eingabe_gesamtwirkleistung",
            "location_transport-gesamt_gesamtwirkleistung",
            "location_wm1-gesamt_gesamtwirkleistung",
            "location_wm1-heizung-reinigen_gesamtwirkleistung",
            "location_wm1-heizung-trocknung_gesamtwirkleistung",
            "location_wm2-gesamt_gesamtwirkleistung",
            "location_wm2-heizung-reinigen_gesamtwirkleistung",
            "location_wm2-heizung-trocknung_gesamtwirkleistung",
            "location_wm2-vakuumpumpe_gesamtwirkleistung",
            "module_1_errorcode",
            "module_1_errorindex",
            "module_1_state",
            "module_1_station_1_process_1_errorcode_0",
            "module_1_station_1_process_1_errorcode_980",
            "module_1_station_2_process_1_errorcode_0",
            "module_1_station_2_process_1_errorcode_980",
            "module_1_station_31_process_1_errorcode_0",
            "module_1_station_31_process_1_errorcode_980",
            "module_1_station_31_process_1_errorcode_998",
            "module_1_station_3_process_1_errorcode_0",
            "module_1_station_3_process_1_errorcode_980",
            "module_1_station_4_process_1_errorcode_0",
            "module_1_station_4_process_1_errorcode_980",
            "module_1_station_5_process_1_errorcode_0",
            "module_1_station_5_process_1_errorcode_980",
            "module_1_station_6_process_1_errorcode_0",
            "module_1_station_6_process_1_errorcode_980",
            "module_2_errorcode",
            "module_2_errorindex",
            "module_2_state",
            "module_2_station_1_process_1_errorcode_0",
            "module_2_station_21_process_1_errorcode_999",
            "module_2_station_22_process_1_errorcode_0",
            "module_2_station_22_process_1_errorcode_999",
            "module_2_station_24_process_1_errorcode_0",
            "module_2_station_25_process_1_errorcode_51",
            "module_2_station_25_process_1_errorcode_53",
            "module_2_station_25_process_1_errorcode_55",
            "module_2_station_28_process_1_errorcode_51",
            "module_2_station_28_process_1_errorcode_53",
            "module_2_station_28_process_1_errorcode_55",
            "module_2_station_28_process_1_errorcode_980",
            "module_2_station_29_process_1_errorcode_0",
            "module_2_station_3_process_1_errorcode_0",
            "module_2_station_3_process_1_errorcode_998",
            "module_2_station_4_process_1_errorcode_0",
            "module_2_station_4_process_1_errorcode_998",
            "module_2_station_50_process_1_errorcode_0",
            "module_2_station_51_process_1_errorcode_0",
            "module_2_station_51_process_1_errorcode_51",
            "module_2_station_51_process_1_errorcode_53",
            "module_2_station_51_process_1_errorcode_55",
            "module_2_station_5_process_1_errorcode_0",
            "module_2_station_5_process_1_errorcode_998",
            "module_2_station_6_process_1_errorcode_0",
            "module_2_station_6_process_1_errorcode_998",
            "module_4_errorcode",
            "module_4_errorindex",
            "module_4_state",
            "module_5_errorcode",
            "module_5_errorindex",
            "module_5_state",
            "module_6_errorcode",
            "module_6_errorindex",
            "module_6_state"
        ],
        "data": "H4sIAKYUlWAC/+Vde0BU1dYf3sNDGBUVj....",
        "default_values": {
            "module_2_station_4_process_1_errorcode_0": 0,
            "module_1_station_1_process_1_errorcode_0": 0,
            "module_2_station_51_process_1_errorcode_0": 0,
            "module_2_station_3_process_1_errorcode_0": 0,
            "module_2_station_50_process_1_errorcode_0": 0,
            "module_2_station_24_process_1_errorcode_0": 0,
            "module_2_station_5_process_1_errorcode_0": 0,
            "module_1_station_31_process_1_errorcode_0": 0,
            "module_1_station_5_process_1_errorcode_0": 0,
            "module_1_station_2_process_1_errorcode_0": 0,
            "module_1_station_3_process_1_errorcode_0": 0,
            "module_1_station_6_process_1_errorcode_0": 0,
            "module_1_station_4_process_1_errorcode_0": 0,
            "module_2_station_6_process_1_errorcode_0": 0,
            "module_2_station_22_process_1_errorcode_0": 0,
            "module_2_station_21_process_1_errorcode_999": 0,
            "module_2_station_1_process_1_errorcode_0": 0,
            "module_2_station_4_process_1_errorcode_998": 0,
            "module_2_station_3_process_1_errorcode_998": 0,
            "module_2_station_5_process_1_errorcode_998": 0,
            "module_2_station_6_process_1_errorcode_998": 0,
            "module_1_station_31_process_1_errorcode_998": 0,
            "module_2_station_51_process_1_errorcode_51": 0,
            "module_2_station_25_process_1_errorcode_51": 0,
            "module_2_station_51_process_1_errorcode_55": 0,
            "module_2_station_25_process_1_errorcode_55": 0,
            "module_2_station_28_process_1_errorcode_55": 0,
            "module_2_station_28_process_1_errorcode_51": 0,
            "module_2_station_28_process_1_errorcode_980": 0,
            "module_2_station_51_process_1_errorcode_53": 0,
            "module_2_station_25_process_1_errorcode_53": 0,
            "module_2_station_28_process_1_errorcode_53": 0,
            "module_2_station_29_process_1_errorcode_0": 0,
            "module_2_station_22_process_1_errorcode_999": 0,
            "module_1_station_1_process_1_errorcode_980": 0,
            "module_1_station_31_process_1_errorcode_980": 0,
            "module_1_station_5_process_1_errorcode_980": 0,
            "module_1_station_3_process_1_errorcode_980": 0,
            "module_1_station_2_process_1_errorcode_980": 0,
            "module_1_station_6_process_1_errorcode_980": 0,
            "module_1_station_4_process_1_errorcode_980": 0
        },
        "service_id": "urn:infai:ses:service:c2872437-3e53-49c6-a5be-bf264d52430d",
        "time_field": "time"
    }

#### /jobs

**GET**

_List IDs of all jobs._

    # Example    
    
    curl http://<host>/jobs
    {
        "current": [],
        "history": [
            "18116293f25c4c11bec9d3572d710df8",
            "2e0f0d0f8e334859a509ff9dc1817cf2",
            "ddd2e5f72156413eacf1ca522a341bae"
        ]
    }

**POST**

_Send a job request to start a job._

    # Example

    cat new_job_request.json
    {
        "model_id": "def7d53676a6035bd6121bdb72a444fed6aba676cb246d4d2467eb0318574425"
    }
    
    curl \
    -d @new_job_request.json \
    -H `Content-Type: application/json` \
    -X POST http://<host>/jobs

#### /jobs/{job_id}

**GET**

Retrieve job details.

    # Example
    
    curl http://<host>/jobs/18116293f25c4c11bec9d3572d710df8
    {
        "id": "18116293f25c4c11bec9d3572d710df8",
        "created": "2021-05-07T10:19:46.483339Z",
        "status": "finished",
        "model_id": "def7d53676a6035bd6121bdb72a444fed6aba676cb246d4d2467eb0318574425",
        "reason": null
    }