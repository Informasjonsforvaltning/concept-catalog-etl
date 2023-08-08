.PHONY: test
all: extract transform load

extract:
	echo "Extracting concepts...."
	python3 ./extract_concepts.py -o ./tmp/

transform:
	echo "Transforming concepts...."
	python3 ./transform_concepts.py -o ./tmp/

load:
	echo "Loading concepts...."
	python3 ./load_concepts.py -o ./tmp/

clean:
	rm ./tmp/*.json
