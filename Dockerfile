FROM pengxg/python:3.10.12
LABEL maintainer="pengxianggui@marssenger.com"
USER root

#ENV PYTHONPATH=/root/chat2llm/.site-packages:/:$PYTHONPATH

WORKDIR /root

COPY . /root/chat2llm/

VOLUME /root/chat2llm/knowledge_base
VOLUME /root/chat2llm/configs
VOLUME /usr/local/python3.10.12/lib/python3.10/site-packages
VOLUME /root/chat2llm/.huggingface_model

#openai api
EXPOSE 20000
# api server
EXPOSE 7861
# webui
EXPOSE 8501

RUN chmod a+x /root/chat2llm/shutdown_lite.sh
RUN chmod a+x /root/chat2llm/restart_with_lite.sh
RUN chmod a+x /root/chat2llm/docker-entrypoint.sh

ENTRYPOINT ["/root/chat2llm/docker-entrypoint.sh"]