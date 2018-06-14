.PHONY: test upload clean bootstrap

test:
	python3 vozesdaterra.py

test-auditok:
	auditok --save-image output.png -e 50 -n 0.4 -s 3. -E -m 60. -n 0.5
	
clear:
	rm data.json
	rm *.wav	