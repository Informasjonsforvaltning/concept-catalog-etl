.PHONY: test
all: extract transform load

extract:
	echo "Extracting concepts...."
	python3 ./extract.py -o ./tmp/

transform:
	echo "Transforming concepts...."
	python3 ./transform.py -o ./tmp/

load:
	echo "Loading concepts...."
	python3 ./load.py -o ./tmp/

clean:
	rm -r ./tmp/*.json
