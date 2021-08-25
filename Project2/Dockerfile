FROM centos:centos7

WORKDIR /usr/local/bin
RUN yum update -y
RUN yum install -y make gcc zlib-devel libffi-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel libuuid-devel xz-devel unzip
RUN curl -O https://www.python.org/ftp/python/3.9.3/Python-3.9.3.tgz && \
    tar xf Python-3.9.3.tgz && \
    cd Python-3.9.3 && \
    ./configure && \
    make && \
    make altinstall

RUN /usr/local/bin/python3.9 -m pip install --upgrade pip && \
    /usr/local/bin/pip3.9 install wikidataintegrator && \
    /usr/local/bin/pip3.9 install cachetools && \
    /usr/local/bin/pip3.9 install shexer && \
    /usr/local/bin/pip3.9 install chardet

COPY wdi_config.py /usr/local/lib/python3.9/site-packages/wikidataintegrator/wdi_config.py

COPY credentials.txt /home/test/credentials.txt
COPY doid.json /home/test/doid.json 
COPY DOID_obographs_bot.py /usr/local/bin/DOID_obographs_bot.py
RUN chmod +x /usr/local/bin/DOID_obographs_bot.py

COPY scheduled-bots-main.zip /usr/local/bin/scheduled-bots-main.zip
RUN  cd /usr/local/bin/ && \
     unzip scheduled-bots-main.zip && \
     /usr/local/bin/pip3.9 install -e scheduled-bots-main
COPY __init__.py /usr/local/bin/scheduled-bots-main/scheduled_bots/__init__.py
COPY wikibase_helper.py /usr/local/lib/python3.9/site-packages/wikidataintegrator/wdi_helpers/wikibase_helper.py
COPY release.py /usr/local/lib/python3.9/site-packages/wikidataintegrator/wdi_helpers/release.py
COPY update_retrieved_if_new.py /usr/local/lib/python3.9/site-packages/wikidataintegrator/ref_handlers/update_retrieved_if_new.py


