# wb-utils
このページでは遺伝研スパコン(it048)上に構築したwikibaseへのデータ登録方法について説明する。

以下の手順で作成する。

(a) wikibaseのインストール

(b) 手動でWikibase上に項目を設定

(c) データ投入用スクリプトをsingularityコンテナ内で実行

# (a) wikibaseのインストール
dockerとdocker-composeは既にスパコンにインストールされているので、インストール手順は割愛する。

wikibase構築用のdocker-composeファイルをダウンロードする。
```
$ wget https://raw.githubusercontent.com/wmde/wikibase-docker/master/docker-compose.yml
```
docker-compose.ymlをダウンロードしたフォルダーで以下を実行する。

```
$ docker-compose pull
```

コンテナを起動
```
$ docker-compose up -d
```

起動したかどうかを確認
```
$ docker-compose ps
Output:
               Name                             		Command              	 State          Ports
-------------------------------------------------------------------------------------------------------------------------
bin_elasticsearch_1_153d06232b02     /usr/local/bin/docker-entr ...     	Up      9200/tcp, 9300/tcp
bin_mysql_1_98bd69a2f5c8             docker-entrypoint.sh mysqld        	Up      3306/tcp
bin_quickstatements_1_e891769db85a   /bin/bash /entrypoint.sh        	Up      0.0.0.0:9191->80/tcp
bin_wdqs-frontend_1_bfb375001f18     /entrypoint.sh nginx -g da ...   	Up      0.0.0.0:8282->80/tcp
bin_wdqs-proxy_1_80cbe1d38f48        /bin/sh -c "/entrypoint.sh"       	Up      0.0.0.0:8989->80/tcp
bin_wdqs-updater_1_f26c47c6ce0f      /entrypoint.sh /runUpdate.sh   	Up
bin_wdqs_1_e573d9c29123              /entrypoint.sh /runBlazegr ...   	Up      9999/tcp
bin_wikibase_1_baf49da91847          /bin/bash /entrypoint.sh               	Up      0.0.0.0:8181->80/tcp
```

# (b) 手動でWikibase上に項目を設定
登録スクリプト実行前に[Wikibaseに手動で項目とプロパティを追加する方法.pdf](https://github.com/satoshi0409/wb-utils/blob/main/Wikibase%E3%81%AB%E6%89%8B%E5%8B%95%E3%81%A7%E9%A0%85%E7%9B%AE%E3%81%A8%E3%83%97%E3%83%AD%E3%83%91%E3%83%86%E3%82%A3%E3%82%92%E8%BF%BD%E5%8A%A0%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95.pdf)

にある手順の5ページ目「Wikibaseの main page　https://wb.ddbj.nig.ac.jp/wiki/Main_Page
に行きログインする」

以降を行い、手動で項目(Q)の新規作成とプロパティ(P)の新規作成を行います。


# (c) データ投入用スクリプトをsingularityコンテナ内で実行
以下の手順で実行できる。

(1-1) institution_master_kakenhi.xml(研究分野情報)
```
[super computer]$ cd /data/wikibase/project1/
[super computer]$ singularity exec project1.sif /usr/local/bin/python3.9 /usr/local/bin/script_wdi_xml_review_section.py
```
(1-2) review_section_master_kakenhi.xml(研究分野情報)
```
[super computer]$ cd /data/wikibase/project1/
[super computer]$ singularity exec project1.sif /usr/local/bin/python3.9 /usr/local/bin/script_wdi_xml_institution.py
```

(2) Human disease ontology(doid.json)
```
[super computer]$ cd/data/wikibase/project2/
[super computer]$ singularity exec project2.sif DOID_obographs_bot.py /home/test/doid.json
```



# 以下は(c)の詳細な注意点になりますので、ゼロから作成する際はご確認ください。

Project1では
- (1-1) 組織情報(institution_master_kakenhi.xml)　Q489からQ3248の2760個
- (1-2) 研究分野情報(review_section_master_kakenhi.xml)　Q2からQ488の481個

Project2では
- (2) Human disease ontology(doid.json) Q3255からQ13980までの10724個
※ 注意点1にあるように、2個分、具体的にはQ5290（doid.jsonの63778行目のサイズエラー）とQ10955(255769行目のサイズエラー)
が向けているので13980-3254-2=10724個
※ Q3249からQ3254はdoid.jsonを登録するために自動で登録されるデータなので本データではない。

をそれぞれ登録します。
登録用スクリプトは上記3データでそれぞれ異なりますが、singularityコンテナをProject1とProject2で分けて

2つ作成すればよいので、そのやり方を説明します。

## Project1 - 組織情報と研究分野情報
入力用の元データである組織情報(institution_master_kakenhi.xml)と研究分野情報(review_section_master_kakenhi.xml)

は https://bitbucket.org/niijp/grants_masterxml_kaken/src/master/ から入手しましたが、下段の注意点１にあるようにデータに一部問題があったので修正しています。

<img width="591" alt="項目とプロパティの新規作成後" src="https://user-images.githubusercontent.com/49433886/130773135-aa56d03f-bcc2-46e1-912d-2ba80539f55e.PNG">

次に[How to run wikidataintegrator python script.docx](https://github.com/satoshi0409/wb-utils/blob/main/How%20to%20run%20wikidataintegrator%20python%20script.docx)

に記載のある設定条件に従ったうえで、
- Project1/script_wdi_xml_institution.py (組織情報用) または

- Project1/script_wdi_xml_review_section.py (研究分野情報)
 
を実行すればwikibaseへのデータ登録は可能です。

ですが環境設定が複雑であるのと、IP制限に引っかからずにスパコン上のwikibaseにアクセスできる必要があるので、

ここではより容易なProject1/Dockerfileからsingularityコンテナを作成してスパコン上から実行する方法を説明します。
```
[local server]$ git clone https://(ユーザー名):(パーソナルアクセストークン)@github.com/ddbj/wb-utils.git
[local server]$ cd wb-utils/Project1/
[local server]$ unzip inputs.zip  # githubが25MBまでしかuploadできないためにxml入力をzipにしてあります。
[local server]$ mv inputs/*.xml  ./

```

[Wikibaseに手動で項目とプロパティを追加する方法.pdf](https://github.com/satoshi0409/wb-utils/blob/main/Wikibase%E3%81%AB%E6%89%8B%E5%8B%95%E3%81%A7%E9%A0%85%E7%9B%AE%E3%81%A8%E3%83%97%E3%83%AD%E3%83%91%E3%83%86%E3%82%A3%E3%82%92%E8%BF%BD%E5%8A%A0%E3%81%99%E3%82%8B%E6%96%B9%E6%B3%95.pdf)
の最後の2ページに従ってcreate_entity関数のQ/Pの数字を必要に応じて編集します。

script_wdi_xml_institution.pyのcreate_entity関数

![image](https://user-images.githubusercontent.com/49433886/130795405-6499db8e-03c6-456e-bcb6-b39f92c45bfc.png)

script_wdi_xml_review_section.pyのcreate_entity関数

![image](https://user-images.githubusercontent.com/49433886/130795447-1c2057b5-0f26-4049-b8b4-eaff74670b87.png)

上記２つのpythonスクリプトを編集したら、docker/singularityコンテナを以下の手順で作成します。

```
[local server]$ docker build -t project1 .
[local server]$ sudo singularity build project1.sif docker-daemon://project1:latest
[local server]$ scp -i ~/NIG/.ssh/id_rsa project1.sif [アカウント名]@gw.ddbj.nig.ac.jp:/home/[アカウント名]
[local server]$ ssh -i ~/NIG/.ssh/id_rsa [アカウント名]@gw.ddbj.nig.ac.jp
[super computer]$ qlogin
[super computer]$ ssh it048
[super computer]$ cp project1.sif /data/wikibase/project1/
```
ここまでは(1-1)と(1-2)で共通ですが、以降は実行スクリプトが異なります。

(1-1) institution_master_kakenhi.xml(研究分野情報)
```
[super computer]$ singularity exec project1.sif /usr/local/bin/python3.9 /usr/local/bin/script_wdi_xml_review_section.py
```
(1-2) review_section_master_kakenhi.xml(研究分野情報)
```
[super computer]$ singularity exec project1.sif /usr/local/bin/python3.9 /usr/local/bin/script_wdi_xml_institution.py
```
## Project2 - Human disease ontology (doid.json)
入力用の元データである doid.owl は https://bioportal.bioontology.org/ontologies/DOID

左下Submissionsからダウンロードして、スパコン上でdoid.jsonに変換しました。

(参考) rapperコマンドを使ったRDFの形式変換の例　https://ddbj-dev.atlassian.net/browse/RESOURCE-28?focusedCommentId=204928

[Instructions to run doid python script.docx](https://github.com/satoshi0409/wb-utils/blob/main/Instructions%20to%20run%20doid%20python%20script.docx)

に記載のある設定条件に従ったうえで、
- Project2/DOID_obographs_bot.py (human disease ontology用)
 
を実行すればwikibaseへのデータ登録は可能ですが、

環境設定が複雑であるのと、IP制限に引っかからずにスパコン上のwikibaseにアクセスできる必要があるので、

ここではより容易なNIG＿Project2/Dockerfileからsingularityコンテナを作成してスパコン上から実行する方法を説明します。
```
[local server]$ git clone https://(ユーザー名):(パーソナルアクセストークン)@github.com/ddbj/wb-utils.git
[local server]$ cd wb-utils/Project2/
[local server]$ docker build -t project2 .
[local server]$ sudo singularity build project2.sif docker-daemon://project2:latest
[local server]$ scp -i ~/NIG/.ssh/id_rsa project2.sif [アカウント名]@gw.ddbj.nig.ac.jp:/home/[アカウント名]
[local server]$ ssh -i ~/NIG/.ssh/id_rsa [アカウント名]@gw.ddbj.nig.ac.jp
[super computer]$ qlogin
[super computer]$ ssh it048
[super computer]$ cp project2.sif /data/wikibase/project2/
[super computer]$ cd/data/wikibase/project2/
[super computer]$ singularity exec project2.sif DOID_obographs_bot.py /home/test/doid.json
```

## 注意点

#### 注意点1: 入力データの問題
入力データの英語名に不要な半角・全角スペースが入っていた箇所は削除しました。

例) [institution_master_kakenhi.xml](https://bitbucket.org/niijp/grants_masterxml_kaken/src/master/institution_master_kakenhi.xml)
```
438798行目      <name lang="en">Policy Research Institute, Ministry of Agriculture, Forestry and Fisheries 　</name>
601255行目      <name lang="en">Kajima Technical Research Institute, Kajima Corporation </name>
```
入力文字数制限が250文字までだったので、長いデータは半角スペースを削除するなどして文字数を減らして登録できるものは登録しました。

例) 変更前 [review_section_master_kakenhi.xml](https://bitbucket.org/niijp/grants_masterxml_kaken/src/master/review_section_master_kakenhi.xml)


```
2910行目      <name lang="en">2190:Physical chemistry, functional solid state chemistry, organic chemistry, inorganic/coordination chemistry, analytical chemistry, polymers, 
organic materials, inorganic materials chemistry, energy-related chemistry, biomolecular chemistry and related fields</name>
```

変更後

```
2910行目      <name lang="en">2190:Physical chemistry,functional solid state chemistry,organic chemistry,inorganic/coordination chemistry,analytical chemistry,polymers,organic/inorganic materials chemistry,energy-related chemistry,biomolecular chemistry and related fields</name>
```

一方、[doid.json](https://github.com/satoshi0409/wb-utils/blob/main/Project2/doid.json)

```
63778行目            "val" : "Myeloid and lymphoid neoplasms with eosinophilia and abnormalities of platelet-derived growth factor receptor alpha (PDGFRA), platelet-derived growth factor receptor beta (PDGFRB), and fibroblast growth factor receptor-1 (FGFR1) are a group of hematologic neoplasms",

255769行目            "val" : "A GM2 gangliosidosis that is characterized the onset in infancy of developmental retardation, followed by paralysis, dementia and blindness, with death in the second or third year of life and has_material_basis_in homozygous or compound heterozygous mutation in the alpha subunit of the hexosaminidase A gene (HEXA) on chromosome 15q23.",
```

は文字数が多過ぎて減らせなかったので除外しています。

#### 注意点2: wikibaseを構築したスパコンが、スクリプトを実行する環境と異なる場合
もしwikibaseを構築したスパコンとは異なるサーバー上からデータ登録を行う場合はIP制限の確認とともに、

以下のcredentials.txtとwdi_configs.pyのIPアドレスをlocalhostではなく指定のIPに書き換える必要があります。

- Project1/credentials.txt、またはProject2/credentials.txtの1行目
```
1  endpointUrl=http://localhost:8181
```

- Project1/wdi_configs.pyの30行目から32行目
```
21  config = {
22      'BACKOFF_MAX_TRIES': None,
23      'BACKOFF_MAX_VALUE': 3600,
24      'USER_AGENT_DEFAULT': 'wikidataintegrator/{}'.format(__version__),
25      'MAXLAG': 5,
26      'PROPERTY_CONSTRAINT_PID': 'P2302',
27      'DISTINCT_VALUES_CONSTRAINT_QID': 'Q21502410',
28      'COORDINATE_GLOBE_QID': 'http://www.wikidata.org/entity/Q2',
29      'CALENDAR_MODEL_QID': 'http://www.wikidata.org/entity/Q1985727',
30      'MEDIAWIKI_API_URL': 'http://localhost:8181/w/api.php',
31      'MEDIAWIKI_INDEX_URL': 'http://localhost:8181/w/index.php',
32      'SPARQL_ENDPOINT_URL': 'http://localhost:8989/bigdata/sparql',
33      'WIKIBASE_URL': 'http://www.wikidata.org',
34      'CONCEPT_BASE_URI': 'http://www.wikidata.org/entity/'
35  }
```

または

- Project2/wdi_configs.pyの30行目、31行目、32行目と34行目
```
21  config = {
22      'BACKOFF_MAX_TRIES': None,
23      'BACKOFF_MAX_VALUE': 3600,
24      'USER_AGENT_DEFAULT': 'wikidataintegrator/{}'.format(__version__),
25      'MAXLAG': 5,
26      'PROPERTY_CONSTRAINT_PID': 'P2302',
27      'DISTINCT_VALUES_CONSTRAINT_QID': 'Q21502410',
28      'COORDINATE_GLOBE_QID': 'http://www.wikidata.org/entity/Q2',
29      'CALENDAR_MODEL_QID': 'http://www.wikidata.org/entity/Q1985727',
30      'MEDIAWIKI_API_URL': 'http://localhost:8181/w/api.php',
31      'MEDIAWIKI_INDEX_URL': 'http://localhost:8181/w/index.php',
32      'SPARQL_ENDPOINT_URL': 'http://localhost:8282/proxy/wdqs/bigdata/namespace/wdq/sparql',
33      'WIKIBASE_URL': 'http://wikibase.org',
34      'CONCEPT_BASE_URI': 'http://localhost:8181/entity/',
35      'WIKIDATA_SPARQL_ENDPOINT_URL': 'https://query.wikidata.org/bigdata/namespace/wdq/sparql/'
36  }
```

