def generate_path_to_merged_df():
    '''
    Description:
    Generates the path to the merged DataFrame file.
    
    Returns:
    path_to_merged_df (str): The path to the merged DataFrame file.

    '''
    path_to_merged_df = f'{GS_directory}/filename_of_merged_df2.csv'
    return path_to_merged_df

def extract_last_name(input_string):
    '''
    Description: 
    Extracts the last name from an input string.
    
    Args:
    input_string (str): The input string containing a name.

    Returns:
    last_name (str): The extracted last name from the input string.
    If no last name is found, returns None.

    '''
    # Define the pattern to match the last name
    pattern = r'[A-Z][a-zA-Z\s]*(?=(?:,|-))'

    # Search for the pattern in the input string
    match = re.search(pattern, input_string)

    if match:
        # Extract the last name from the matched substring
        last_name = match.group(0).strip().split()[-1]
        return last_name

    # If the last name is not found, return None or raise an exception
    return None

def add_Pubmed_info_to_dataframe(leftoff, autosave, df, developer_mode):
    '''
    Description:
    This function uses the PubMed tool to generate the pubmed ID from the value in the Title 
    column of each row of the desired dataframe.

    Args:
    leftoff (int): The row index from which to start adding information.
    autosave (int): The number of iterations before being saved as a CSV.
    df (DataFrame): The desired DataFrame to add the information to.
    developer_mode (bool): Flag indicating whether to run the function in developer mode.

    Returns:
    df (DataFrame): The modified DataFrame with the PMID, Author, Publication Date, and Journal columns appended.

    '''
    for column in df.columns:
        df[column] = df[column].apply(lambda x: unidecode(str(x)))

    # initialize the tool being used 
    pubmed = PubMed(tool="PubMedSearcher", email="mao@ucdavis.edu")
    
    # Initialize columns values to be added to NaN
    if 'Title from PMC' not in df:
        df['Title from PMC'] = np.nan
    if 'PMID' not in df:
        df['PMID'] = np.nan

    # iterate over the df from the designated row 
    for index, row in df[leftoff:].iterrows():
        try:
            
            if pd.isna(row['Title']):    # if the value in Title is empty skip over it 
                continue
            
            df_title = row['Title']
            df_title = df_title.replace("'", "")
            df_title = df_title.replace("'", "")
            df_title = df_title.replace("a-", "α-")
            df_title = df_title.replace("-a", "-α")
            df_title = df_title.replace("b-", "β-")
            df_title = df_title.replace("-b", "-β")
            last_name = extract_last_name(row['Publication Info'])
            word_list = df_title.split()
            filtered_words = [word for word in word_list if word not in stopwords.words('english')]
            search_term = (" ".join(filtered_words))
            max_results = 500
            results = pubmed.query(search_term, max_results=max_results)
            matching_pubmed = None  # Initialize to None

            # iterate through each of the paper titles in results, if the title is 80% similar to one of the 
            # articles - then that is the paper that we will grab information from 
            for article in results:
                title = article.title
                pubmedId = article.pubmed_id.partition('\n')[0]
                authors = article.authors
                # Extracting the first author's lastname
                first_author_lastname = authors[0]['lastname']
                # Compare the similarity of the title and the search term
                similarity = fuzz.token_set_ratio(title.lower(), df_title.lower())
                matching_authors = [author for author in authors if unidecode(author['lastname']) == last_name]
                if (similarity >= 60 and matching_authors) or (similarity >= 95):
                    matching_pubmed = pubmedId
                    break

            if matching_pubmed is not None:  # Only assign pubmed_id if a significant title is found
                if developer_mode is True:
                    print(f"\nSimilarity:{similarity}\nTitle in dataframe: {row['Title']}\nTitle from search: {title}\nPubmed ID: {matching_pubmed}")
                    print(f"Author from df : {last_name}\nAuthor from PubMed : {first_author_lastname}\n") 
                df.at[index, 'Title from PMC'] = article.title
                df.at[index, 'PMID'] = matching_pubmed   # assign the PMID to the row 
                df.at[index, 'Date'] = article.publication_date # assign the publication date to the row 
                df.at[index, 'Title Similarity'] = similarity
                # Extracting the first author's lastname
                first_author_lastname = authors[0]['lastname']
                # Creating the formatted string for publication info
                publication_info = f"{first_author_lastname} et al. {article.journal}"
                df.at[index, 'Publication'] = unidecode(publication_info)
                
            # save the dataframe whenever there are 100 iterations - there is a possibility of being dropped
            if index % autosave == 0:
                for col in df.columns:
                    if col.startswith("Unnamed"):
                        df = df.drop(col, axis=1)
                df.to_csv(generate_path_to_merged_df())

        except Exception as e:
            print(f"Error occurred while processing row {index}: {e}")
            continue
            
        # remove the 'unnamed' column from the df 
    for col in df.columns:
        if col.startswith("Unnamed"):
            df = df.drop(col, axis=1)

    # Drop duplicate rows based on the "title" column
    df = df.drop_duplicates(subset=['Title'], keep='first')

    df.to_csv(f'{GS_directory}/merged_df_w_pubmed.csv', encoding='utf-8')
