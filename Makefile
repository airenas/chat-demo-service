-include Makefile.options
kaldi-url?=ws://localhost:9090/client/ws/speech
greetOnConnect?=--no-greet_on_connect
#####################################################################################
install/req:
	# conda create --name cds python=3.12
	pip install -r requirements.txt
install/test-req:
	pip install -r requirements_test.txt

run:
	LOG_LEVEL=debug python -m chat_demo.run --tts_key $(tts-key) \
	    --tts_url=$(tts-url) \
	    --kaldi_url=$(kaldi-url) $(greetOnConnect) --use_terminal_input \
	    --bot_url=$(bot-url) \
	    --translate_key=$(translate-key) \

run/kaldi:
	docker run -it -p 9090:80 --restart unless-stopped intelektikalt/docker-kaldi-calc:0.1.1

test/unit:
	pytest -v --log-level=INFO

test/lint:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	#exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 . --count --max-complexity=10 --max-line-length=127 --statistics
#####################################################################################
.PHONY:
	run test install-req
