# GOReverseLookup
**GOReverseLookup** is a Python package designed for Gene Ontology Reverse Lookup. It serves the purpose of identifying statistically significant genes within a set of selected Gene Ontology Terms.

While Gene Ontology offers valuable insights through gene annotations associated with individual terms, the biological reality often involves the complex interaction of multiple terms that either promote or inhibit a specific pathophysiological process. Unfortunately, Gene Ontology does not provide a built-in mechanism for computing statistically significant genes that are shared across multiple terms.

GOReverseLookup steps in to bridge this gap. It empowers researchers to uncover genes of statistical significance that participate in various interconnected Gene Ontology Terms, shedding light on intricate biological processes.

# Getting started
This section instructs you how to install the GOReverseLookup package and it's prerequisites.
## Prerequisites
* Python >= 3.10.0
* Integrated Development Application (IDE) - such as Visual Studio Code (VSCode)
* Downloading several database files (Gene Ontology files and 3rd party database human-ortholog mapping files).
    - Gene Ontology Annotations File for Homo Sapiens proteins: http://current.geneontology.org/products/pages/downloads.html
    - Gene Ontology .obo file: http://current.geneontology.org/ontology/go.obo
    - ZFIN human ortholog mapping file: https://zfin.org/downloads/human_orthos.txt
    - RGD human ortholog mapping file: https://download.rgd.mcw.edu/pub/data_release/orthologs/RGD_ORTHOLOGS_Ortholog.txt
    - MGI human ortholog mapping file: https://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt
    - Xenbase human ortholog mapping file: https://download.xenbase.org/xenbase/GenePageReports/XenbaseGeneHumanOrthologMapping.txt
## Installation
To use the package, install it with pip:
```
pip install goreverselookup
```

# Usage
## Using an IDE (e.g., Visual Studio Code)
### Folder structure setup
Firstly, create a folder that will be the root of your Python project. We will refer to the root folder as `root/`. Ideally, you should create the following folder structure:
```
root/
    - input_files
        - input.txt
    - results
        - data.json
        - statistically_significant_genes.json
    - main.py
```
Explanation of the folder structure:
    - `input_files` is where input.txt files are stored. These files will server as the entry point for the program and will have to be constructed manually.
    - `results` is where the results of the analysis will be stored. After the program runs in entirety, two files will be computed: 
        - `data.json` 
        - `statistically_significant_genes.json`
        The contents of the above files are explained in subsequent sections.
    - `main.py` is the main file, where the Python code will be placed to carry out the analysis.

### Creating the input.txt file
**input.txt** is the entry to the program. It contains all the relevant data for the program to successfully complete the analysis of statistically important genes that positively or negatively contribute to one or more pathophysiological processes.

An example input.txt file to discover the genes that positively contribute to both the development of chronic inflammation and cancer is:
```
# comments are preceded by a single '#'
# section titles are preceded by three '###'
###settings
homosapiens_only	True
require_product_evidence_codes	False
fisher_test_use_online_query	False
include_all_goterm_parents	True
uniprotkb_genename_online_query	False
p_value	0.05
###processes [proces name] [to be expressed + or suppressed -]
chronic_inflammation	+
cancer	+
###categories [category] [True / False]
biological_process	True
molecular_activity	True
cellular_component	False
###GO_terms [GO id] [process] [upregulated + or downregulated - or general 0] [weight 0-1] [GO term name - optional] [GO term description - optional]
GO:0006954	chronic_inflammation	+	1	inflammatory response
GO:1900408	chronic_inflammation	-	1	negative regulation of cellular response to oxidative stress
GO:1900409	chronic_inflammation	+	1	positive regulation of cellular response to oxidative stress
GO:2000524	chronic_inflammation	-	1	negative regulation of T cell costimulation
GO:2000525	chronic_inflammation	+	1	positive regulation of T cell costimulation
GO:0002578	chronic_inflammation	-	1	negative regulation of antigen processing and presentation
GO:0002579	chronic_inflammation	+	1	positive regulation of antigen processing and presentation
GO:1900017	chronic_inflammation	+	1	positive regulation of cytokine production involved in inflammatory response
GO:1900016	chronic_inflammation	-	1	negative regulation of cytokine production involved in inflammatory response
GO:0001819	chronic_inflammation	+	1	positive regulation of cytokine production
GO:0001818	chronic_inflammation	-	1	negative regulation of cytokine production
GO:0050777	chronic_inflammation	-	1	negative regulation of immune response
GO:0050778	chronic_inflammation	+	1	positive regulation of immune response
GO:0002623	chronic_inflammation	-	1	negative regulation of B cell antigen processing and presentation
GO:0002624	chronic_inflammation	+	1	positive regulation of B cell antigen processing and presentation
GO:0002626	chronic_inflammation	-	1	negative regulation of T cell antigen processing and presentation
GO:0002627	chronic_inflammation	+	1	positive regulation of T cell antigen processing and presentation

GO:0007162	cancer	+	1	negative regulation of cell adhesion
GO:0045785	cancer	-	1	positive regulation of cell adhesion
GO:0010648	cancer	+	1	negative regulation of cell communication
GO:0010647	cancer	-	1	positive regulation of cell communication
GO:0045786	cancer	-	1	negative regulation of cell cycle
GO:0045787	cancer	+	1	positive regulation of cell cycle
GO:0051782	cancer	-	1	negative regulation of cell division
GO:0051781	cancer	+	1	positive regulation of cell division
GO:0030308	cancer	-	1	negative regulation of cell growth
GO:0030307	cancer	+	1	positive regulation of cell growth
#GO:0043065	cancer	-	1	positive regulation of apoptotic process
#GO:0043066	cancer	+	1	negative regulation of apoptotic process
GO:0008285	cancer	-	1	negative regulation of cell population proliferation
GO:0008284	cancer	+	1	positive regulation of cell population proliferation
```
The **settings** section contains the settings that will be used during the algorithm.
The available settings are the following: 
* `homosapiens_only`: if only homosapiens products should be queried from uniprot and ensembl; WARNING: This setting is currently hardcoded to True
* `require_product_evidence_codes`: if only genes with evidence code should be used in the analysis; WARNING: This setting is currently hardcoded to False.
* `fisher_test_use_online_query`: When performing the Fisher's test, the GO Terms (eg. GO:0008284) associated to a gene can be parsed either from the GO Annotations File (`goa_human.gaf`) or they can be queried by submitting a request to the Gene Ontology servers (via `http://api.geneontology.org/api/bioentity/gene/{gene_id}/function`). If this setting is true, then an online query will be used, otherwise the GO Annotations File will be used to deduce terms associated to genes.
* `include_all_goterm_parents`: In Gene Ontology, genes are annotated only to very specific GO Terms, which might be nested very deep in the GO Terms hierarchy tree. If this setting is true, all indirectly annotated terms (aka parent terms) are also accounted for, besides directly annotated GO Terms. If this setting is false, only directly annotated GO Terms are accounted for.
* `uniprotkb_genename_online_query`: When querying all genes associated to a GO Term, Gene Ontology returns UniProtKB identified genes (amongst others, such as ZFIN, Xenbase, MGI, RGD). During the algorithm, gene name has to be determined from the UniProtKB id, which is done in (Product).fetch_ortholog_async function. The gene name can be obtained either online via UniProtApi or offline via GO Annotations File. If True, will query genename from a UniProtKB id via an online server request. If False, will query genename from a UniProtKB id via the GO Annotations File.
* `pvalue`: Represents the p-value against which the genes will be scored to determine if they are statistically significant. For example, if the VEGFA gene has pvalues smaller than the set pvalue (default is 0.05) for all the processes of interest of the user (eg. cancer+, inflammation+) AND also higher pvalues than the set pvalue for opposite processes (eg. cancer-, inflammation-), then the VEGFA gene is said to be statistically important in the event of coexistance of inflammation and cancer.

### Code
There are two main algorithms that can be used to achieve the same result. The mentioned scripts should be put in the `main.py` file, which you should execute using an IDE of your choice, preferably Visual Studio Code.

a) ** The Workflows Algorithm**
Workflows provide a simple and easy-to-use solution to jumpstart your research. All that is needed is that you provide an input file and a save folder to the PrimaryWorkflow class and call workflow.run_workflow():
```python
# import necessary classes
from goreverselookup import PrimaryWorkflow
from goreverselookup import Cacher
from goreverselookup import LogConfigLoader

# setup logger
import logging
LogConfigLoader.setup_logging_config()
logger = logging.getLogger(__name__)

# setup cacher
Cacher.init(cache_dir="app/goreverselookup/cache")

# run the research algorithm
workflow = PrimaryWorkflow(input_file_fpath="input_files/input.txt", save_folder_dir="results")
workflow.run_workflow()
```
PrimaryWorkflow expects two parameters: the first is `input_file_fpath`, which should be set to the path of your input.txt file. The second parameter is `save_folder_dir`, which is a path to the directory where the result files will be saved.

If the workflow executes successfully, two files should be saved into `save_folder_dir`:
    - `data.json` contains the representation of the entire research workflow (model) and can be later used to load the model instead of recomputing it from input.txt again
    - `statistically_significant_genes.json` contains the genes which were found to statistically significantly contribute to the processes the researcher is interested in

**Logger** is set up in order to log the current algorithm steps to the console of your IDE (e.g., VSCode). By setting up the logger, you can monitor which commands the program is currently executing.

**Cacher** is set up in order to save web responses and and function return values. It's function is to speed up any subsequent program runs on data that has been already requested from the servers or data already computed in a previous time point. This is useful, because if you make slight modifications to input.txt and re-run the program, Cacher will restore the already computed values from the program's cache and only send the web requests only for the new additions to the input.txt file. 

b) ** The ReverseLookup Model Algorithm **
The ReverseLookup (research) model is the core of the analysis. Workflows are actually just a wrapper around the ReverseLookup model, hiding all the complexities from the researcher. To carry out the same full analysis (as is done in the workflows algorithm), you need to construct and run the following `main.py` file:
```python
from goreverselookup import ReverseLookup
from goreverselookup import Cacher
from goreverselookup import LogConfigLoader
from goreverselookup import nterms, adv_product_score, binomial_test, fisher_exact_test

# setup logger
import logging
LogConfigLoader.setup_logging_config()
logger = logging.getLogger(__name__)

# setup cacher
Cacher.init(cache_dir="app/goreverselookup/cache")

# load the model from input file and query relevant data from the web
model = ReverseLookup.from_input_file("input_files/input.txt")
model.fetch_all_go_term_names_descriptions(run_async=True, req_delay=0.1)
model.fetch_all_go_term_products(web_download=True, run_async=True)
model.create_products_from_goterms()
model.fetch_ortholog_products(run_async=True, max_connections=15, semaphore_connections=5, req_delay=0.1)
model.prune_products()
model.fetch_product_infos(refetch=False, run_async=True, max_connections=15, semaphore_connections=10, req_delay=0.1)
model.save_model("results/data.json")

# test model load from existing json, perform model scoring
model = ReverseLookup.load_model("results/data.json")
nterms_score = nterms(model)
adv_prod_score = adv_product_score(model)
binom_score = binomial_test(model)
fisher_score = fisher_exact_test(model)
model.score_products(score_classes=[nterms_score, adv_prod_score, binom_score, fisher_score])
model.model_settings.pvalue = 0.05 # set pvalue to be used in statistical analysis
model.perform_statistical_analysis(test_name="fisher_test", filepath="results/statistically_relevant_genes.json")
model.save_model("results/data.json")
```
Each function call on the `ReverseLookup` instance called `model` has a descriptive name, highlighting it's task. The functions are heavily commented in code, so we encourage you to explore these comments and the code of our GitHub repository so as to gain a deeper understanding of the inner complexities of our tool.

## Using GOReverseLookup.exe
### GOReverseLookup.exe from existing project template
This section shows you how to start the GOReverseLookup by downloading and (if needed) modifying an existing project template. **This is strongly recommended for beginners** or for those without programming knowledge. The example project demonstrates a research attempt to find statistically significant genes, which stimulate the "chronic inflammation" and "cancer" pathophysiological processes. 

Instructions:
1. Download the zip archive from MEGA and save it to your computer: [todo: link to mega folder]
2. Place the zip archive into any folder in File Explorer on your computer. We suggest giving the folder a meaningful name, such as GOReverseLookup.
3. Extract the zip archive using WinRar or 7zip (or other extractor utilities): `Right click on the zip file` -> `WinRar` -> `Extract Here`
4. Make sure you are connected to the internet, since web requests will be sent to different servers during the analysis
5. Run `GOReverseLookup.exe`; this will open the command prompt and the example should run. After approximately 20 minutes (if the internet connection is stable), the analysis should be finished and the resulting files saved into the `results` folder.

Note: If you experience any **issues** when the .exe runs the example, close the command prompt and run `GOReverseLookup.exe` again. The most likely cause of issues is blocking on the web server's end due to too many requests. The code in background relies heavily on asynchronous requests, and if the server is overloaded, it might start blocking incoming requests. However, request caching is implemented in code - if the same requests are resent to the server, they will be loaded from a previously successfully received request (which are saved in the `cache` folder). Therefore, during a subsequent run of the same program, there will be less requests sent to the servers, diminishing the probability of the server blocking the requests.

If you wish to **carry out your own research analysis**, modify the input.txt file inside the `input_files` folder as per instructions on how to create the input.txt file explained above.

Note: Downloading the entire Mega folder comes with pre-downloaded 3rd party database files, which are used heavily in code when you run the research analysis, but may be outdated. The following 3rd party database files exist in the `data_files` folder:
- `go.obo`
- `goa_human.gaf`
- `mgi_human_ortholog_mapping.txt`
- `rgd_human_ortholog_mapping.txt`
- `xenbase_human_ortholog_mapping.txt`
- `zfin_human_ortholog_mapping.txt`
The download links to all of these files are specified above. If you wish to update these files, you must download them from the above-specified download links. Following the download, you have two options:
a) move the downloaded file into the `data_files` folder and rename it exactly to one of the above names
b) store the downloaded file anywhere in your file system and provide the filepath to the downloaded file inside `input_fules/input.txt`. For example, if you have downloaded an updated version of a go.obo file and you decided to store the go.obo file at the following filepath: `C:/User/Desktop/research/go.obo`, then you need to update the path to go.obo in the `filepaths` section inside `input_fules/input.txt`, like so:
```
...
###filepaths
go_obo_filepath	C:/User/Desktop/research/go.obo
goaf_filepath	data_files/goa_human.gaf
zfin_human_ortho_mapping_filepath	data_files/zfin_human_ortholog_mapping.txt
mgi_human_ortho_mapping_filepath	data_files/mgi_human_ortholog_mapping.txt
rgd_human_ortho_mapping_filepath	data_files/rgd_human_ortholog_mapping.txt
xenbase_human_ortho_mapping_filepath	data_files/xenbase_human_ortholog_mapping.txt
...
```




### GOReverseLookup.exe from scratch
The 

# Roadmap
[todo]: link github projects here

# Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

# License
Distributed using Apache 2.0 License. See `LICENSE.txt` for more information.

# Contact
Aljoša Škorjanc - skorjanc.aljosa@gmail.com
Vladimir Smrkolj - smrkolj.vladimir@gmail.com
