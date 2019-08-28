DOCKER_IMG			?= ircbot
DOCKER_BUILD_ARG	:=
DOCKER_FLAGS		:= --rm -v $(PWD):/bot

ifeq ($(CMD),)
$(error Missing macro CMD)
endif

usage:
	@echo "Make Interface"
	@echo "run	: run the container in interactive mode"
	@echo "detached: run the container in detached mode (be sure to know how to stop detached containers :^))"
	@echo "build	: build the container (timestamp in .built)"
	@echo "clean	: you'll need to do this if you want to rebuild the bot (this will also rm the current image)"

run: build
	docker run -it $(DOCKER_FLAGS) $(DOCKER_IMG) $(CMD) $(BOT)

detached: build
	docker run -d $(DOCKER_FLAGS) $(DOCKER_IMG) $(CMD) $(BOT)

build: ../.built

../.built:
	docker build $(DOCKER_BUILD_ARG) --tag=$(DOCKER_IMG) ..
	echo $(shell date) > $@

clean:
	$(RM) ../.built
	docker image rm $(DOCKER_IMG)
