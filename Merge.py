def merge_created_dataframes_from_GS():
    '''
    Description :
    Merges the created dataframes from the searches into a single dataframe.
    
    Returns:
    merged_df (DataFrame): The merged dataframe.
    
    Constraints :
    make sure that any merged dataframes with the exception of the Neuromab only 
    search dataframes that were merged prior are the only files in the directory. Otherwise 
    some of the functions in this code will not work 
    '''

    # Collection of all of the created dataframes in results directory into a list 
    df_list = []

    for file in os.listdir(GS_directory):
        if 'test_run' in file:
            df = pd.read_csv(f"{GS_directory}/{file}", encoding='utf-8')
            df_list.append(df)

    publications_neuromab_df = pd.concat(df_list)

    # Group by 'title' column and aggregate 'antibody' column 
    def concatenate_antibodies(antibodies):
        """
        Concatenates antibodies in a comma-separated string.

        Args:
        antibodies (list): The list of antibodies.

        Returns:
        concatenated_antibodies (str): The concatenated string of antibodies.
        
        """
        # Convert non-string values to empty strings
        antibodies = [str(ab) for ab in antibodies if isinstance(ab, (str, int))]
        return ', '.join(set(antibodies))  # Join unique antibodies with commas

    def concatenate_targets(targets):
        """
        Concatenates targets in a comma-separated string.

        Args:
        targets (list): The list of targets.

        Returns:
        concatenated_targets (str): The concatenated string of targets.
        
        """
        # Convert non-string values to empty strings
        targets = [str(t) for t in targets if isinstance(t, (str, int))]
        return ', '.join(set(targets))  # Join unique targets with commas

    # group the antbodies and targets togther in the same column of the same paper row 
    publications_neuromab_df['Antibody'] = publications_neuromab_df.groupby('Title')['Antibody'].transform(concatenate_antibodies)
    publications_neuromab_df['Target'] = publications_neuromab_df.groupby('Title')['Target'].transform(concatenate_targets)

    # Remove white spaces in the DataFrame, except for spaces between words
    publications_neuromab_df = publications_neuromab_df.replace(r'\s+', ' ', regex=True).applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Drop duplicate rows based on 'title' column
    publications_neuromab_df.drop_duplicates(subset='Title', keep='first', inplace=True)

    # Reset the index
    publications_neuromab_df.reset_index(drop=True, inplace=True)
    
    # strip the whitespace 
    publications_neuromab_df.replace(r'\s+', ' ', regex=True, inplace=True)


    # Rename columns Antibody and Target 
    publications_neuromab_df = publications_neuromab_df.rename(columns={'Antibody':'Neuromab(s)','Target':'Target(s)'})

    # Iterate over 'Target(s)' column and reverse the order of items
    for index, row in publications_neuromab_df.iterrows():
        targets = row['Target(s)'].split(', ')  # Split items by comma and space
        reversed_targets = ', '.join(reversed(targets))  # Reverse the order of items
        publications_neuromab_df.at[index, 'Target(s)'] = reversed_targets  # Update 'Target(s)' column

    # Drop columns that start with 'Unnamed'
    publications_neuromab_df = publications_neuromab_df.loc[:, ~publications_neuromab_df.columns.str.startswith('Unnamed')]
    
    for column in df.columns:
        df[column] = df[column].apply(lambda x: unidecode(str(x)))
    
    # Save dataframe to csv 
    publications_neuromab_df.to_csv(f'{GS_directory}/filename_of_merged_df.csv',  encoding='utf-8' )


