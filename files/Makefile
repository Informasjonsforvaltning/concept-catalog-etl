.PHONY: test
transform_json: transform_concepts_json delete
transform_xml: transform_concepts_xml transform_comments delete
load: load_concepts load_comments

delete:
	echo "Make delete-file"
	python3 ./get_ids.py -o ./tmp/

transform_concepts_json:
	echo "Transforming concepts...."
	python3 ./transform_concepts_json.py -o ./tmp/

transform_concepts_xml:
	echo "Transforming concepts...."
	python3 ./transform_concepts_xml.py -o ./tmp/

transform_comments:
	echo "Transforming comments...."
	python3 ./transform_comments.py -o ./tmp/

load_concepts:
	echo "Loading concepts...."
	python3 ./load_concepts.py -o ./tmp/

load_comments:
	echo "Loading comments...."
	python3 ./load_comments.py -o ./tmp/

publish:
	echo "Publishing...."
	python3 ./publish.py -o ./tmp/

clean:
	rm -r ./tmp/*
