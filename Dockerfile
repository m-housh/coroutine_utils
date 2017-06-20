FROM mhoush/tox

RUN pyenv install --skip-existing 3.6.1  && \
    pyenv global 3.6.1 && \
    pip install --upgrade tox && \
    pip install /usr/src/app

CMD ["make", "run-tox"]
