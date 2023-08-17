.PHONY: test
all: transform load
transform: transform_users transform_concepts transform_comments transform_history
load: load_users load_concepts load_comments load_history

transform_users:
	echo "Transforming users...."
	python3 ./transform_users.py -o ./tmp/

transform_concepts:
	echo "Transforming concepts...."
	python3 ./transform_concepts.py -o ./tmp/

transform_comments:
	echo "Transforming comments...."
	python3 ./transform_comments.py -o ./tmp/

transform_history:
	echo "Transforming history...."
	python3 ./transform_history.py -o ./tmp/
	sort ./tmp/unknown_fields.txt
load_users:
	echo "Loading users...."
	python3 ./load_users.py -o ./tmp/

load_concepts:
	echo "Loading concepts...."
	python3 ./load_concepts.py -o ./tmp/

load_comments:
	echo "Loading comments...."
	python3 ./load_comments.py -o ./tmp/

load_history:
	echo "Loading history...."
	python3 ./load_history.py -o ./tmp/

clean:
	rm ./tmp/*.json
