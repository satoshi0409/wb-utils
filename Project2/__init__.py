PROPS = {}

ITEMS = {
    'Cancer Biomarkers database': 'Q38100115',
    'Genome assembly GRCh37': 'Q21067546',
    'sequence variant': 'Q15304597',
    'Missense Variant': 'Q27429979',
    'MyVariant.info': 'Q38104308',
    'CGI Evidence Clinical Practice': 'Q38145055',
    'CGI Evidence Clinical Trials III-IV': 'Q38145539',
    'CGI Evidence Clinical Trials I-II': 'Q38145727',
    'CGI Evidence Case Reports': 'Q38145865',
    'CGI Evidence Pre-Clinical Data': 'Q38145925',
    'combination therapy': 'Q1304270',
    'CIViC database': 'Q27612411',
    'Homo sapiens': 'Q15978631',
    'Wikipathways': 'Q7999828',
    'Food and Drug Administration': 'Q204711',
    'Inxight: Drugs Database': 'Q57664317',
    'MitoDB': 'Q58019775',
    'Mitochondrial Disease Database': 'Q58019775',
    'percentage': 'Q11229'
}

DEFAULT_CORE_PROPS = ['NCBI taxonomy ID', 'National Cancer Institute ID', 'UNII', 'MeSH tree code', 'Guide to Pharmacology Ligand ID', 'archive URL', 'UniProt protein ID', 'RefSeq RNA ID', 'Entrez Gene ID', 'DOI', 'Refseq Genome ID','image', 'NCBI Locus tag', 'PMCID', 'PubMed ID', 'NCI Thesaurus ID','InterPro ID', 'InChIKey', 'ChEBI ID', 'mirTarBase ID', 'ChemSpider ID', 'Mouse Genome Informatics ID', 'miRBase mature miRNA ID', 'Disease Ontology ID', 'PubChem CID', 'HGNC ID', 'RTECS Number', 'NDF-RT ID', 'Gene Ontology ID', 'Drugbank ID', 'miRBase pre-miRNA ID', 'KEGG ID', 'InChI', 'MeSH descriptor ID', 'HGNC gene symbol', 'ChEMBL ID', 'Orphanet ID', 'CIViC Variant ID', 'WikiPathways ID']

DEFAULT_CORE_PROPS_PIDS = {}

DEFAULT_PROPS = ['reference URL','equivalent property']

DEFAULT_ITEMS = ['version, edition, or translation','Disease Ontology','Identifiers.org Registry','disease','distinct-values constraint']

PROPS_NAMES = ['property constraint','edition number','edition or translation of','publication date','ATC code','archive URL','authority','approved by','CAS registry number','CIViC Variant ID','ChEBI ID','ChEMBL ID','ChemSpider ID','DOI','Disease Ontology ID','Drugbank ID','drug used for treatment','EC Number','Encoded By','Ensembl Gene ID','Ensembl Protein ID','Ensembl Transcript ID','Entrez Gene ID','Entrez Gene ID','GARD rare disease ID','Gene Ontology ID','genomic end','genomic start','HGNC gene symbol','HGNC ID','HGVS nomenclature','HGNC gene symbol','Human Phenotype Ontology ID','ICD-10','ICD-10-CM','ICD-9','ICD-9-CM','Guide to Pharmacology Ligand ID','InChI','InChIKey','incidence','InterPro ID',      'canonical SMILES','KEGG ID','Mouse Genome Informatics ID','MeSH tree code','MeSH descriptor ID','Mondo ID','NCBI Locus tag','NCBI taxonomy ID','NCI Thesaurus ID','NDF-RT ID','National Cancer Institute ID','OMIM ID','Orphanet ID','PDB structure ID','PMCID','image','PubChem CID','PubMed ID','RTECS Number','Rat Genome Database ID','RefSeq RNA ID','Refseq Genome ID','Refseq Protein ID','RxNorm ID','canonical SMILES','Saccharomyces Genome Database ID','Sequence Ontology ID','start time','UBERON ID','UMLS CUI','UNII','UniProt protein ID','WikiPathways ID','anatomical location','biological process','biological variant of','cell component','chemical formula',
'chromosome','curator','cytogenetic location','determination method','develops from','encodes','equivalent property','equivalent class','exact match','found in taxon','genetic association',       'genomic assembly','genomic end','genomic start','has cause','has part','has phenotype','homologene id','instance of','location','medical condition treated','miRBase mature miRNA ID','miRBase pre-miRNA ID','mirTarBase ID','molecular function','negative diagnostic predictor','negative prognostic predictor','negative therapeutic predictor','observed in','official website','ortholog','pathogen transmission process','parent taxon','part of','positive diagnostic predictor','positive prognostic predictor','positive therapeutic predictor','rating','reference URL','regulates (molecular biology)','retrieved','route of administration','stated in','statement disputed by','subclass of','subject has role','symptoms','taxon name',
'uberon id','IEDB Epitope ID','ChEBI ID','encoded by','RefSeq Protein ID','UniProt protein ID','strand orientation','HGNC ID','HGNC Gene Symbol','HomoloGene ID','Mouse Genome Informatics ID','Mouse Genome Informatics ID','Wormbase Gene ID','FlyBase Gene ID','ZFIN Gene ID']


def get_default_core_props(sparql_endpoint_url='https://query.wikidata.org/sparql') -> set:
    # get the distinct value props from wikidata, and merge that list with the default_core_props listed here
    from wikidataintegrator import wdi_core, wdi_helpers
    h = wdi_helpers.WikibaseHelper(sparql_endpoint_url)
    pids = set(h.get_pid(x) for x in DEFAULT_CORE_PROPS_PIDS)
    wdi_core.WDItemEngine.get_distinct_value_props(sparql_endpoint_url)
    wdi_core.WDItemEngine.DISTINCT_VALUE_PROPS[sparql_endpoint_url].update(pids)
    core_props = wdi_core.WDItemEngine.DISTINCT_VALUE_PROPS[sparql_endpoint_url]
    return core_props
