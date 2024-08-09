node.spy: node.py
	spyc node.py

.PHONY: load
load: node.spy
	toolbelt node bridge script load node.spy

.PHONY: run
run:
	python server.py

.PHONY: clean
clean:
	rm *.spy
