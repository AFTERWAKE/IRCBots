DOCKER_SHARE	:= -v $(realpath .):/bot
CMD				:= go run
ifeq ($(BOT),)
$(error Since there are 2 bots in this dir, please define either BOT=dad.go or BOT=mom.go when calling make)
endif
include ../IRCBot.mk
