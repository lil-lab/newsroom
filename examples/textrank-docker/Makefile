SYSTEM=textrank

build:
	docker build . -t $(SYSTEM)

save:
	docker save $(SYSTEM) | bzip2 > $(SYSTEM).tar.bz2

load:
	bzcat $(SYSTEM).tar.bz2 | docker load

clean:
	docker rmi $(SYSTEM) || true
	rm -f $(SYSTEM).tar.bz2

.PHONY: clean
