# concept-etl
ETL type utilities related to our concept catalogue

This branch of the ETL is for migrating data between environments.
It will delete all existing data in the environment you want to move the data to.

You'll have to manually set a connection to the environment you want to extract data from/move data into.

You'll also have to manually trigger a harvest when prompted, and manually reindex concept-catalog after this job is finished.

How to run:

- Connect to the correct environment and port-forward the mongodb where the data resides
- cd files
- make extract
- Connect to the environment and port-forward the mongodb where you want the data to be migrated to
- make delete
  - harvest the emptied catalog on prompt
- make load
- trigger reindex
