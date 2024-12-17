.PHONY: test
all: extract delete load

extract:
	echo "Extracting concepts...."
	python3 ./extract.py -o ./tmp/

delete:
	echo "Deleting concepts...."
	python3 ./delete.py -o ./tmp/

load:
	echo "Loading concepts...."
	python3 ./load.py -o ./tmp/

clean:
	rm -r ./tmp/*
