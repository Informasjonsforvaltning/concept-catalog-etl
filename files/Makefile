.PHONY: test
all: extract transform

extract:
	echo "Extracting concepts...."
	python3 ./extract_concepts.py -o ./tmp/

transform:
	echo "Transforming concepts...."
	python3 ./transform_concepts.py -o ./tmp/

clean:
	rm ./tmp/*.json
