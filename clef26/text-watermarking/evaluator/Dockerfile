# docker build -t mam10eks/pan-watermarking:eval-0.0.1 .
FROM nvcr.io/nvidia/cuda:12.8.0-cudnn-devel-ubuntu24.04

RUN apt-get update \
	&& apt-get install -y python3 python3-pip \
	&& pip3 install --break-system-packages tira click pandas

ADD requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt --break-system-packages \
	&& rm /tmp/requirements.txt \
	&& pip3 cache purge

RUN python3 -c 'import nltk; nltk.download("punkt_tab")' \
	&& python3 -c 'from bert_score import BERTScorer; BERTScorer(model_type="roberta-large", lang="en")'

ENV HF_HUB_OFFLINE=1

ADD evaluator.py /

