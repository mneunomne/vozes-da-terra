.PHONY: test upload clean bootstrap

test:
	python3 oraculo.py

clear:
	rm *.wav
	rm data.json