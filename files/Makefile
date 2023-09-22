.PHONY: test
all: transform load
transform: generate_mapping transform_concepts transform_comments transform_history make_delete_file
load: load_users load_concepts load_comments load_history
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

make_delete_file:
	echo "Making delete file...."
	python3 ./get_ids.py -o ./tmp/

generate_mapping:
	echo "Generating mapping...."
	python3 ./map_published_concepts.py -o ./tmp/

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

publish:
	echo "Publishing...."
	python3 ./publish.py -o ./tmp/

clean:
	rm -r ./tmp/*
