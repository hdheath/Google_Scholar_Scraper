def create_search_term_list(df2, neuromab):
    '''
    Creates a list of search terms based on the provided Neuromab ID and corresponding values
    from the given dataframe.

    Inputs:
    - df2: The dataframe containing the relevant data.
    - neuromab: The Neuromab ID for which the search terms are generated.

    Returns:
    - regex_string: A regular expression string generated from the search terms.
    - changed_parts: The parts of the search terms that have been modified.

    '''
    
    search_terms = []
    search_terms.append(neuromab)
    ai_catalog_pure = df2.loc[df2['Clone'] == neuromab, 'AICatalogPure'].values
    ai_catalog_pure = ai_catalog_pure[0].replace('\\', '')
    search_terms.append(ai_catalog_pure)
    search_terms.append(ai_catalog_pure.replace('-', '&#x02013;'))
    search_terms.append(ai_catalog_pure.replace('-', ' - '))
    search_terms.append(ai_catalog_pure.replace('-', '/'))
    search_terms.append(ai_catalog_pure.replace('-', '&#x02010;'))
    search_terms.append(ai_catalog_pure.replace('-', ' –'))
    search_terms.append(ai_catalog_pure.replace('-', ' -'))
    search_terms.append(ai_catalog_pure.replace('-', '- '))
    search_terms.append(ai_catalog_pure.replace('-', '– '))
    search_terms.append(ai_catalog_pure.replace('-', ' – '))
    search_terms.append(ai_catalog_pure.replace("-", "–") + "\n")
    

    ai_catalog_tcsupe = df2.loc[df2['Clone'] == neuromab, 'AICatalogTCSupe'].values
    ai_catalog_tcsupe = ai_catalog_tcsupe[0].replace('\\', '')
    search_terms.append(ai_catalog_tcsupe)
    search_terms.append(ai_catalog_tcsupe.replace('-', '&#x02013;'))
    search_terms.append(ai_catalog_tcsupe.replace('-', '&#x02010;'))
    search_terms.append(ai_catalog_tcsupe.replace('-', '/'))
    search_terms.append(ai_catalog_tcsupe.replace('-', ' –'))
    search_terms.append(ai_catalog_tcsupe.replace('-', ' -'))
    search_terms.append(ai_catalog_tcsupe.replace('-', '- '))
    search_terms.append(ai_catalog_tcsupe.replace('-', '– '))
    search_terms.append(ai_catalog_tcsupe.replace("-", "–") + "\n")

    # Convert search terms list to a regular expression string
    regex_string = '|'.join(search_terms)
    #print(regex_string)
    
    return regex_string

def DOI_url(PMID):
    '''
    Description:
    Generates a DOI link for a given PubMed ID (PMID) by scraping the PubMed website.

    Inputs:
    - PMID: The PubMed ID for which the DOI link is generated.

    Returns:
    - doi_link: The generated DOI link.
    - 'NA' if the DOI link cannot be generated.

    '''
    url = f'https://pubmed.ncbi.nlm.nih.gov/{PMID}/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
    }
    response = requests.get(url, headers=headers)

    content = response.text

    text_lines = response.text.split('\n')  # Split response text into lines

    pattern_doi = 'doi'

    doi_pattern = re.search(pattern_doi, response.text)
    if doi_pattern:
        # Extract the DOI from the link pattern
        doi = doi_pattern.group(0).split('/')[-1]
        # Find the index of the DOI in the response text
        doi_index = response.text.find(doi)
        comma_index = response.text.find(',', doi_index)
        # Print the text up until the comma after the DOI
        doi = (response.text[doi_index+len(doi)+1:comma_index])
        doi_link = f"https://doi.org/{doi}"
        #print(doi_link)
        return doi_link
    else:
        print(f'Doi could not be generated for {url}')
        df.at[index, 'URL'] = url
        return 'NA'


def pdf_function(pdf_url, pattern, neuromabs, df2, df, index, developer_mode, headers, neuromab_website_df):
    '''
    Description:
    Performs verification of Neuromab antibodies by scraping PDF content or HTML content from a given URL.
    Updates the corresponding columns in the dataframe with the verification results.

    Args:
    - pdf_url: The URL of the PDF file or HTML page to be scraped.
    - pattern: The pattern to search for in the PDF or HTML content.
    - neuromabs: Neuromab IDs separated by commas, corresponding to the antibodies to be verified.
    - df2: The dataframe containing the relevant data.
    - df: The dataframe to update with the verification results.
    - index: The index of the row in the dataframe being processed.
    - developer_mode: A flag indicating whether to display additional information for debugging purposes.
    - headers: Headers to be included in the requests sent to the server.

    Returns:
    None - annotates dataframe accordingly based on result
    '''
    
    response = requests.get(pdf_url, headers = headers)
    content_type = response.headers.get('content-type')
    
    if 'pdf' in content_type or 'force-download' in content_type:
        try:
            combined_text = "" 
            pdf = PyPDF2.PdfFileReader(io.BytesIO(response.content))
            found = False  # Flag to track if pattern is found
            not_found_neuromabs = []  # Initialize an empty list to store not found Neuromabs
            for page_num in range(pdf.getNumPages()):
                page = pdf.getPage(page_num)
                text = page.extractText()
                combined_text += text  # Concatenate the text from each page
            if re.search(pattern, combined_text, re.IGNORECASE):
                found = True
                df.at[index, 'NeuroMab Verification'] = 'OK'
                df.at[index, 'Method of Verification'] = 'PDF scrape'
                if developer_mode:
                    print('FOUND')
                if not pd.isna(neuromabs):
                    for neuromab in neuromabs.split(', '):
                        search_terms = create_search_term_list(df2, neuromab)
                        if (re.search(search_terms, combined_text, re.IGNORECASE)):
                            continue
                        else:
                            not_found_neuromabs.append(neuromab)

            if found:
                if not_found_neuromabs:
                    df.at[index, 'Antibody Verification'] = ', '.join(not_found_neuromabs)
                    if developer_mode:
                        print(f"PDF Scraper : '{', '.join(not_found_neuromabs)}' not found in {pdf_url}")
                else:
                    df.at[index, 'Antibody Verification'] = 'OK'
                    if developer_mode:
                        print('ALL ABs FOUND')

            else:
                df.at[index, 'NeuroMab Verification'] = f'Manual verification needed'
                df.at[index, 'URL'] = pdf_url
                if developer_mode:  
                    print(f"NEUROMAB NOT FOUND in : {pdf_url}")
                    
        except Exception as e:
            df.at[index, 'NeuroMab Verification'] = f'Manual verification needed'
            
        df.at[index, 'Method of Verification'] = 'PDF scrape'
    
    else:
        try:
            new_response = requests.get(pdf_url, headers = headers)
            paper_doc = BeautifulSoup(new_response.text, 'html.parser')
            paper_doc = paper_doc.prettify()
            Scrape_for_NeuroMab(pdf_url, paper_doc, df, df2, neuromabs,pattern, index, developer_mode)
            df.at[index, 'Method of Verification'] = 'HTML search from Google Link'

        except Exception as e:
            if 'object of type' in str(e):
                df.at[index, 'NeuroMab Verification'] = f'Cannot access html content'
            else:
                df.at[index, 'NeuroMab Verification'] = f'Manual verification needed'
            df.at[index, 'URL'] = pdf_url


def Create_PMC_url(PMID, headers, df, index):
    '''
    Description:
    Creates a URL for a given PubMed ID (PMID) to access the corresponding article in PMC (PubMed Central).
    Updates the dataframe with the method of verification and the generated URL.

    Inputs:
    - PMID: The PubMed ID for which the PMC URL is generated.
    - headers: Headers to be included in the requests sent to the server.
    - df: The dataframe to update with the verification results.
    - index: The index of the row in the dataframe being processed.

    Returns:
    - new_url: The generated URL for accessing the article in PMC.

    '''
    try:
        handle = Entrez.esummary(db="pubmed", id=PMID)
        record = Entrez.read(handle)
        handle.close()
        pmcid = record[0]['ArticleIds']['pmc']
        # new_url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/'
        new_url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmcid}/unicode'
        # https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/37190086/unicode
        df.at[index, 'Method of Verification'] = 'PMCID'
     
    except Exception as e:
        print(f"Error occurred: {e}, Going to DOI URL")
        df.at[index, 'Method of Verification'] = 'DOI'
        new_url = DOI_url(PMID)
        
    return new_url


def Scrape_for_NeuroMab(url, paper_doc, df, df2, neuromabs, pattern, pdf_url, index, developer_mode, neuromab_website_df):
    '''
    Description:
    Scrape the paper document for NeuroMab information based on a given pattern.
    Update the dataframe with the verification results and perform additional actions based on the results.

    Inputs:
    - url: The URL of the paper.
    - paper_doc: The paper document to be scraped.
    - df: The dataframe to update with the verification results.
    - df2: The additional dataframe used for search term generation.
    - neuromabs: The Neuromab IDs to search for in the paper document.
    - pattern: The pattern to search for in the paper document.
    - pdf_url: The URL of the PDF associated with the paper.
    - index: The index of the row in the dataframe being processed.
    - developer_mode: A flag indicating whether developer mode is enabled.

    '''
    if re.search(pattern, paper_doc, re.IGNORECASE):
        df.at[index, 'NeuroMab Verification'] = 'OK'
        if developer_mode:
            print('FOUND Neuromab')
        Scrape_for_ABs(url, paper_doc, df, df2, neuromabs, index, neuromab_website_df, developer_mode)

    else:
        if any(keyword in str(url) for keyword in ['sciencedirect', 'wiley', 'researchgate', 'jbc', 'pnas','academia','tandf','nature','cell','embopress','journals.physiology','proquest', 'jlr','sagepub','prism','sol3','publicnow','doi']):
            df.at[index, 'URL'] = url
            df.at[index, 'NeuroMab Verification'] = f'Manual verification needed'
            print(f'Manual verification needed for {url}')
        else:
            df.at[index, 'NeuroMab Verification'] = f"Neuromab not found"
            pdf_function(pdf_url, pattern, neuromabs, df2, df, index, developer_mode, headers, neuromab_website_df)
            print(f"NeuroMab not found in {url}")
        
        df.at[index, 'URL'] = url


def Scrape_for_ABs(url, paper_doc, df, df2, neuromabs, index, neuromab_website_df, developer_mode):
    '''
    Scrape the paper document for Antibody (AB) information based on search terms generated from Neuromab IDs.
    Update the dataframe with the verification results.

    Inputs:
    - url: The URL of the paper.
    - paper_doc: The paper document to be scraped.
    - df: The dataframe to update with the verification results.
    - df2: The additional dataframe used for search term generation.
    - neuromabs: The Neuromab IDs to search for in the paper document.
    - index: The index of the row in the dataframe being processed.

    '''
    # Initialize an empty list to store not found Neuromabs
    not_found_neuromabs = []
    if not pd.isna(neuromabs):
        for neuromab in neuromabs.split(', '):
            search_terms = create_search_term_list(df2,neuromab)
            found = False
            for term in search_terms:
                if re.search(term, paper_doc, re.IGNORECASE):
                    found = True
                    #print(f"'{term}' found in the text for Neuromab '{neuromab}'")
                    break
            if not found:
                not_found_neuromabs.append(neuromab)
                if developer_mode:
                    print(f"'{neuromab}' Not found in {url}")

    # Add the not found Neuromabs as a comma-separated string to the 'Verification' column
    if len (not_found_neuromabs) > 0:
        df.at[index, 'Antibody Verification'] = ', '.join(not_found_neuromabs)
        df.at[index, 'URL'] = url
    else:
        df.at[index, 'Antibody Verification'] = 'OK'
        if developer_mode:
            print('FOUND ALL ABs')


def scrape_for_target(paper_doc, df, index, neuromab_website_df):
    target_values = neuromab_website_df['Target'].tolist()
    found_targets = []
    found = False
    for target in target_values:
        for word in paper_doc.split():
            similarity = fuzz.ratio(target.lower(), word.lower())
            if similarity > 95:
                found_targets.append(target)
                found = True 
                print(f'Target: {target} Word : {word}')
    if found == True:
        df.at[index, 'Target'] = ', '.join(found_targets)


def path_to_merged_df_w_pubmed():
    '''
    Description:
    Create the file path for the merged dataframe with PubMed information.

    Returns:
    - path: The file path for the merged dataframe with PubMed information.
    
    '''
    
    path = f'{GS_directory}/merged_df_w_pubmed.csv'
    return path

def verify_GS_results(df, df2, leftoff, developer_mode):
    '''
    Description:
    Verify the results in the Google Sheets dataframe by scraping PubMed and performing NeuroMab and Antibody verification.
    Update the dataframe with the verification results and save the updated dataframe as a CSV file.

    Inputs:
    - df: The path to the Google Sheets dataframe.
    - df2: The path to the additional dataframe used for search term generation.
    - leftoff: The index from which to start iterating over the rows in the dataframe.
    - developer_mode: A flag indicating whether developer mode is enabled.
    '''
    
    df = pd.read_csv(df, encoding='utf-8' )
    df['PMID'] = df['PMID'].astype(str)
    df2 = pd.read_excel(df2)
    # Define the regular expression pattern to search for
    pattern = r'(NeuroMAB|NeuroM ab|Neuromab|Neuro Mab|NeuroMab|Antibodies,?\s?Inc\.?|Antibodies Inc)'
    for index, row in df[leftoff:].iterrows():
        neuromabs = row['Neuromab(s)']
        pdf_url = row['PDF Link']
        PMID = row['PMID']
        print(f"Iterating over row: {index}")
        try:
            if len(PMID) > 3 or (not pd.isna(PMID) and PMID != 'nan'):
                url = Create_PMC_url(PMID, headers, df, index)
                new_response = requests.get(url, headers=headers)
                paper_doc = BeautifulSoup(new_response.text, 'html.parser')
                paper_doc = paper_doc.prettify()
                Scrape_for_NeuroMab(url, paper_doc, df, df2, neuromabs, pattern, pdf_url, index, developer_mode, neuromab_website_df)
            else:
                if not pd.isna(pdf_url):
                    pdf_function(pdf_url, pattern, neuromabs, df2, df, index, developer_mode, headers, neuromab_website_df)
                else:
                    df.at[index, 'NeuroMab Verification'] = f'Manual verification needed'
                    df.at[index, 'URL'] = url
            # autosave every 100 rows
            if index % 100 == 0:
                df.to_csv(f'{GS_directory}/merged_df_w_pubmed_&_verified.csv', encoding='utf-8')

        except Exception as e:
            print(f"Error occurred: {e} for {url}")
            df.at[index, 'NeuroMab Verification'] = f'Manual verification needed'
            df.at[index, 'URL'] = url
            
    # remove unnamed columns
    for col in df.columns:
        if col.startswith("Unnamed"):
            df = df.drop(col, axis=1)
            
    df.to_csv(f'{GS_directory}/merged_df_w_pubmed_&_verified.csv', encoding='utf-8')
