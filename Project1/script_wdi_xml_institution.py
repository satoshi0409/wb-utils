#!/usr/local/bin/python3.9

# load the necessary libraries
from wikidataintegrator import wdi_core, wdi_login
import pandas as pd
import pprint
import shexer
import xml.etree.ElementTree as ET
from datetime import datetime

def checkKey(dict, key):
    if key in dict.keys():
        return True;
    else:
        return False;

def removeDuplicate(name_en):
    wd_items = wdi_core.WDItemEngine.execute_sparql_query(
        'SELECT distinct ?item WHERE{  ?item ?label "'+ name_en +'"@en. }')
    for item in wd_items['results']['bindings']:
        qid = item['item']['value'].split('/')[-1]
        wdi_core.WDItemEngine.delete_item(item=qid, login=login_instance, reason='remove duplicates')

def findQidByLable(name_en):
    qid = ''

    wd_items = wdi_core.WDItemEngine.execute_sparql_query(
        'SELECT distinct ?item WHERE{  ?item ?label "'+ name_en +'"@en. }')

    for item in wd_items['results']['bindings']:
        qid = item['item']['value'].split('/')[-1]
    return qid

def createEntity(code_nii, code_mext, code_jsps, name_ja, name_en, name_yomi, removeDuplicates = False, item_type = 'P13', group = '', start_date = '', end_date = ''):
    qid = ''
    if removeDuplicates:
        removeDuplicate(name_en)
    else:
        print(name_en)
        qid = findQidByLable(name_en)

    if end_date == '':
        item_statements = [
            wdi_core.WDString(code_nii, prop_nr='P1'),
            wdi_core.WDString(code_mext, prop_nr='P2'),
            wdi_core.WDString(code_jsps, prop_nr='P3'),
            wdi_core.WDString(name_ja, prop_nr='P4'),
            wdi_core.WDString(name_en, prop_nr='P5'),
            wdi_core.WDString(name_yomi, prop_nr='P6'),
            wdi_core.WDProperty(item_type, prop_nr='P7'),
            wdi_core.WDString(group, prop_nr='P8'),
            wdi_core.WDTime(start_date, prop_nr='P9'),
        ]
    else:
        item_statements = [
            wdi_core.WDString(code_nii, prop_nr='P1'),
            wdi_core.WDString(code_mext, prop_nr='P2'),
            wdi_core.WDString(code_jsps, prop_nr='P3'),
            wdi_core.WDString(name_ja, prop_nr='P4'),
            wdi_core.WDString(name_en, prop_nr='P5'),
            wdi_core.WDString(name_yomi, prop_nr='P6'),
            wdi_core.WDProperty(item_type, prop_nr='P7'),
            wdi_core.WDString(group, prop_nr='P8'),
            wdi_core.WDTime(start_date, prop_nr='P9'),
            wdi_core.WDTime(end_date, prop_nr='P10'),
        ]

    #qid = findQidByLable(name_en)

    wd_item = wdi_core.WDItemEngine(wd_item_id=qid, data=item_statements)
    #print(wd_item)
    print(code_nii,code_mext,code_jsps,name_ja,name_en,name_yomi,group,start_date,end_date)
    wd_item.set_label(name_en, lang="en")
    wd_item.set_label(name_ja, lang="ja")
    #wd_item.set_description("*"+name_en, lang="en")
    #wd_item.set_description("*"+name_ja, lang="ja")

    # pprint.pprint(wd_item.get_wd_json_representation())
    return wd_item.write(login_instance)
    #return ''

resourceUrl = '/w/api.php'

with open('/home/test/credentials.txt', 'rt') as fileObject:
    lineList = fileObject.read().split('\n')
endpointUrl = lineList[0].split('=')[1]
username = lineList[1].split('=')[1]
password = lineList[2].split('=')[1]
apiUrl = endpointUrl + resourceUrl

# login to wikibase
login_instance = wdi_login.WDLogin(user=username, pwd=password, mediawiki_api_url=apiUrl)

tree = ET.parse('/home/test/institution_master_kakenhi.xml')
root = tree.getroot()

group_string = '';
start_date_utc_string = '';
end_date_utc_string = '';
removeDuplicates = False;


# all item attributes
print("\n");
for child in root:
    #print(child.tag, child.attrib, child.text,root.tag)
    if child.tag == "institution_table":
        if checkKey(child.attrib, 'group'):
            group_string = child.attrib['group']
        if checkKey(child.attrib, 'start_date'):
            start_date_string = child.attrib['start_date']
            start_date = datetime.strptime(start_date_string, "%Y-%m-%d").date()
            start_date_utc_string = start_date.strftime("+%Y-%m-%dT%H:%M:%SZ")
        if checkKey(child.attrib,'end_date') :
            end_date_string = child.attrib['end_date']
            end_date = datetime.strptime(end_date_string, "%Y-%m-%d").date()
            end_date_utc_string = end_date.strftime("+%Y-%m-%dT%H:%M:%SZ")
        for child1 in child:
            #print(child1.tag, child1.attrib, child1.text)
            if child1.tag == "institution":
                for child2 in child1:
                    if child2.tag == "code" and child2.attrib['type'] == "nii":
                        code_nii = child2.text
                    if child2.tag == "code" and child2.attrib['type'] == "mext":
                        code_mext = child2.text
                    if child2.tag == "code" and child2.attrib['type'] == "jsps":
                        code_jsps = child2.text
                    if child2.tag == "name" and child2.attrib['lang'] == "ja":
                        name_ja = child2.text
                    if child2.tag == "name" and child2.attrib['lang'] == "en":
                        name_en = child2.text
                    if child2.tag == "name_yomi":
                        name_yomi = child2.text
                        createEntity(code_nii,code_mext,code_jsps,name_ja,name_en,name_yomi,
                                     group=group_string,start_date=start_date_utc_string,
                                     end_date=end_date_utc_string,removeDuplicates=removeDuplicates)

    else:
        continue

