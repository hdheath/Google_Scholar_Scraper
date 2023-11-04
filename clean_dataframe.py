def generate_path_to_df_to_clean():
    '''
    Description:
    Generates the file path for a DataFrame to be cleaned.

    Inputs: None

    Returns:
    - path: The file path where the cleaned DataFrame will be saved.

    '''
    return f"{GS_directory}/merged_df_w_pubmed_&_verified.csv"

def clean_for_neuromab_site(df):
    '''
    Description:
    Cleans a DataFrame by performing various cleaning operations.

    Inputs:
    - df: The DataFrame to be cleaned.

    Returns: 
    None - saves df to csv
    '''
    df = pd.read_csv(df, encoding='utf-8')
    print(f"Length of Df before cleaning: {len(df)}")

    null_rows = df[df['PMID'].isnull()]
    df = df.drop_duplicates(subset='PMID').dropna(subset=['PMID'])
    df = pd.concat([df, null_rows])
    print(f"Length after dropping duplicated PMIDs: {len(df)}")

    for index, row in df.iterrows():
        if pd.isnull(row['Publication']) or (row['Publication'] == 0):
            publication_info = row['Publication Info']
            if pd.notnull(publication_info):
                if ',' in publication_info:
                    split_info = publication_info.split(',')
                    last_name = split_info[0].strip()
                else:
                    split_info = publication_info.split(' ')
                    last_name = split_info[0] + split_info[1]
                    
                df.at[index, 'Publication'] = last_name + ' et al.' + split_info[-1]

    df = df.apply(lambda x: x.astype(str).str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8'))

    def extract_year_from_publication(publication):
        match = re.search(r'\b(19|20)\d{2}\b', publication)
        return int(match.group()) if match else None

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df.apply(lambda row: extract_year_from_publication(row['Publication']) if pd.isnull(row['Date']) else row['Date'].year, axis=1)
    df['Publication'] = df['Publication'].replace(r'\b(19|20)\d{2}\b', '', regex=True).str.strip()
    df.dropna(subset=['Year'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    df['Publication'] = df['Publication'].str.replace('-  -', ' - ').str.replace(',  -', ' - ')

    thresholds = {2006: 50, 2007: 100, 2008: 150, 2009: 200, 2010: 250, 2011: 300}

    def apply_threshold(row):
        year = row['Year']
        neuromab = row['Neuromab(s)']
        if year <= 2011 and 'N' in neuromab:
            n_value = int(re.search(r'N(\d+)/\d+', neuromab).group(1))
            threshold = thresholds.get(year, 0)
            if n_value > threshold:
                return re.sub(r'N\d+/\d+', '', neuromab)
        return neuromab

    df['Neuromab(s)'] = df.apply(lambda row: apply_threshold(row), axis=1)

    df['PMID'] = pd.to_numeric(df['PMID'], errors='coerce').fillna(0).astype(int)
    df['Neuromab(s)'] = df['Neuromab(s)'].replace('nan', np.nan)
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    df['title_lowercase'] = df['Title'].str.lower()
    df.drop_duplicates(subset='title_lowercase', keep='first', inplace=True)
    print(f'Length after dropping for duplicated titles: {len(df)}')
    # Delete rows where 'NeuroMab Verification' column is not 'OK'
    df = df[df['NeuroMab Verification'] == 'OK']
    # Reset the index
    df = df.reset_index(drop=True)
    df.reset_index(drop=True, inplace=True)
    print(f"Length after removing unverified rows: {len(df)}")

    new_columns = ["Title", "Publication Info", "Cited by", "PDF Link", "Clone", "Target","Title from PMC", "PubMed", "Date",
                   "Title Similarity", "Citation", "Method of Verification", "NeuroMab Verification",
                   "Antibody Verification", "URL", "Year", "Lowercase Title"]
    df.columns = new_columns

    columns_to_keep = ['Year', 'Clone', 'Target', 'Citation', 'PubMed']
    df = df[columns_to_keep]
    df.to_csv(f'{GS_directory}/Neuromab_final_cleaned_df.csv', encoding='utf-8')
