.PHONY: test upload clean bootstrap

test:
	python3 vozesdaterra.py

test-auditok:
	auditok --save-image output.png -e 50 -n 0.4 -s 3. -E -m 60. -n 0.5
	
long_audios:
	python3 vozesdaterra.py -s "entrevista" --save-image output.png


clear:
	rm data.json
	rm *.wav