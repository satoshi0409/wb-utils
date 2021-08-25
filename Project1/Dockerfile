FROM centos:centos7

WORKDIR /usr/local/bin
RUN yum update -y
RUN yum install -y make gcc zlib-devel libffi-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel libuuid-devel xz-devel
RUN curl -O https://www.python.org/ftp/python/3.9.3/Python-3.9.3.tgz && \
    tar xf Python-3.9.3.tgz && \
    cd Python-3.9.3 && \
    ./configure && \
    make && \
    make altinstall

RUN /usr/local/bin/python3.9 -m pip install --upgrade pip && \
    /usr/local/bin/pip3.9 install wikidataintegrator && \
    /usr/local/bin/pip3.9 install chardet

COPY wdi_config.py /usr/local/lib/python3.9/site-packages/wikidataintegrator/wdi_config.py

COPY credentials.txt /home/test/credentials.txt
COPY institution_master_kakenhi.xml /home/test/institution_master_kakenhi.xml
COPY review_section_master_kakenhi.xml /home/test/review_section_master_kakenhi.xml

COPY script_wdi_xml_institution.py /usr/local/bin/script_wdi_xml_institution.py
COPY script_wdi_xml_review_section.py /usr/local/bin/script_wdi_xml_review_section.py
RUN chmod +x /usr/local/bin/script_wdi_xml_institution.py
RUN chmod +x /usr/local/bin/script_wdi_xml_review_section.py




