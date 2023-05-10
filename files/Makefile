.PHONY: test
all: transform load

transform:
	echo "Transforming concepts...."
	python3 ./transform_concepts.py -o ./tmp/

load:
	echo "Loading concepts...."
	python3 ./load_concepts.py -o ./tmp/

clean:
	rm ./tmp/*.json
