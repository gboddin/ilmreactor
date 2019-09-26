#!/usr/bin/env python3
import requests
import os
import time
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')

logging.info("IlmReactor started")
url = os.getenv("ES_URL", "http://localhost:9200")
es_server_info = requests.get(url).json()

# looop
while True:
    # Get ILM details
    ilm_details = requests.get(url + '/*/_ilm/explain').json()
    for index_name, index_details in ilm_details['indices'].items():
        # If index is in error
        if index_details["managed"] and index_details["step"] == "ERROR":
            logging.info("Found index %s with error %s" % (index_name, index_details["step_info"]['type']))
            # Check if we can retry safely
            # Timeout -> occurs when cluster is overloaded
            # Closed -> seems to be a race condition when working with frequent rollovers
            # Validation -> Operator needs to review index/ILM settings, retrying won't hurt since ES doesn't do it automatically
            if index_details["step_info"]['type'] in \
                    [ "process_cluster_event_timeout_exception", "index_closed_exception", "validation_exception" ]:
                # Loop while cluster is busy before retrying
                while True:
                    status = requests.get(
                        "%s/_cluster/health?wait_for_status=green&timeout=10s&wait_for_no_relocating_shards=true" % url
                    )
                    if status.status_code == 200:
                        break
                        # Evade loop when cluster is OK
                    else:
                        logging.warning("Server is unhealthy or currently moving indices ...")
                # Cluster is OK , retrying ILM on this index
                logging.info("Retrying ILM for index %s" % index_name)
                logging.info(requests.post("%s/%s/_ilm/retry" % (url, index_name), "").json())
    # Avoid DDOS
    time.sleep(10)

