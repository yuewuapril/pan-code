# docker build -t mam10eks/pan-watermarking:obfuscator-0.0.2 .
FROM ubuntu

RUN apt-get update \
	&& apt-get install -y python3 python3-pip \
	&& pip3 install --break-system-packages tira click pandas nltk \
	&& python3 -c 'import nltk; nltk.download("punkt_tab")' \
	&& pip3 cache purge

ADD obfuscate.py /

