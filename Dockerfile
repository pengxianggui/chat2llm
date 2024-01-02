FROM python:3.10.12
LABEL maintainer="pengxianggui@marssenger.com"

#ENV PYTHONPATH=/app/.site-packages:${PYTHONPATH}

WORKDIR /app

# 将当前目录下所有内容复制到镜像中(.dockerignore声明排除范围)
COPY . /app

VOLUME /app/knowledge_base
VOLUME /app/configs
#VOLUME /app/.site-packages
VOLUME /app/.huggingface_model

#openai api
EXPOSE 20000
# api server
EXPOSE 7861
# webui
EXPOSE 8501

RUN chmod a+x /app/shutdown_lite.sh
RUN chmod a+x /app/restart_with_lite.sh
RUN chmod a+x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]