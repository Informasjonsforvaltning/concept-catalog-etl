.PHONY: test
extract: extract_concepts
transform: transform_concepts
load: load_concepts

extract_concepts:
	echo "Extracting concepts...."
	python3 ./extract.py -o ./tmp/

transform_concepts:
	echo "Transforming concepts...."
	python3 ./transform.py -o ./tmp/

load_concepts:
	echo "Loading concepts...."
	python3 ./load.py -o ./tmp/

clean:
	rm -r ./tmp/*
