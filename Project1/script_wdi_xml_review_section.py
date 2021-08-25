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
        'SELECT distinct ?item WHERE{  ?item ?label "'+ name_en +'"@en. }');
    for item in wd_items['results']['bindings']:
        qid = item['item']['value'].split('/')[-1]
        wdi_core.WDItemEngine.delete_item(item=qid, login=login_instance, reason='remove duplicates')

def findQidByLable(name_en):
    qid = ''
    wd_items = wdi_core.WDItemEngine.execute_sparql_query(
        'SELECT distinct ?item WHERE{  ?item ?label "'+ name_en +'"@en. }');
    for item in wd_items['results']['bindings']:
        qid = item['item']['value'].split('/')[-1]
    return qid

def createEntity(path, code_nii, code_mext, name_en, name_ja, removeDuplicates = False, subrecord_of = '', item_type= 'P14', start_date = '', end_date = ''):

    qid = ''
    if removeDuplicates:
        removeDuplicate(name_en)
    else:
        qid = findQidByLable(name_en)

    if subrecord_of == '':
        subrecord_of = 'Q1'
    if end_date == '':
        item_statements = [
            wdi_core.WDString(path, prop_nr='P12'),
            wdi_core.WDString(code_nii, prop_nr='P1'),
            wdi_core.WDString(code_mext, prop_nr='P2'),
            wdi_core.WDString(name_en, prop_nr='P5'),
            wdi_core.WDString(name_ja, prop_nr='P4'),
            wdi_core.WDItemID(subrecord_of, prop_nr='P11'),
            wdi_core.WDProperty(item_type, prop_nr='P7'),
            wdi_core.WDTime(start_date, prop_nr='P9'),
        ]
    else :
        item_statements = [
            wdi_core.WDString(path, prop_nr='P12'),
            wdi_core.WDString(code_nii, prop_nr='P1'),
            wdi_core.WDString(code_mext, prop_nr='P2'),
            wdi_core.WDString(name_en, prop_nr='P5'),
            wdi_core.WDString(name_ja, prop_nr='P4'),
            wdi_core.WDItemID(subrecord_of, prop_nr='P11'),
            wdi_core.WDProperty(item_type, prop_nr='P7'),
            wdi_core.WDTime(start_date, prop_nr='P9'),
            wdi_core.WDTime(end_date, prop_nr='P10'),
        ]


    wd_item = wdi_core.WDItemEngine(wd_item_id=qid, data=item_statements)
    #print(wd_item)
    print(path, code_nii, code_mext, name_ja, name_en)
    wd_item.set_label(name_en, lang="en")
    wd_item.set_label(name_ja, lang="ja")
    #wd_item.set_description("*"+name_en, lang="en")
    #wd_item.set_description("*"+name_ja, lang="ja")

    # pprint.pprint(wd_item.get_wd_json_representation())
    print(wd_item.write(login_instance))
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

tree = ET.parse('/home/test/review_section_master_kakenhi.xml')
root = tree.getroot()

count = 0
path = ''
subrecord_of1 = ''
subrecord_of2 = ''
subrecord_of3 = ''
start_date_utc_string = ''
end_date_utc_string = ''
removeDuplicates = False

# all item attributes
print("\n")
for child in root:
    #print(child.tag, child.attrib, child.text,root.tag)
    if child.tag == "review_section_table":
        if checkKey(child.attrib, 'start_date'):
            start_date_string = child.attrib['start_date']
            start_date = datetime.strptime(start_date_string, "%Y-%m-%d").date()
            start_date_utc_string = start_date.strftime("+%Y-%m-%dT%H:%M:%SZ")
        if checkKey(child.attrib,'end_date') :
            end_date_string = child.attrib['end_date']
            end_date = datetime.strptime(end_date_string, "%Y-%m-%d").date()
            end_date_utc_string = end_date.strftime("+%Y-%m-%dT%H:%M:%SZ")
        for child1 in child:
            # print(child1.tag, child1.attrib, child1.text)
            if child1.tag == "review_section":
                path = child1.attrib['path']
            for child2 in child1:
                # print(child2.tag, child2.attrib, child2.text)
                if child2.tag == "code" and child2.attrib['type'] == "nii":
                    code_nii = child2.text
                if child2.tag == "code" and child2.attrib['type'] == "mext":
                    code_mext = child2.text
                if child2.tag == "name" and child2.attrib['lang'] == "ja":
                    name_ja = child2.text
                if child2.tag == "name" and child2.attrib['lang'] == "en":
                    name_en = child2.text
                    subrecord_of2 = createEntity(path, code_nii, code_mext, name_en, name_ja,
                                                  subrecord_of=subrecord_of1, start_date=start_date_utc_string,
                                                  end_date=end_date_utc_string,removeDuplicates=removeDuplicates)
                if child2.tag == "review_section":
                    path = child2.attrib['path']
                for child3 in child2:
                    # print(child3.tag, child3.attrib, child3.text)
                    if child3.tag == "code" and child3.attrib['type'] == "nii":
                        code_nii = child3.text
                    if child3.tag == "code" and child3.attrib['type'] == "mext":
                        code_mext = child3.text
                    if child3.tag == "name" and child3.attrib['lang'] == "ja":
                        name_ja = child3.text
                    if child3.tag == "name" and child3.attrib['lang'] == "en":
                        name_en = child3.text
                        subrecord_of3 = createEntity(path, code_nii, code_mext, name_en, name_ja,
                                                      subrecord_of=subrecord_of2, start_date=start_date_utc_string,
                                                      end_date=end_date_utc_string,removeDuplicates=removeDuplicates)
                    if child3.tag == "review_section":
                        path = child3.attrib['path']
                    for child4 in child3:
                        # print(child4.tag, child4.attrib, child4.text)
                        if child4.tag == "code" and child4.attrib['type'] == "nii":
                            code_nii = child4.text
                        if child4.tag == "code" and child4.attrib['type'] == "mext":
                            code_mext = child4.text
                        if child4.tag == "name" and child4.attrib['lang'] == "ja":
                            name_ja = child4.text
                        if child4.tag == "name" and child4.attrib['lang'] == "en":
                            name_en = child4.text
                            createEntity(path, code_nii, code_mext, name_en, name_ja, subrecord_of=subrecord_of3,
                                         start_date=start_date_utc_string, end_date=end_date_utc_string,removeDuplicates=removeDuplicates)

    else:
        continue


