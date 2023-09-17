import os
import requests

from ..parse.GOAFParser import GOAnnotationsFile

import logging

# from logging import config
# config.fileConfig("../logging_config.py")
logger = logging.getLogger(__name__)


class HumanOrthologFinder:
    def __init__(
        self,
        goaf: GOAnnotationsFile,
        zfin_filepath: str = "",
        xenbase_filepath: str = "",
        mgi_filepath: str = "",
        rgd_filepath: str = "",
    ):
        """
        Constructs the HumanOrthologFinder, which uses file-based search on pre-downloaded 3rd party database ortholog mappings to find
        ortholog genes.

        Parameters:
          - (GOAnnotationsFile) goaf: A GOAnnotationsFile instance. Good practice is to pass the goaf from ReverseLookup instance.
          - (str) zfin_filepath: Filepath to the Zebrafish Information Network human ortholog mapping file, found at https://zfin.org/downloads -> Orthology Data -> Human and Zebrafish Orthology -> link = https://zfin.org/downloads/human_orthos.txt
          - (str) xenbase_filepath: Filepath to the Xenbase human ortholog mapping file, found at https://www.xenbase.org/ -> Download -> Data Download (https://www.xenbase.org/xenbase/static-xenbase/ftpDatafiles.jsp) -> Data Reports -> Orthology -> Xenbase genes to Human Entrez Genes -> link: https://download.xenbase.org/xenbase/GenePageReports/XenbaseGeneHumanOrthologMapping.txt
          - (str) mgi_filepath: Filepath to the Mouse Genome Informatics human ortholog mapping file, found at: https://www.informatics.jax.org/ -> Download (https://www.informatics.jax.org/downloads/reports/index.html) -> Vertebrate homology -> Human and Mouse Homology Classes with Sequence information (tab-delimited) -> link = https://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt
          - (str) rgd_filepath: Filepath to the Rat Genoma Database human ortholog mapping file, found at: https://rgd.mcw.edu/ -> Data -> Download -> data/release -> RGD_ORTHOLOGS.txt -> link = https://download.rgd.mcw.edu/data_release/RGD_ORTHOLOGS.txt
                                TODO: RGD also offers various other ortholog files, of use may be the Ensembl ortholog file, which also offers some ensembl ids: RGD_ORTHOLOGS_Ensembl.txt (https://download.rgd.mcw.edu/data_release/RGD_ORTHOLOGS_Ensembl.txt)

        The files are expected to reside in app/goreverselookup/data_files/ folder.
        """
        self.zfin = ZFINHumanOrthologFinder(filepath=zfin_filepath)
        self.xenbase = XenbaseHumanOrthologFinder(filepath=xenbase_filepath)
        self.mgi = MGIHumanOrthologFinder(filepath=mgi_filepath)
        self.rgd = RGDHumanOrthologFinder(filepath=rgd_filepath)
        self.goaf = goaf

    def find_human_ortholog(self, product):
        """
        Finds the human ortholog for the given product.

        Args:
            product (str): The product (id) for which to find the human ortholog.

        Returns:
            The human gene symbol or None if no human ortholog was found.
        """
        if "ZFIN" in product:
            result = self.zfin.find_human_ortholog(
                product
            )  # returns [0]: gene symbol, [1]: long name of the gene
            human_gene_symbol = result[0] if result is not None else None
            # human_gene_symbol = self.zfin.find_human_ortholog(product)[0]
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        elif "Xenbase" in product:
            result = self.xenbase.find_human_ortholog(product)
            human_gene_symbol = result[0] if result is not None else None
            # human_gene_symbol = self.xenbase.find_human_ortholog(product)[0]
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        elif "MGI" in product:
            human_gene_symbol = self.mgi.find_human_ortholog(product)
            human_gene_symbol = (
                human_gene_symbol if (human_gene_symbol is not None) else None
            )
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        elif "RGD" in product:
            human_gene_symbol = self.rgd.find_human_ortholog(product)
            human_gene_symbol = (
                human_gene_symbol if (human_gene_symbol is not None) else None
            )
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        else:
            logger.info(f"No database found for {product}")

        return human_gene_symbol

    async def find_human_ortholog_async(self, product):
        if "ZFIN" in product:
            result = await self.zfin.find_human_ortholog_async(
                product
            )  # returns [0]: gene symbol, [1]: long name of the gene
            return result[0] if result is not None else None
            # human_gene_symbol = self.zfin.find_human_ortholog(product)[0]
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        elif "Xenbase" in product:
            result = await self.xenbase.find_human_ortholog_async(product)
            return result[0] if result is not None else None
            # human_gene_symbol = self.xenbase.find_human_ortholog(product)[0]
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        elif "MGI" in product:
            human_gene_symbol = await self.mgi.find_human_ortholog_async(product)
            return human_gene_symbol if (human_gene_symbol is not None) else None
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        elif "RGD" in product:
            human_gene_symbol = await self.rgd.find_human_ortholog_async(product)
            return human_gene_symbol if (human_gene_symbol is not None) else None
            # return None if "Error" in human_gene_symbol else human_gene_symbol
        else:
            logger.info(f"No database found for {product}")
            return None


class ZFINHumanOrthologFinder(HumanOrthologFinder):
    def __init__(self, filepath: str = ""):
        """
        This class allows the user to search Zebrafish human orthologs. The human orthologs mapping file should be downloaded
        from the ZFIN webpage: https://zfin.org/downloads -> Orthology Data -> Human and Zebrafish Orthology -> link = https://zfin.org/downloads/human_orthos.txt

        Parameters:
          - (str) filepath: if left to default value, self._filepath will be set to "app/goreverselookup/data_files/zfin_human_ortholog_mapping.txt", else
                            self._filepath will be set to {filepath}
        """
        if filepath == "":
            self._filepath = (
                "data_files/zfin_human_ortholog_mapping.txt"
            )
        else:
            self._filepath = filepath
        self._check_file()
        with open(self._filepath, "r") as read_content:
            self._readlines = read_content.readlines()
        logger.info(f"ZFINHumanOrthologFinder setup ok: {len(self._readlines)} readlines.")

    def _check_file(self):
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        if not os.path.exists(self._filepath):
            url = "https://zfin.org/downloads/human_orthos.txt"
            response = requests.get(url)
            with open(self._filepath, "wb") as f:
                f.write(response.content)
            logger.info(
                f"Downloaded zfin_human_ortholog_mapping.txt to {self._filepath}"
            )

    def find_human_ortholog(self, product_id):
        """
        If product_id is from the ZFIN database, searches through the zebrafish-human orthologs and returns the name of the
        symbol of the human gene ortholog.

        Returns:
        - [0]: gene symbol
        - [1]: long name of the gene
        """

        def _zfin_get_human_gene_symbol_from_line(line):
            """
            Splits zfin line and retrieves human gene symbol (full caps of zebrafish gene symbol)
            """
            # better, as zfin human ortholog sometimes has different name than the zebrafish gene
            human_symbol = line.split("\t")[3]
            human_gene_name = line.split("\t")[4]
            return (
                human_symbol,
                human_gene_name,
            )  # look at zfin orthologs txt file (in data_files) -> when you higlight a row, you see a TAB as '->' and a SPACEBAR as '.' -> splitting at \t means every [3] linesplit element is the human gene name

        product_id = product_id.split(":")[1]  # eliminates 'ZFIN:'
        for line in self._readlines:
            if product_id in line:
                e = _zfin_get_human_gene_symbol_from_line(line)
                human_symbol = e[0]
                human_gene_name = e[1]
                # logger.info(f"[ Returning human symbol {human_symbol} and {human_gene_name}")
                return human_symbol, human_gene_name
        return None
        # return [f"ZfinError_No-human-ortholog-found:product_id={product_id}"]

    async def find_human_ortholog_async(self, product_id):
        """
        If product_id is from the ZFIN database, searches through the zebrafish-human orthologs and returns the name of the
        symbol of the human gene ortholog.

        Returns:
        - [0]: gene symbol
        - [1]: long name of the gene
        """

        def _zfin_get_human_gene_symbol_from_line(line):
            """
            Splits zfin line and retrieves human gene symbol (full caps of zebrafish gene symbol)
            """
            # better, as zfin human ortholog sometimes has different name than the zebrafish gene
            human_symbol = line.split("\t")[3]
            human_gene_name = line.split("\t")[4]
            return (
                human_symbol,
                human_gene_name,
            )  # look at zfin orthologs txt file (in data_files) -> when you higlight a row, you see a TAB as '->' and a SPACEBAR as '.' -> splitting at \t means every [3] linesplit element is the human gene name

        product_id = product_id.split(":")[1]  # eliminates 'ZFIN:'
        for line in self._readlines:
            if product_id in line:
                e = _zfin_get_human_gene_symbol_from_line(line)
                human_symbol = e[0]
                human_gene_name = e[1]
                # logger.info(f"[ Returning human symbol {human_symbol} and {human_gene_name}")
                return human_symbol, human_gene_name
        return None


class XenbaseHumanOrthologFinder(HumanOrthologFinder):
    def __init__(self, filepath: str = ""):
        """
        This class allows the user to search Xenbase human orthologs. The human orthologs mapping file should be downloaded
        from the Xenbase webpage: https://www.xenbase.org/ -> Download -> Data Download (https://www.xenbase.org/xenbase/static-xenbase/ftpDatafiles.jsp) -> Data Reports -> Orthology -> Xenbase genes to Human Entrez Genes -> link: https://download.xenbase.org/xenbase/GenePageReports/XenbaseGeneHumanOrthologMapping.txt

        Parameters:
          - (str) filepath: if left to default value, self._filepath will be set to "app/goreverselookup/data_files/xenbase_human_ortholog_mapping.txt", else
                            self._filepath will be set to {filepath}
        """
        if filepath == "":
            self._filepath = (
                "data_files/xenbase_human_ortholog_mapping.txt"
            )
        else:
            self._filepath = filepath

        self._check_file()
        with open(self._filepath, "r") as read_content:
            self._readlines = read_content.readlines()
        logger.info(f"XenbaseHumanOrthologFinder setup ok: {len(self._readlines)} readlines.")

    def _check_file(self):
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        if not os.path.exists(self._filepath):
            url = "https://download.xenbase.org/xenbase/GenePageReports/XenbaseGeneHumanOrthologMapping.txt"
            response = requests.get(url)
            with open(self._filepath, "wb") as f:
                f.write(response.content)
            logger.info(
                f"Downloaded xenbase_human_ortholog_mapping.txt to {self._filepath}"
            )

    def find_human_ortholog(self, product_id):
        """
        Attempts to find a human ortholog from the xenbase database.
        Parameters:
        - product_id: eg. Xenbase:XB-GENE-495335 or XB-GENE-495335
        Returns:
        - [0]: symbol of the human ortholog gene (eg. rsu1) or 'XenbaseError_no-human-ortholog-found'
        - [1]: long name of the gene
        """

        def _xenbase_get_human_symbol_from_line(line):
            """Splits xenbase line at tabs and gets human gene symbol (in full caps)"""
            symbol = str(line.split("\t")[2]).upper()
            name = str(line.split("\t")[3])
            return symbol, name

        product_id_short = ""
        if ":" in product_id:
            product_id_short = product_id.split(":")[1]
        else:
            product_id_short = product_id

        for line in self._readlines:
            if product_id_short in line:
                e = _xenbase_get_human_symbol_from_line(line)
                human_symbol = e[0]
                human_gene_name = e[1]
                logger.info(
                    f"Found human ortholog {human_symbol}, name = {human_gene_name} for"
                    f" xenbase gene {product_id}"
                )
                return human_symbol, human_gene_name
        logger.info(
            f"DID NOT find human ortholog for xenbase gene {product_id}"
        )
        return None


    async def find_human_ortholog_async(self, product_id):
        """
        Attempts to find a human ortholog from the xenbase database.
        Parameters:
        - product_id: eg. Xenbase:XB-GENE-495335 or XB-GENE-495335
        Returns:
        - [0]: symbol of the human ortholog gene (eg. rsu1) or 'XenbaseError_no-human-ortholog-found'
        - [1]: long name of the gene
        """

        def _xenbase_get_human_symbol_from_line(line):
            """Splits xenbase line at tabs and gets human gene symbol (in full caps)"""
            symbol = str(line.split("\t")[2]).upper()
            name = str(line.split("\t")[3])
            return symbol, name

        product_id_short = ""
        if ":" in product_id:
            product_id_short = product_id.split(":")[1]
        else:
            product_id_short = product_id

        for line in self._readlines:
            if product_id_short in line:
                e = _xenbase_get_human_symbol_from_line(line)
                human_symbol = e[0]
                human_gene_name = e[1]
                logger.info(
                    f"Found human ortholog {human_symbol}, name = {human_gene_name} for"
                    f" xenbase gene {product_id}"
                )
                return human_symbol, human_gene_name
        logger.info(
            f"DID NOT find human ortholog for xenbase gene {product_id}"
        )
        return None


class MGIHumanOrthologFinder(HumanOrthologFinder):
    def __init__(self, filepath: str = ""):
        """
        This class allows the user to search MGI human orthologs. The human orthologs mapping file should be downloaded
        from the MGI webpage: Filepath to the Mouse Genome Informatics human ortholog mapping file, found at:
        https://www.informatics.jax.org/ -> Download (https://www.informatics.jax.org/downloads/reports/index.html) -> Vertebrate homology -> Human and Mouse Homology Classes with Sequence information (tab-delimited) -> link = https://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt

        Parameters:
          - (str) filepath: if left to default value, self._filepath will be set to "app/goreverselookup/data_files/mgi_human_ortholog_mapping.txt", else
                            self._filepath will be set to {filepath}
        """
        if filepath == "":
            self._filepath = (
                "data_files/mgi_human_ortholog_mapping.txt"
            )
        else:
            self._filepath = filepath

        self._check_file()
        with open(self._filepath, "r") as read_content:
            self._readlines = read_content.readlines()
        logger.info(
            f"MGIHumanOrthologFinder setup ok: {len(self._readlines)} readlines."
        )

    def _check_file(self):
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        if not os.path.exists(self._filepath):
            url = "https://www.informatics.jax.org/downloads/reports/HOM_MouseHumanSequence.rpt"
            response = requests.get(url)
            with open(self._filepath, "wb") as f:
                f.write(response.content)
            logger.info(
                f"Downloaded mgi_human_ortholog_mapping.txt to {self._filepath}"
            )

    def find_human_ortholog(self, product_id):
        """
        Attempts to find a human ortholog from the mgi database.
        Parameters: gene-id eg. MGI:MGI:98480
        Returns: symbol of the human ortholog gene or "MgiError_no-human-ortholog-found".

        Note: Cannot return longer gene name from the MGI .txt file, since it doesn't contain the longer name
        """

        def _mgi_get_human_symbol_from_line(line, line_index):
            """
            Splits mgi line at tabs and gets human gene symbol
            """
            split = line.split("\t")
            if split[1] != "human":
                # try i+2 to check one line further down
                line = self._readlines[line_index + 2]
                second_split = line.split("\t")
                if second_split[1] == "human":
                    logger.debug("Found keyword 'human' on secondpass line querying.")
                    return second_split[3]
                else:
                    # this still means no human ortholog!
                    # example: MGI:2660935 (Prl3d2) contains no "human" (neither i+1 nor i+2), also checked uniprot and no human gene for prl3d2 exists
                    return f"[MgiError_No-human-ortholog-found:product_id={product_id}"
            else:
                return split[3]

        # logger.debug(f"Starting MGI search for {product_id}")
        product_id_short = ""
        if ":" in product_id:
            split = product_id.split(":")
            if len(split) == 3:
                product_id_short = split[2]  # in case of MGI:xxx:xxxxx
            elif len(split) == 2:
                product_id_short = split[1]  # in case of MGI:xxxxx
        else:
            product_id_short = product_id

        i = 0
        for line in self._readlines:
            if product_id_short in line:
                # if "mouse" gene smybol is found at line i, then human gene symbol will be found at line i+1
                human_symbol = _mgi_get_human_symbol_from_line(
                    self._readlines[i + 1], i
                )
                if "MgiError" in human_symbol:
                    logger.info(
                        f"DID NOT find human ortholog for mgi gene {product_id}"
                    )
                    return None
                logger.info(
                    f"Found human ortholog {human_symbol} for mgi gene {product_id}"
                )
                return human_symbol  # return here doesnt affect line counter 'i', since if gene is found i is no longer needed
            i += 1
        logger.info(
            f"DID NOT find human ortholog for mgi gene {product_id}"
        )
        return None

    async def find_human_ortholog_async(self, product_id):
        """
        Attempts to find a human ortholog from the mgi database.
        Parameters: gene-id eg. MGI:MGI:98480
        Returns: symbol of the human ortholog gene or "MgiError_no-human-ortholog-found".

        Note: Cannot return longer gene name from the MGI .txt file, since it doesn't contain the longer name
        """

        def _mgi_get_human_symbol_from_line(line, line_index):
            """
            Splits mgi line at tabs and gets human gene symbol
            """
            split = line.split("\t")
            if split[1] != "human":
                # try i+2 to check one line further down
                line = self._readlines[line_index + 2]
                second_split = line.split("\t")
                if second_split[1] == "human":
                    logger.debug("Found keyword 'human' on secondpass line querying.")
                    return second_split[3]
                else:
                    # this still means no human ortholog!
                    # example: MGI:2660935 (Prl3d2) contains no "human" (neither i+1 nor i+2), also checked uniprot and no human gene for prl3d2 exists
                    return f"[MgiError_No-human-ortholog-found:product_id={product_id}"
            else:
                return split[3]

        logger.debug(f"Starting MGI search for {product_id}")
        product_id_short = ""
        if ":" in product_id:
            split = product_id.split(":")
            if len(split) == 3:
                product_id_short = split[2]  # in case of MGI:xxx:xxxxx
            elif len(split) == 2:
                product_id_short = split[1]  # in case of MGI:xxxxx
        else:
            product_id_short = product_id

        i = 0
        for line in self._readlines:
            if product_id_short in line:
                # if "mouse" gene smybol is found at line i, then human gene symbol will be found at line i+1
                logger.debug(
                    f"i = {i}, product_id_short = {product_id_short}, line = {line}"
                )
                human_symbol = _mgi_get_human_symbol_from_line(
                    self._readlines[i + 1], i
                )
                if "MgiError" in human_symbol:
                    logger.info(
                        f"Couldn't find human ortholog for mgi gene {product_id}"
                    )
                    return None
                logger.info(
                    f"Found human ortholog {human_symbol} for mgi gene {product_id}"
                )
                return human_symbol  # return here doesnt affect line counter 'i', since if gene is found i is no longer needed
            i += 1
        logger.info(
            f"DID NOT find human ortholog for mgi gene {product_id}"
        )
        return None


class RGDHumanOrthologFinder(HumanOrthologFinder):
    def __init__(self, filepath: str = ""):
        """
        This class allows the user to search RGD human orthologs. The human orthologs mapping file should be downloaded
        from the RGD webpage: https://rgd.mcw.edu/ -> Data -> Download -> data/release -> RGD_ORTHOLOGS.txt -> link = https://download.rgd.mcw.edu/data_release/RGD_ORTHOLOGS.txt
                              TODO: RGD also offers various other ortholog files, of use may be the Ensembl ortholog file, which also offers some ensembl ids: RGD_ORTHOLOGS_Ensembl.txt (https://download.rgd.mcw.edu/data_release/RGD_ORTHOLOGS_Ensembl.txt)

        Parameters:
          - (str) filepath: if left to default value, self._filepath will be set to "app/goreverselookup/data_files/rgd_human_ortholog_mapping.txt", else
                            self._filepath will be set to {filepath}
        """
        if filepath == "":
            self._filepath = (
                "data_files/rgd_human_ortholog_mapping.txt"
            )
        else:
            self._filepath = filepath

        self._check_file()
        with open(self._filepath, "r") as read_content:
            self._readlines = read_content.readlines()
        logger.info(
            f"RGDHumanOrthologFinder setup ok: {len(self._readlines)} readlines."
        )

    def _check_file(self):
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        if not os.path.exists(self._filepath):
            url = "https://download.rgd.mcw.edu/pub/data_release/orthologs/RGD_ORTHOLOGS_Ortholog.txt"
            response = requests.get(url)
            with open(self._filepath, "wb") as f:
                f.write(response.content)
            logger.info(
                f"Downloaded rgd_human_ortholog_mapping.txt to {self._filepath}"
            )

    def find_human_ortholog(self, product_id):
        """
        Attempts to find a human ortholog from the RGD (rat genome database)
        Returns: human gene symbol

        Note: longer name of the gene cannot be returned, since it is not specified in the rgd txt file
        """

        def _rgd_get_human_symbol_from_line(line):
            """Splits rgd line at tabs and gets human gene smybol"""
            # also clears whitespace from linesplit (which is split at tab). Some lines in RGD db text file had whitespace instead of \t -> clear whitespace from array to resolve
            # example: linesplit = ['Ang2', '1359373', '497229', '', '', '', '', 'Ang2', '1624110', '11731', 'MGI:104984', 'RGD', '\n']
            linesplit = line.split("\t")
            result_list = []
            for element in linesplit:
                if element != "":
                    result_list.append(element)
            if len(result_list) >= 4:  # bugfix
                return result_list[3]
            else:
                logger.warning(
                    f"FAULTY LINE IN RGD while searching for {product_id}, linesplit =:"
                    f" {linesplit}"
                )
                return None

        product_id_short = ""
        if ":" in product_id:
            product_id_short = product_id.split(":")[1]
        else:
            product_id_short = product_id

        for line in self._readlines:
            if product_id_short in line:
                line.split("\t")
                human_symbol = _rgd_get_human_symbol_from_line(line)
                logger.info(
                    f"Found human ortholog {human_symbol} for RGD gene {product_id}"
                )
                return human_symbol
        logger.info(
            f"DID NOT find human ortholog for RGD gene {product_id}"
        )
        return None
        # return f"[RgdError_No-human-ortholog-found:product_id={product_id}"

    async def find_human_ortholog_async(self, product_id):
        """
        Attempts to find a human ortholog from the RGD (rat genome database)
        Returns: human gene symbol

        Note: longer name of the gene cannot be returned, since it is not specified in the rgd txt file
        """

        def _rgd_get_human_symbol_from_line(line):
            """Splits rgd line at tabs and gets human gene smybol"""
            # also clears whitespace from linesplit (which is split at tab). Some lines in RGD db text file had whitespace instead of \t -> clear whitespace from array to resolve
            # example: linesplit = ['Ang2', '1359373', '497229', '', '', '', '', 'Ang2', '1624110', '11731', 'MGI:104984', 'RGD', '\n']
            linesplit = line.split("\t")
            result_list = []
            for element in linesplit:
                if element != "":
                    result_list.append(element)
            if len(result_list) >= 4:  # bugfix
                return result_list[3]
            else:
                logger.warning(
                    f"FAULTY LINE IN RGD while searching for {product_id}, linesplit =:"
                    f" {linesplit}"
                )
                return None

        product_id_short = ""
        if ":" in product_id:
            product_id_short = product_id.split(":")[1]
        else:
            product_id_short = product_id

        for line in self._readlines:
            if product_id_short in line:
                line.split("\t")
                human_symbol = _rgd_get_human_symbol_from_line(line)
                logger.info(
                    f"Found human ortholog {human_symbol} for RGD gene {product_id}"
                )
                return human_symbol
        logger.info(
            f"DID NOT find human ortholog for RGD gene {product_id}"
        )
        return None
