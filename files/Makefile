.PHONY: test
all: transform load
transform: transform_concepts delete
load: load_concepts

delete:
	echo "Make delete-file"
	python3 ./get_ids.py -o ./tmp/

transform_concepts:
	echo "Transforming concepts...."
	python3 ./transform_concepts.py -o ./tmp/

load_concepts:
	echo "Loading concepts...."
	python3 ./load_concepts.py -o ./tmp/

publish:
	echo "Publishing...."
	python3 ./publish.py -o ./tmp/

clean:
	rm -r ./tmp/*
