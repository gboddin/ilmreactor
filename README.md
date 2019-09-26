# Elasticsearch ILM Reactor

The current ILM implementation has no retry mechanism whatsoever to manage errors.

This can be problematic if you experience a timeout and your biggest index doesn't rollover, additioning GBs to it.

ILM Reactor will just list all index having trouble and retry them when the cluster is green and not moving shard.

It should be as passive as possible.

You must set the environment variable `ES_URL` with your correct ES URL/credentials for this script to work.
