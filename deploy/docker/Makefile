include Makefile.options
########################################################################################################
## print usage information
help:
	@echo 'Usage:'
	@cat ${MAKEFILE_LIST} | grep -e "^## " -A 1 | grep -v '\-\-' | sed 's/^##//' | cut -f1 -d":" | \
		awk '{info=$$0; getline; print "  " $$0 ": " info;}' | column -t -s ':' | sort
########################################################################################################
########################################################################################################
install: run	
########################################################################################################
status: 
	docker compose ps

run: init
	docker compose up -d 
.PHONY: run	
init: .env traefik/traefik.toml traefik/rules.toml 
.PHONY: init	

clean:
	docker compose down

stop:
	docker compose stop

## _logs/xxx provides service log
_logs/%:
	docker compose logs -f $*	
logs/gui: _logs/gui

## _redeploy/xxx redeploys one service
_redeploy/%: init
	docker compose up --detach --build $*
redeploy/ai-chatbot: _redeploy/ai-chatbot
redeploy/proxy: _redeploy/proxy
redeploy/demo-service: _redeploy/demo-service
########################################################################################################
.env: .env.in Makefile.options
	cat $< | envsubst > $@
traefik/traefik.toml: traefik/traefik.toml.in Makefile.options
	cat $< | envsubst > $@
traefik/rules.toml: traefik/rules.toml.in Makefile.options
	cat $< | envsubst > $@
########################################################################################################
.EXPORT_ALL_VARIABLES:
