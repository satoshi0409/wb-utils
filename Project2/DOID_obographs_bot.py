#!/usr/local/bin/python3.9

import argparse
import json
import os
import sys
import traceback
import urllib.request
from collections import defaultdict, Counter
from datetime import datetime
from itertools import chain
from time import gmtime, strftime, sleep

import requests
from tqdm import tqdm

from scheduled_bots import utils, PROPS, PROPS_NAMES, DEFAULT_CORE_PROPS_PIDS, DEFAULT_CORE_PROPS ,DEFAULT_PROPS, DEFAULT_ITEMS, ITEMS
from wikidataintegrator import wdi_core, wdi_helpers, wdi_login, wdi_config
from wikidataintegrator.ref_handlers import update_retrieved_if_new
from wikidataintegrator.wdi_helpers import id_mapper

#try:
#    from scheduled_bots.local import WDUSER, WDPASS
#except ImportError:
#    if "WDUSER" in os.environ and "WDPASS" in os.environ:
#        WDUSER = os.environ['WDUSER']
#        WDPASS = os.environ['WDPASS']
#    else:
#        raise ValueError("WDUSER and WDPASS must be specified in local.py or as environment variables")

with open('/home/test/credentials.txt', 'rt') as fileObject:
    lineList = fileObject.read().split('\n')
endpointUrl = lineList[0].split('=')[1]
username = lineList[1].split('=')[1]
password = lineList[2].split('=')[1]

apiUrl = wdi_config.config['MEDIAWIKI_API_URL']
sparql = wdi_config.config['SPARQL_ENDPOINT_URL']



#wdi_core.WDItemEngine.core_props.wd_properties[PROPS['OMIM ID']]['core_id'] = False
#wdi_core.WDItemEngine.core_props.wd_properties[PROPS['MeSH descriptor ID']]['core_id'] = False
#wdi_core.WDItemEngine.core_props.wd_properties[PROPS['Orphanet ID']]['core_id'] = False
#wdi_core.WDItemEngine.core_props.wd_properties[PROPS['NCI Thesaurus ID']]['core_id'] = False

### new section - create items
def findQIdByLabelEn(name_en):
    qid = ''
    wd_items = wdi_core.WDItemEngine.execute_sparql_query(
        'SELECT DISTINCT ?item WHERE { ?item rdfs:label ?obj; FILTER (lang(?obj) = "en") FILTER(LCASE(STR(?obj)) = LCASE("'+name_en+'"))}');
    for item in wd_items['results']['bindings']:
        qid = item['item']['value'].split('/')[-1]
    return qid

def createItemByLabelEN(login,label):
  qid = findQIdByLabelEn(label)
  if qid == '':
      localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(apiUrl,sparql)
      item = localEntityEngine(wd_item_id=qid)
      item.set_label(label,lang="en")
      qid=item.write(login)

  return qid

### new section - create properties
def findPIdByLabelEn(name_en):
    pid = ''
    wd_prop = wdi_core.WDItemEngine.execute_sparql_query(
        'SELECT DISTINCT ?property WHERE { ?property rdfs:label ?obj; a wikibase:Property; wikibase:directClaim ?p. FILTER (lang(?obj) = "en") FILTER(LCASE(STR(?obj)) = LCASE("'+name_en+'"))}',
        endpoint=sparql);
    for prop in wd_prop['results']['bindings']:
        pid = prop['property']['value'].split('/')[-1]
    return pid

def findPropertyInWDByLabelEn(name_en):
    wd_prop = wdi_core.WDItemEngine.execute_sparql_query(
        'SELECT DISTINCT ?property ?propertyLabel ?propertyDescription ?propType WHERE { ?property rdfs:label ?obj; a wikibase:Property; wikibase:directClaim ?p; wikibase:propertyType ?propType ; schema:description ?propertyDescription ; rdfs:label ?propertyLabel.FILTER (lang(?propertyLabel) = "en") FILTER (lang(?propertyDescription) = "en") FILTER (lang(?obj) = "en") FILTER(LCASE(STR(?obj)) = LCASE("'+name_en+'"))}',
        endpoint=wdi_config.config['WIKIDATA_SPARQL_ENDPOINT_URL'],as_dataframe=True);
    return wd_prop;

datatype_map = {'http://wikiba.se/ontology#CommonsMedia': 'commonsMedia',
                'http://wikiba.se/ontology#ExternalId': 'external-id',
                'http://wikiba.se/ontology#GeoShape': 'geo-shape',
                'http://wikiba.se/ontology#GlobeCoordinate': 'globe-coordinate',
                'http://wikiba.se/ontology#Math': 'math',
                'http://wikiba.se/ontology#Monolingualtext': 'monolingualtext',
                'http://wikiba.se/ontology#Quantity': 'quantity',
                'http://wikiba.se/ontology#String': 'string',
                'http://wikiba.se/ontology#TabularData': 'tabular-data',
                'http://wikiba.se/ontology#Time': 'time',
                'http://wikiba.se/ontology#Url': 'url',
                'http://wikiba.se/ontology#WikibaseItem': 'wikibase-item',
                'http://wikiba.se/ontology#WikibaseProperty': 'wikibase-property'}

def createPropertyByLabelEN(login,label,default_prop=False):
  pid_ex = findPIdByLabelEn(label)
  pid = pid_ex;
  if pid != '':
      default_prop=False
  #if pid != '':
  #    print('Property '+label+ ' already exists with pid:'+pid)
  #else:
  wd_prop=findPropertyInWDByLabelEn(label)
  for row in wd_prop.itertuples():
      if default_prop == True:
          s = []
      else:
          s = [wdi_core.WDUrl(row.property, prop_nr=PROPS['reference URL'])]

      localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(apiUrl,sparql)
      item = localEntityEngine(wd_item_id=pid,data=s)
      item.set_label(row.propertyLabel)
      item.set_description(row.propertyDescription)
      pid=item.write(login, entity_type="property", property_datatype=datatype_map[row.propType])
      if pid_ex == '':
          print('New Property added with pid: '+pid+' label: '+row.propertyLabel)

      if row.propertyLabel == 'equivalent property':
          s = [wdi_core.WDUrl('http://www.w3.org/2002/07/owl#equivalentProperty', prop_nr=pid)]
          localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(apiUrl, sparql)
          item = localEntityEngine(wd_item_id=pid,data=s)
          item.write(login, entity_type="property")

      if row.propertyLabel == 'equivalent class':
          s = [wdi_core.WDUrl('http://www.w3.org/2002/07/owl#equivalentClass', prop_nr=PROPS['equivalent property'])]
          localEntityEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(apiUrl, sparql)
          item = localEntityEngine(wd_item_id=pid,data=s)
          item.write(login, entity_type="property")

  return pid

__metadata__ = {'name': 'DOIDBot',
                'tags': ['disease', 'doid'],
                'properties': list(PROPS.values())
                }

login = wdi_login.WDLogin(user=username, pwd=password, mediawiki_api_url=apiUrl)
print("Successfully Login to Wikidata ", apiUrl)

print("Automatic Property setup starts...")

for default_prop_name in DEFAULT_PROPS:
    pid = findPIdByLabelEn(default_prop_name)
    if pid == '' :
        pid = createPropertyByLabelEN(login,default_prop_name,default_prop=True)
    elif pid != '' and default_prop_name == 'reference URL' :
        PROPS.update({default_prop_name: pid})
        pid = createPropertyByLabelEN(login, default_prop_name, default_prop=True)
    else:
        PROPS.update({ default_prop_name: pid})

undefind_prop_names= set();

for prop_name in tqdm(PROPS_NAMES, total=len(PROPS_NAMES)):
    pid = findPIdByLabelEn(prop_name)
    if pid == '':
        undefind_prop_names.add(prop_name)
    else:
        PROPS.update({ prop_name: pid})

print("{} new properties found!".format(len(undefind_prop_names)))

for undefind_prop_name in undefind_prop_names:
    pid = createPropertyByLabelEN(login,undefind_prop_name)
    PROPS.update({ undefind_prop_name: pid})

DEFAULT_CORE_PROPS_PIDS = set(PROPS[x] for x in DEFAULT_CORE_PROPS)

wdi_config.config['PROPERTY_CONSTRAINT_PID'] = PROPS['property constraint']
print("Automatic Property setup done!")

print("Automatic Item setup starts...")

for default_item in DEFAULT_ITEMS :
    qid = createItemByLabelEN(login,default_item)
    ITEMS.update({default_item:qid})

wdi_config.config['DISTINCT_VALUES_CONSTRAINT_QID'] = ITEMS['distinct-values constraint']

class DOGraph:
    edge_prop = {
        # 'http://purl.obolibrary.org/obo/IDO_0000664': PROPS['has cause'],  # has_material_basis_in -> has cause
        'http://purl.obolibrary.org/obo/RO_0001025': PROPS['location'],  # located in
        # 'http://purl.obolibrary.org/obo/RO_0002451': None,  # transmitted by. "pathogen transmission process" (P1060)?
        'is_a': PROPS['subclass of']}

    xref_prop = {'ORDO': PROPS['Orphanet ID'],
                 'UMLS_CUI': PROPS['UMLS CUI'],
                 'DOID': PROPS['Disease Ontology ID'],
                 'ICD10CM': PROPS['ICD-10-CM'],
                 'ICD10': PROPS['ICD-10'],
                 'ICD9CM': PROPS['ICD-9-CM'],
                 'ICD9': PROPS['ICD-9'],
                  #'MSH': 'P486',
                  #'MESH': 'P486',
                 'NCI': PROPS['NCI Thesaurus ID'],
                 'OMIM': PROPS['OMIM ID'],
                 # 'SNOMEDCT_US_2016_03_01': ''  # can't put in wikidata...
                 }
    purl_wdid = dict()

    def get_existing_items(self):
        # get all existing items we can add relationships to
        doid_wdid = id_mapper(PROPS['Disease Ontology ID'])
        if doid_wdid==None:
            doid_wdid = dict()
        self.purl_wdid = {"http://purl.obolibrary.org/obo/{}".format(k.replace(":", "_")): v for k, v in
                          doid_wdid.items()}
        # add in uberon items so we can do "located in"
        uberon_wdid = id_mapper(PROPS['UBERON ID'])
        if uberon_wdid==None:
            uberon_wdid = dict()
        self.purl_wdid.update({"http://purl.obolibrary.org/obo/UBERON_{}".format(k): v for k, v in uberon_wdid.items()})
        # add in taxonomy items for "has_material_basis_in"
        ncbi_wdid = id_mapper(PROPS['NCBI taxonomy ID'])
        if ncbi_wdid==None:
            ncbi_wdid = dict()
        self.purl_wdid.update(
            {"http://purl.obolibrary.org/obo/NCBITaxon_{}".format(k): v for k, v in ncbi_wdid.items()})

    def __init__(self, graph, login=None, fast_run=True):
        self.fast_run = fast_run
        self.version = None
        self.date = None
        self.default_namespace = None
        self.login = login
        self.nodes = dict()
        self.parse_meta(graph['meta'])
        self.parse_nodes(graph['nodes'])
        self.parse_edges(graph['edges'])
        self.dedupe_wikilinks()
        self.release = None
        if not self.purl_wdid:
            self.get_existing_items()

    def parse_meta(self, meta):
        self.version = meta['version']
        datestr = [x['val'] for x in meta['basicPropertyValues'] if
                   x['pred'] == 'http://www.geneontology.org/formats/oboInOwl#date'][0]
        self.date = datetime.strptime(datestr, '%d:%m:%Y %H:%M')
        self.default_namespace = [x['val'] for x in meta['basicPropertyValues'] if
                                  x['pred'] == 'http://www.geneontology.org/formats/oboInOwl#default-namespace'][0]

    def parse_nodes(self, nodes):
        for node in nodes:
            try:
                tmp_node = DONode(node, self)
                if "http://purl.obolibrary.org/obo/DOID_" in tmp_node.id and not tmp_node.deprecated and tmp_node.type == "CLASS":
                    self.nodes[tmp_node.id] = tmp_node
            except Exception as e:
                msg = wdi_helpers.format_msg(node['id'], PROPS['Disease Ontology ID'], None, str(e), msg_type=type(e))
                wdi_core.WDItemEngine.log("ERROR", msg)

    def parse_edges(self, edges):
        for edge in edges:
            # don't add edges where the subject is a node not in this ontology
            if edge['sub'] not in self.nodes:
                continue
            self.nodes[edge['sub']].add_relationship(edge['pred'], edge['obj'])

    def create_release(self):
        release_label = 'Disease Ontology release {}'.format(self.date.strftime('+%Y-%m-%d'))
        wd_item_id = findQIdByLabelEn(release_label)
        if wd_item_id == '':
            r = wdi_helpers.Release(release_label,
                                'Release of the Disease Ontology', self.date.strftime('+%Y-%m-%d'),
                                archive_url=self.version, edition_of_wdid=ITEMS['Disease Ontology'],
                                pub_date=self.date.date().strftime('+%Y-%m-%dT%H:%M:%SZ'),
                                mediawiki_api_url=apiUrl, sparql_endpoint_url=sparql)

            wd_item_id = r.get_or_create(self.login)

        if wd_item_id:
            self.release = wd_item_id
        else:
            raise ValueError("unable to create release")

    def create_ref_statement(self, doid):
        if not self.release:
            self.create_release()
        stated_in = wdi_core.WDItemID(value=self.release, prop_nr=PROPS['stated in'], is_reference=True)
        ref_doid = wdi_core.WDExternalID(value=doid, prop_nr=PROPS['Disease Ontology ID'], is_reference=True)
        ref_retrieved = wdi_core.WDTime(strftime("+%Y-%m-%dT00:00:00Z", gmtime()), prop_nr=PROPS['retrieved'], is_reference=True)
        do_reference = [stated_in, ref_retrieved, ref_doid]
        return do_reference

    def dedupe_wikilinks(self):
        """remove sitelinks that are used for multiple nodes"""
        dupes = {k: v for k, v in Counter([x.wikilink for x in self.nodes.values() if x.wikilink]).items() if v > 1}
        for node in self.nodes.values():
            if node.wikilink in dupes:
                node.wikilink = None


class DONode:
    def __init__(self, node, do_graph):
        self.do_graph = do_graph
        self.id = node['id']
        self.doid = node['id'].split("/")[-1].replace("_", ":")
        self.lbl = node.get('lbl', None)
        self.type = node.get('type', None)
        self.namespace = None
        self.definition = None
        self.definition_xrefs = None
        self.deprecated = None
        self.alt_id = None
        self.synonym_xrefs = None
        self.synonym_values = None
        self.synonyms = None
        self.wikilink = None
        self.xrefs = []
        if 'meta' in node:
            self.parse_meta(node['meta'])
        self.relationships = []
        self.reference = None

        self.s = []  # statements
        self.s_xref = None
        self.s_main = None

    def parse_meta(self, meta):
        """
        Using: definition, deprecated, synonyms, basicPropertyValues
        :return:
        """
        self.definition = meta.get('definition', dict()).get('val', None)
        self.definition_xrefs = meta.get('definition', dict()).get('xrefs', None)
        self.deprecated = meta.get('deprecated', False)

        if 'xrefs' in meta:
            self.xrefs = [x['val'] for x in meta['xrefs']]

        if self.definition_xrefs:
            url_xrefs = [x for x in self.definition_xrefs if 'url:http://en.wikipedia.org/wiki/' in x]
            if len(url_xrefs) == 1:
                url = urllib.request.unquote(url_xrefs[0].replace("url:http://en.wikipedia.org/wiki/", ""))
                if '#' not in url:
                    # don't use links like 'Embryonal_carcinoma#Testicular_embryonal_carcinoma'
                    self.wikilink = url

        if 'basicPropertyValues' in meta:
            bp = defaultdict(set)
            for basicPropertyValue in meta['basicPropertyValues']:
                bp[basicPropertyValue['pred']].add(basicPropertyValue['val'])
            namespace = bp['http://www.geneontology.org/formats/oboInOwl#hasOBONamespace']
            assert len(namespace) <= 1, "unknown namespace"
            if namespace:
                self.namespace = list(namespace)[0]
            else:
                self.namespace = self.do_graph.default_namespace
            if 'http://www.geneontology.org/formats/oboInOwl#hasAlternativeId' in bp:
                self.alt_id = bp['http://www.geneontology.org/formats/oboInOwl#hasAlternativeId']

        if 'synonyms' in meta:
            sxref = defaultdict(set)
            sval = defaultdict(set)
            for syn in meta['synonyms']:
                sxref[syn['pred']].update(syn['xrefs'])
                sval[syn['pred']].add(syn['val'])
            self.synonym_xrefs = dict(sxref)
            self.synonym_values = dict(sval)
            self.synonyms = set(chain(*self.synonym_values.values())) - {self.lbl}

    def add_relationship(self, pred, obj):
        self.relationships.append((pred, obj))

    def get_dependencies(self, relationships):
        """
        What wikidata IDs do we need to have before we can make this item?
        :return:
        """
        # todo: This is not implemented
        need_purl = [x[1] for x in self.relationships if x[0] in relationships]
        return [x for x in need_purl if x not in self.do_graph.purl_wdid]

    def create(self, write=True):
        if self.deprecated:
            msg = wdi_helpers.format_msg(self.doid, PROPS['Disease Ontology ID'], None, "delete me", msg_type="delete me")
            wdi_core.WDItemEngine.log("WARNING", msg)
            print(msg)
            return None
        try:
            self.create_xref_statements()
            self.s.extend(self.s_xref)
            self.create_main_statements()
            self.s.extend(self.s_main)
            wd_item = wdi_core.WDItemEngine(wd_item_id=findQIdByLabelEn(self.lbl),data=self.s,
                                            append_value=[PROPS['subclass of'], PROPS['instance of'],
                                                          PROPS['has cause'], PROPS['location'],
                                                          PROPS['OMIM ID'], PROPS['Orphanet ID'],
                                                          # PROPS['MeSH descriptor ID'],
                                                          PROPS['ICD-10-CM'],
                                                          PROPS['ICD-10'], PROPS['ICD-9-CM'],
                                                          PROPS['ICD-9'], PROPS['NCI Thesaurus ID'],
                                                          PROPS['UMLS CUI']
                                                          ],
                                            fast_run=self.do_graph.fast_run,
                                            fast_run_base_filter={PROPS['Disease Ontology ID']: ''},
                                            fast_run_use_refs=True,
                                            global_ref_mode='CUSTOM',
                                            ref_handler=update_retrieved_if_new
                                            )
            ##wd_item.fast_run_container.debug = False
            if wd_item.get_label(lang="en") == "":
                wd_item.set_label(self.lbl, lang="en")
            current_descr = wd_item.get_description(lang='en')
            if current_descr == self.definition and self.definition and len(self.definition) < 250:
                # change current def to cleaned def
                wd_item.set_description(utils.clean_description(self.definition))
            elif current_descr.lower() in {"", "human disease", "disease"} and self.definition and len(
                    self.definition) < 250:
                wd_item.set_description(utils.clean_description(self.definition))
            elif current_descr.lower() == "":
                wd_item.set_description(description="human disease", lang='en')
            if self.synonyms is not None:
                wd_item.set_aliases(aliases=self.synonyms, lang='en', append=True)
            if self.wikilink is not None:
                # a lot of these are not right... don't do this
                # wd_item.set_sitelink(site="enwiki", title=self.wikilink)
                pass
            wdi_helpers.try_write(wd_item, record_id=self.doid, record_prop=PROPS['Disease Ontology ID'], login=self.do_graph.login,
                                  write=write)
            return wd_item
        except Exception as e:
            exc_info = sys.exc_info()
            print(self.doid)
            traceback.print_exception(*exc_info)
            msg = wdi_helpers.format_msg(self.doid, PROPS['Disease Ontology ID'], None, str(e), msg_type=type(e))
            wdi_core.WDItemEngine.log("ERROR", msg)

    def create_reference(self):
        self.reference = self.do_graph.create_ref_statement(self.doid)

    def create_xref_statements(self):
        if not self.reference:
            self.create_reference()
        self.s_xref = []
        self.s_xref.append(wdi_core.WDExternalID(self.doid, PROPS['Disease Ontology ID'], references=[self.reference]))
        for xref in self.xrefs:
            if ":" in xref:
                prefix, code = xref.split(":", 1)
                prefix = prefix.strip()
                code = code.strip()
                if prefix.upper() in DOGraph.xref_prop:
                    if prefix.upper() == "OMIM" and code.startswith("PS"):
                        continue
                    self.s_xref.append(
                        wdi_core.WDExternalID(code, DOGraph.xref_prop[prefix.upper()], references=[self.reference]))

    def create_main_statements(self):
        if not self.reference:
            self.create_reference()
        self.s_main = []
        for relationship in self.relationships:
            if relationship[0] not in self.do_graph.edge_prop:
                # s = "unknown relationship: {}".format(relationship[0])
                # msg = wdi_helpers.format_msg(self.doid, PROPS['Disease Ontology ID'], None, s, msg_type="unknown relationship")
                # wdi_core.WDItemEngine.log("WARNING", msg)
                continue
            if relationship[1] not in self.do_graph.purl_wdid:
                s = "unknown obj: {}".format(relationship[1])
                msg = wdi_helpers.format_msg(self.doid, PROPS['Disease Ontology ID'], None, s, msg_type="unknown obj")
                wdi_core.WDItemEngine.log("WARNING", msg)
                continue
            self.s_main.append(wdi_core.WDItemID(self.do_graph.purl_wdid[relationship[1]],
                                                 self.do_graph.edge_prop[relationship[0]], references=[self.reference]))
        # add http://purl.obolibrary.org/obo/, exact match
        self.s_main.append(wdi_core.WDString(self.id, PROPS['exact match'], references=[self.reference]))

        if self.doid != "DOID:4":
            # instance of disease
            self.s_main.append(wdi_core.WDItemID(ITEMS['disease'], PROPS['instance of'], references=[self.reference]))

        miriam_ref = [wdi_core.WDItemID(value=ITEMS['Identifiers.org Registry'], prop_nr=PROPS['stated in'], is_reference=True),
                      wdi_core.WDUrl("http://www.ebi.ac.uk/miriam/main/collections/MIR:00000233", PROPS['reference URL'],
                                     is_reference=True)]
        self.s_main.append(wdi_core.WDString("http://identifiers.org/doid/{}".format(self.doid), PROPS['exact match'],
                                             references=[miriam_ref]))


def get_deprecated_nodes(graph):
    doid_qid = id_mapper(PROPS['Disease Ontology ID'])
    nodes = [node['id'].split("/")[-1].replace("_", ":") for node in graph['nodes'] if
             "http://purl.obolibrary.org/obo/DOID_" in node['id']
             and 'meta' in node and node['meta'].get("deprecated", False)
             and node.get('type', None) == "CLASS"]
    dep_nodes = {node: doid_qid[node] for node in nodes if node in doid_qid}
    return dep_nodes


def get_releases():
    s = 'select ?item where {{ ?item wdt:{first} wd:{second}; wdt:{third} wd:{fourth} }}'.format(first=PROPS['instance of'],second=ITEMS['version, edition, or translation'],third=PROPS['edition or translation of'],fourth=ITEMS['Disease Ontology'])
    return [x['item']['value'].split("/")[-1] for x in
            wdi_core.WDItemEngine.execute_sparql_query(s)['results']['bindings']]


RELEASES = get_releases()

def remove_deprecated_statements(qid, frc, release_wdid, props, login):
    releases = set(int(x.replace("Q", "")) for x in RELEASES)
    # don't count this release
    releases.discard(int(release_wdid.replace("Q", "")))

    for prop in props:
        frc.write_required([wdi_core.WDString("fake value", prop)])
    orig_statements = frc.reconstruct_statements(qid)

    s_dep = []
    for s in orig_statements:
        if s.get_prop_nr() == PROPS['Disease Ontology ID']:
            continue
        if any(any(x.get_prop_nr() == PROPS['stated in'] and x.get_value() in releases for x in r) for r in s.get_references()):
            setattr(s, 'remove', '')
            s_dep.append(s)

    if s_dep:
        print("-----")
        print(qid)
        print(len(s_dep))
        print([(x.get_prop_nr(), x.value) for x in s_dep])
        print([(x.get_references()[0]) for x in s_dep])
        wd_item = wdi_core.WDItemEngine(wd_item_id=qid, data=s_dep, fast_run=False)
        wdi_helpers.try_write(wd_item, '', '', login, edit_summary="remove deprecated statements")


def main(json_path='/home/test/doid.json', log_dir="./logs", fast_run=True, write=True):

    wdi_core.WDItemEngine.setup_logging(log_dir=log_dir, logger_name='WD_logger', log_name=log_name,
                                        header=json.dumps(__metadata__))

    print('Wait! OBO Graph is loading...')
    with open(json_path, encoding="utf-8") as f:
        d = json.load(f)
    graphs = {g['id']: g for g in d['graphs']}
    graph = graphs['http://purl.obolibrary.org/obo/doid.owl']
    # get the has phenotype, has_material_basis_in, and transmitted by edges from another graph
    graph['edges'].extend(graphs['http://purl.obolibrary.org/obo/doid/obo/ext.owl']['edges'])
    do = DOGraph(graph, login, fast_run)
    nodes = sorted(do.nodes.values(), key=lambda x: x.doid)
    items = []
    for n, node in tqdm(enumerate(nodes), total=len(nodes)):
        item = node.create(write=write)
        # if n>100:
        #    sys.exit(0)
        if item:
            items.append(item)

    sleep(10 * 60)
    doid_wdid = id_mapper(PROPS['Disease Ontology ID'])
    frc = items[0].fast_run_container
    if not frc:
        print("fastrun container not found. not removing deprecated statements")
        return None
    frc.clear()
    #for doid in tqdm(doid_wdid.values()):
    #    remove_deprecated_statements(doid, frc, do.release, list(PROPS.values()), login)

    #print("You have to remove these deprecated diseases manually: ")
    #print(get_deprecated_nodes(graph))

    print('Automatic Item setup done!')

if __name__ == "__main__":
    """
    Bot to add/update disease ontology to wikidata. Requires an obograph-generated json file.
    See: https://github.com/geneontology/obographs
    """

    parser = argparse.ArgumentParser(description='run wikidata disease ontology bot')
    parser.add_argument("json_path", help="Path to json file")
    parser.add_argument('--log-dir', help='directory to store logs', type=str)
    parser.add_argument('--dummy', help='do not actually do write', action='store_true')
    parser.add_argument('--fastrun', dest='fastrun', action='store_true')
    parser.add_argument('--no-fastrun', dest='fastrun', action='store_false')
    parser.set_defaults(fastrun=True)
    args = parser.parse_args()
    log_dir = args.log_dir if args.log_dir else "./logs"
    run_id = datetime.now().strftime('%Y%m%d_%H:%M')
    __metadata__['run_id'] = run_id
    fast_run = args.fastrun

    log_name = '{}-{}.log'.format(__metadata__['name'], run_id)
    if wdi_core.WDItemEngine.logger is not None:
        wdi_core.WDItemEngine.logger.handles = []
    wdi_core.WDItemEngine.setup_logging(log_dir=log_dir, log_name=log_name, header=json.dumps(__metadata__),
                                        logger_name='doid')

    if args.json_path.startswith("http"):
        print("Downloading")
        response = requests.get(args.json_path)
        with open('/tmp/do.json', 'wb') as f:
            f.write(response.content)
        args.json_path = '/tmp/do.json'
        print("Done downloading")

    main(args.json_path, log_dir=log_dir, fast_run=fast_run, write=not args.dummy)
