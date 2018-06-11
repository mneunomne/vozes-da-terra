.PHONY: test upload clean bootstrap

test:
	python3 oraculo.py

clear:
	rm data.json
	rm *.wav	