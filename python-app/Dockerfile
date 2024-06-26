FROM python:3.9.4-slim
RUN groupadd --gid 1000 app && \
    useradd --create-home --gid 1000 --uid 1000 app
RUN mkdir -p /home/app/src
WORKDIR /home/app/src
COPY ./src /home/app/src
RUN pip3 install -r requirements.txt
RUN chown -R app:app /home/app/src
USER app
ENTRYPOINT ["gunicorn"]
CMD ["app:app"]