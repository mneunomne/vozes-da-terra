.PHONY: test upload clean bootstrap

test:
	python3 vozesdaterra.py

clear:
	rm data.json
	rm *.wav	