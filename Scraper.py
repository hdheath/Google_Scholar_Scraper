def RandomWait():
    '''
    Description:
    This returns a random time between 5 and 10 sec for the 
    program to wait between requests in an attempt to limit being dropped from google
    
    '''
    return random.randint(5, 10)

def CreateURLneuromabOnly():
    '''
    Description:
    This function creates a url for the neuromab only search to compare the search 
    results to the found number of items 
    
    Returns: 
    url to search for NeuroMab only searches
    '''
    return f'https://scholar.google.com/scholar?q=%22Neuromab%22&hl=en&as_sdt=0%2C5&as_ylo={(SetYearParameters())[0]}&as_yhi={(SetYearParameters())[0]}'

def parse(parser: Callable, organic_results_data: Callable):
    '''
    Arugments:
    - parser:  Lexbor parser from scrape_google_scholar_organic_results() function.
    - organic_results_data: List to append data to. List origin location is scrape_google_scholar_organic_results() function. Line 104.
    
    This function parses data from Google Scholar Organic results and appends data to a List.
    
    It's used by scrape_google_scholar_organic_results().
    
    It returns nothing as it appends data to `organic_results_data`, 
    which appends it to `organic_results_data` List in the scrape_google_scholar_organic_results() function.
    '''
    
    for result in parser.css('.gs_r.gs_or.gs_scl'):
        try:
            title: str = result.css_first('.gs_rt').text()
        except: title = None

        try:
            title_link: str = result.css_first('.gs_rt a').attrs['href']
        except: title_link = None

        try:
            publication_info: str = result.css_first('.gs_a').text()
        except: publication_info = None

        try:
            snippet: str = result.css_first('.gs_rs').text()
        except: snippet = None

        try:
            # if Cited by is present in inline links, it will be extracted
            cited_by_link = ''.join([link.attrs['href'] for link in result.css('.gs_ri .gs_fl a') if 'Cited by' in link.text()])
        except: cited_by_link = None
        
        try:
            # if Cited by is present in inline links, it will be extracted and type cast it to integer
            cited_by_count = int(''.join([re.search(r'\d+', link.text()).group() for link in result.css('.gs_ri .gs_fl a') if 'Cited by' in link.text()]))
        except: cited_by_count = None
        
        try:
            pdf_file: str = result.css_first('.gs_or_ggsm a').attrs['href']
        except: pdf_file = None

        organic_results_data.append({
            'title': title,
            'title_link': title_link,
            'publication_info': publication_info,
            'snippet': snippet if snippet else None,
            'cited_by_link': f'https://scholar.google.com{cited_by_link}' if cited_by_link else None,
            'cited_by_count': cited_by_count if cited_by_count else None,
            'pdf_file': pdf_file
        })

def scrape_google_scholar_organic_results(
                                        query: str,
                                        pagination: bool = False,
                                        operating_system: str = 'Windows' or 'Linux',
                                        year_start: int = None,
                                        year_end: int = None,
                                        save_to_csv: bool = False, 
                                        save_to_json: bool = False
                                        ) -> List[Dict[str, str]]:
    '''
    Extracts data from Google Scholar Organic resutls page:
    - title: str
    - title_link: str
    - publication_info: str 
    - snippet: str
    - cited_by_link: str 
    - cited_by_count: int
    - pdf_file: str
    
    Arguments:
    - query: str. Search query. 
    - pagination: bool. Enables or disables pagination.
    - operating_system: str. 'Windows' or 'Linux', Checks for operating system to either run Windows or Linux verson of chromedriver
    
    Usage:
    data = scrape_google_scholar_organic_results(query='blizzard', pagination=False, operating_system='win') # pagination defaults to False 
    
    for organic_result in data:
        print(organic_result['title'])
        print(organic_result['pdf_file'])
    '''
    assert year_start and year_end
    if year_start or year_end:
        assert year_start and year_end
        assert year_start <= year_end

    # selenium stealth
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # checks for operating system to either run Windows or Linux verson of chromedriver
    # expects to have chromedriver near the runnable file
    if operating_system is None:
        raise Exception('Please provide your OS to `operating_system` argument: "Windows" or "Linux" for script to operate.')
    
    if operating_system.lower() == 'windows' or 'win':
        driver = webdriver.Chrome(options=options, service=Service(executable_path='chromedriver.exe'))
    
    if operating_system.lower() == 'linux': 
        driver = webdriver.Chrome(options=options, service=Service(executable_path='chromedriver'))
    
    stealth(driver,
        languages=['en-US', 'en'],
        vendor='Google Inc.',
        platform='Win32',
        webgl_vendor='Intel Inc.',
        renderer='Intel Iris OpenGL Engine',
        fix_hairline=True,
    )
    
    page_num: int = 0
    organic_results_data: list = []
    
    if pagination:
        while True:
            # parse all pages
            driver.get(f'https://scholar.google.com/scholar?q={query}&hl=en&gl=us&start={page_num}&as_ylo={year_start}&as_yhi={year_end}')
            parser = LexborHTMLParser(driver.page_source)
            parse(parser=parser, organic_results_data=organic_results_data)
            
            # pagination
            if parser.css_first('.gs_ico_nav_next'):  # checks for the "Next" page button
                page_num += 10                         # paginate to the next page
                time.sleep(random.randint(1, 7))      # sleep between paginations
            else:
                break
    else:
        # parse single, first page
        driver.get(f'https://scholar.google.com/scholar?q={query}&hl=en&gl=us&start={page_num}')
        parser = LexborHTMLParser(driver.page_source)
    
        parse(parser=parser, organic_results_data=organic_results_data)
        
    if save_to_csv:
        pd.DataFrame(data=organic_results_data).to_csv('google_scholar_organic_results_data.csv', 
                                                        index=False, encoding='utf-8')
    if save_to_json:
        pd.DataFrame(data=organic_results_data).to_json('google_scholar_organic_results_data.json', 
                                                        index=False, orient='records')
    driver.quit()
    return organic_results_data


def AddTargetCol(neuromab_website_df,GS):
    '''
    Description:
    Creates a list of the Target Item from the Neuromab dataframe website to append to final df
    
    Args: 
    neuromab_website_df - neuromab df from web-site 
    final_df - dataframe that is having column added 
    
    Returns: 
    The new dataframe with the added column 
    
    '''     
    merged_df = GS.merge(
        
        neuromab_website_df[['Clone', 'Target']], left_on=['Antibody'],right_on=['Clone'], how='left'
    
    )
    merged_df = merged_df.drop('Clone', axis=1)
   
    return merged_df

def CreateURL(query_name, TCSupe, PureID, NeuromabinQuery,MabIDinQuery,TCSupeInQuery,PureInQuery, first_year, last_year):
    '''
    Description:
    Creates a URL to search Google Scholar for the results number at the top of the page 
    
    Args: 
    query_name = name of the antibody 
    TCSupe = the TC ID of AB
    PureID = Pure ID of AB
    NeuromabinQuery = Boolean value of whether or to put 'Neuromab' in the search 
    MabIDinQuery = Boolean value of whether or to put the Mab ID in the search
    TCSupeInQuery = Boolean value of whether or to put the TCSupe ID in the search
    PureInQuery = Boolean value of whether or to put the Pure ID in the search
    
    Returns: 
    a constructed URL to search 
    
    '''
    if NeuromabinQuery:
        First_name = 'Neuromab'
    else: 
        First_name = 'Antibodies+Inc'
        
    if MabIDinQuery:
        MABpt1, MABpt2 = query_name.split('/') 
        url = (
            f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&as_ylo=\"{first_year}\"&as_yhi=\"{last_year}\"&q=\"{First_name}\"\"{MABpt1}%2F{MABpt2}\"&btnG="
        )


    if TCSupeInQuery:
        url = (
            f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=\"{First_name}\"\"{TCSupe}\"&hl=en&as_sdt=0%2C5&as_ylo={first_year}&as_yhi={last_year}"
            )
    if PureInQuery:
        url = (
            f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=\"{First_name}\"\"{PureID}\"&hl=en&as_sdt=0%2C5&as_ylo={first_year}&as_yhi={first_year}"
            )


            
    return url

def CreateDF(query_name, result_value, data, GS_directory, Iteration_num, runresultsdf, developer_mode):
    '''
    Description:
    Creates a dataframe of the search results from Google scholar, prints different alert depending 
    on how many papers are different from search result number and results found from scraping GS
    
    Args: 
    query_name - The neuromab ID 
    result_value - The number of results found from a search, used to compare to Google Scholar scraper results 
    data - The table created from the Google Scholar search results 
    GS_directory - The location of the table from the Google Scholar search results 
    Iteration_num - The column that is being searched through, creates different results based on iteration number 
    runresultsdf - The summary dataframe
    developer_mode - display updates on df creation
    
    Returns : 
    A dataframe of the search results from a single search term 
    
    '''
    
    data_length = int({len(data)}.pop())

    # Record the difference between search result # and data length 
    count = (int(result_value)) - (int(data_length))
    GS_df = pd.DataFrame(data)

    # Get rid of extraneous strings from title 
    GS_df['title'] = GS_df['title'].str.replace(
        '\[HTML\]\[HTML\]|\[PDF\]\[PDF\]|\[CITATION\]|\[C\]|\[BOOK\]\[BOOK\]|\[B\]|\[BOOK\]\[B\]', ''
    )

    # Input Antibody name into table 
    GS_df["Antibody"] = query_name 
    GS_df = AddTargetCol(neuromab_website_df,GS_df)
    GS_df = GS_df.rename(columns={'title': 'Title', 'cited_by_count': 'Cited by','pdf_file' : 'PDF Link', 'publication_info': 'Publication Info'})
    columns_to_drop = [1,3,4]  # Column numbers to drop
    GS_df.drop(GS_df.columns[columns_to_drop], axis=1, inplace=True)
    runresultsdf.loc[runresultsdf['Clone'] == query_name, 'Iteration '+str(Iteration_num)] = f'{data_length} citations'

    if developer_mode:
        print(f'Length of created dataframe is {data_length}')

    return GS_df

def NeuroMab_Only_Search():
    '''
    Description:
    Perform the NeuroMab only search.
    
    Returns:
    None - passes df to merge function
    '''
    query = ('"Neuromab"')
    url = CreateURLneuromabOnly()
    filename = f'Neuromab_only_{first_year}_{last_year}.csv'

    print(f"Starting search for NeuroMab only from {(SetYearParameters())[0]} to {(SetYearParameters())[1]}")
    # Grab data from google scholar 
    data = scrape_google_scholar_organic_results(query=query,
                                                 pagination=True,
                                                 operating_system="Windows",
                                                 year_start=(SetYearParameters())[0],
                                                 year_end=(SetYearParameters())[1]
                                            )

    # create a dataframe of the search result 
    neuromab_only_df = pd.DataFrame(data)

    print(f'URL is {url}')
    url_info = requests.get(url)
    time.sleep(RandomWait())
    html = url_info.text

    # Create a BeautifulSoup object from the HTML string
    soup = BeautifulSoup(html, 'html.parser')
    result_elem = soup.select_one('#gs_ab_md .gs_ab_mdw')

    # Create text from Google Scholar Page and find search results number. 
    if result_elem:
        result_text = result_elem.get_text(strip=True)
        result_match = re.search(r'(\d+[\d,]*)\s+results', result_text)

        if result_match == None:
            result_match = re.search(r'(\d+[\d,]*)\s+result', result_text)

        if result_match:
            result_value = result_match.group(1)
            result_value = result_value.replace(',', '')
            print(f'Results search value is {result_value}')

    data_length = int({len(data)}.pop())
    print(f'Length of created dataframe is {data_length}')

    # Record the difference between search result # and data length 
    count = (int(result_value)) - (int(data_length))
    print(f'The difference between number of items in dataframe and google search is {count}')

    # Get rid of extraneous strings from title 
    neuromab_only_df['title'] =  neuromab_only_df['title'].str.replace(
        '\[HTML\]\[HTML\]|\[PDF\]\[PDF\]|\[CITATION\]|\[C\]|\[BOOK\]\[BOOK\]|\[B\]|\[BOOK\]\[B\]', ''
    )

    # Save df 
    neuromab_only_df.to_csv(os.path.join(GS_directory, filename), index=False)
    print(f'{filename} saved to {GS_directory}')

    # merge the neuromab only search dataframes 
    merge_neuromab_only_dfs(GS_directory)

def merge_neuromab_only_dfs(GS_directory):
    '''
    Descripition:
    Merges the Neuromab search only dfs. Since the Neuromab only searches create more search results than allowed, 
    these dataframes from seperate year ranges will need to be merged together
    
    Returns:
    merged (DataFrame): Merged dataframe of all Neuromab only search results.
    
    '''
    # create a list of dataframes
    dfs = []
    for filename in glob.glob(f'{GS_directory}/Neuromab_only_*.csv'):
        df = pd.read_csv(filename)
        dfs.append(df)

    # concatenate the dataframes vertically and rename columns
    merged = pd.concat(dfs, ignore_index=True)[['title', 'cited_by_count']] \
             .rename(columns={'title': 'Title', 'cited_by_count': 'Cited by'})

    merged.to_csv(f'{GS_directory}/Merged_Neuromab_Only_Search.csv')

def Scholar_Query(leftoff, developer_mode):
    '''
    Description:
    Main Scraping function 
     
    Args:
    leftoff (int): The row number of the summary dataframe from where you would like to start your search.
    developer_mode (bool): Flag to enable developer mode for additional print statements.

    Returns : 
    neuromab_search_dataframes (list): List of dataframes for each successful GS search, containing information on 
    the paper that mentions a neuromab.
        - also updates the summary dataframe which shows results from searches 
        i.e. how many papers were found for each antibody, and where the search 
        left off 
        
    '''
    # Input varables for paramters 
    (GS_directory, path_to_file, SUM_df, first_year, last_year) = set_up_parameters()
    # Create an empty list to store the DataFrames
    neuromab_search_dataframes = []    
    # Initialize a value to count 0 result pages 
    zero_result_counter = 0
    # Read in summary df 
    runresultsdf = pd.read_excel(SUM_df)
    # Make the error flag initially false
    error_occurred = False  # Flag to track if an error occurred
    
    print(f'Years: {first_year} to {last_year}')

    for index, row in runresultsdf.iloc[leftoff:].iterrows():
        Iteration_num = 1
        while Iteration_num <= 6:
            try:
                data = {}
                query_name = row['Clone']
                TCSupe = row['AICatalogTCSupe']
                PureID = row['AICatalogPure']
                print(f"\nStarting Google Scholar scrape for {query_name}, Iteration {str(Iteration_num)}, Row {str(row[0])}...")
                # Set query for google scholar 
                # Example: “Neuromab " "N289/16"
                # and create URL to grab search results number
                # and set filename for query df 

                # Create a dictionary to map Iteration_num to query_name, TCSupe, PureID
                search_dict = {
                    1: (f'Neuromab_{query_name}.csv', 'Neuromab', query_name, TCSupe, PureID, True, True, False, False),
                    2: (f'Neuromab_{TCSupe}.csv', 'Neuromab', TCSupe, query_name, PureID, True, False, True, False),
                    3: (f'Neuromab_{PureID}.csv', 'Neuromab', PureID, query_name, TCSupe, True, False, False, True),
                    4: (f'AntibodiesInc_{query_name}.csv', 'Antibodies Inc', query_name, TCSupe, PureID, False, True, False, False),
                    5: (f'AntibodiesInc_{TCSupe}.csv', 'Antibodies Inc', TCSupe, query_name, PureID, False, False, True, False),
                    6: (f'AntibodiesInc_{PureID}.csv', 'Antibodies Inc', PureID, query_name, TCSupe, False, False, False, True)
                }

                # Get the values based on Iteration_num
                filename, query_prefix, query_value, url_arg1, url_arg2, NeuromabinQuery, MabIDinQuery, TCSupeInQuery, PureInQuery = search_dict[Iteration_num]
                # Construct the query string
                query = f'"{query_prefix}""{query_value}"'
                # Create the URL
                url = CreateURL(query_name, TCSupe, PureID, NeuromabinQuery, MabIDinQuery, TCSupeInQuery, PureInQuery, first_year, last_year)
                print(f"Query is {query}")
                url_info = requests.get(url)
                time.sleep(RandomWait())
                html = url_info.text
                # Create a BeautifulSoup object from the HTML string
                soup = BeautifulSoup(html, 'html.parser')
                result_elem = soup.select_one('#gs_ab_md .gs_ab_mdw')
                # Create text from Google Scholar Page and find search results number. 
                if result_elem:
                    result_text = result_elem.get_text(strip=True)
                    result_match = re.search(r'(\d+[\d,]*)\s+results?', result_text)
                    if result_match:
                        result_value = result_match.group(1).replace(',', '')
                        if developer_mode:
                            print(f'URL is {url}')
                            print(f'Results search value is {result_value}')
                            
                        # Grab data from google scholar 
                        data = scrape_google_scholar_organic_results(
                            query=query,
                            pagination=True,
                            operating_system="Windows",
                            year_start=first_year,
                            year_end=last_year
                                                                    )

                        final_df = CreateDF(
                            query_name,
                            result_value,
                            data, 
                            GS_directory,
                            Iteration_num,
                            runresultsdf,
                            developer_mode
                                           )
                        # Append the DataFrame to the list
                        neuromab_search_dataframes.append(final_df)
                        
                    else:
                        if developer_mode is True:
                            print(f'{query} No research Published')
                            
                else:
                    error_occurred = True
                    break     

            except Exception as e:
                print(e)
                print(str(e))
                print(type(e))
                if 'title' in str(e):
                    print(f"Error occurred while processing row {index}: {e}")
                    error_occurred = True
                    break
        
            Iteration_num += 1
        
        if error_occurred:
            print(f"Restart with new VPN using command : Scholar_Query({str(row[0])}, True)")
            break
                
    if len(neuromab_search_dataframes) > 0:
        # Concatenate the DataFrames into a final DataFrame
        final_df = pd.concat(neuromab_search_dataframes)
        # Reset the index of the final DataFrame
        final_df = final_df.reset_index(drop=True) 

        # Check if the file already exists
        if os.path.isfile(path_to_file):
            # Read the existing file as a DataFrame
            existing_df = pd.read_csv(path_to_file)
            # Concatenate the existing DataFrame with the new DataFrame
            merged_df = pd.concat([existing_df, final_df])
            merged_df = merged_df.applymap(lambda x: ' '.join(x.split()) if isinstance(x, str) else x)
            merged_df.to_csv(path_to_file, index=False)
            print(f"The DataFrame has been merged with {path_to_file}")
        else:
            # Save the merged DataFrame to the CSV file
            final_df = final_df.applymap(lambda x: ' '.join(x.split()) if isinstance(x, str) else x)
            final_df.to_csv(path_to_file, index=False)
            print(f"The DataFrame has been saved as {path_to_file}")


