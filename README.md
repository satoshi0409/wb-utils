# wb-utils
このページでは遺伝研スパコン上に構築したwikibaseへのデータ登録方法について説明します。

Project1では
- (1-1) 組織情報(institution_master_kakenhi.xml)
- (1-2) 研究分野情報(review_section_master_kakenhi.xml)

Project2では
- (2) Human disease ontology(doid.json)

をそれぞれ登録します。
登録用スクリプトは上記3データでそれぞれ異なりますが、singularityコンテナをProject1とProject2で分けて

2つ作成すればよいので、そのやり方を説明します。

## Project1 - 組織情報と研究分野情報
入力用の元データである組織情報(institution_master_kakenhi.xml)と研究分野情報(review_section_master_kakenhi.xml)

は https://bitbucket.org/niijp/grants_masterxml_kaken/src/master/ から入手しました。

登録スクリプト実行前にProject1/**Wikibaseに手動で項目とプロパティを追加する方法.pdf**

にある手順に従い手動で項目(Q)の新規作成とプロパティ(P)の新規作成を行います。

<img width="591" alt="項目とプロパティの新規作成後" src="https://user-images.githubusercontent.com/49433886/130773135-aa56d03f-bcc2-46e1-912d-2ba80539f55e.PNG">



次にProject1/How to run wikidataintegrator python script.docx

に記載のある設定条件に従ったうえで、
- Project1/script_wdi_xml_institution.py (組織情報用) または

- Project1/script_wdi_xml_review_section.py (研究分野情報)
 
を実行すればwikibaseへのデータ登録は可能です。

ですが環境設定が複雑であるのと、IP制限に引っかからずにスパコン上のwikibaseにアクセスできる必要があるので、

ここではより容易なProject1/Dockerfileからsingularityコンテナを作成してスパコン上から実行する方法を説明します。
```
[local server]$ git clone https://github.com/satoshi0409/wb-utils/
[local server]$ cd Project1/
```

```
create_entity.py
```

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
[super computer]$ singularity exec proejct1.sif script_wdi_xml_review_section.py
```
(1-2) review_section_master_kakenhi.xml(研究分野情報)
```
[super computer]$ singularity exec proejct1.sif script_wdi_xml_institution.py
```
## Project2 - DOID json
入力用の元データである doid.owl は https://bioportal.bioontology.org/ontologies/DOID

左下Submissionsからダウンロードして、スパコン上でdoid.jsonに変換しました。

(参考) rapperコマンドを使ったRDFの形式変換の例　https://ddbj-dev.atlassian.net/browse/RESOURCE-28?focusedCommentId=204928

Project2/Instructions to run doid python script.docx

に記載のある設定条件に従ったうえで、
- Project2/DOID_obographs_bot.py (human disease ontology用)
 
を実行すればwikibaseへのデータ登録は可能ですが、

環境設定が複雑であるのと、IP制限に引っかからずにスパコン上のwikibaseにアクセスできる必要があるので、

ここではより容易なNIG＿Project2/Dockerfileからsingularityコンテナを作成してスパコン上から実行する方法を説明します。
```
[local server]$ git clone https://github.com/satoshi0409/wb-utils/
[local server]$ cd Project2/
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
入力データの英語名(半角英数想定)に全角スペースが入っていた箇所は削除しました。


入力文字数制限が250文字までだったので、

のデータは半角スペースを削除するなどして文字数を減らしたうえで登録しました。
一方、


は文字数が多く減らせなかったので除外しています。

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
