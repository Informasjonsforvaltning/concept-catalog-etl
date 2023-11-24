.PHONY: test
transform: transform_concepts_xml create_delete_file
load: load_concepts
publish: publish_concepts
fix_metadata: extract_metadata transform_metadata load_metadata

extract_metadata:
	echo "Extracting metadata...."
	python3 ./extract_metadata.py -o ./tmp/

transform_metadata:
	echo "Transforming metadata...."
	python3 ./transform_metadata.py -o ./tmp/

load_metadata:
	echo "Loading metadata...."
	python3 ./load_metadata.py -o ./tmp/

create_delete_file:
	echo "Make delete-file"
	python3 ./get_ids.py -o ./tmp/

transform_concepts_json:
	echo "Transforming concepts...."
	python3 ./transform_concepts_json.py -o ./tmp/

transform_concepts_xml:
	echo "Transforming concepts...."
	python3 ./transform_concepts_xml.py -o ./tmp/

load_concepts:
	echo "Loading concepts...."
	python3 ./load_concepts.py -o ./tmp/

publish_concepts:
	echo "Publishing...."
	python3 ./publish.py -o ./tmp/

clean:
	rm -r ./tmp/*
