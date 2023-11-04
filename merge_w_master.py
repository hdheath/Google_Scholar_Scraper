def generate_path_to_master_df():
    path = '/Users/HMans_MacBook_Pro/Desktop/Test_Code/Neuromab_6_12.csv'
    return path

def generate_path_to_merging_df():
    path = f'{GS_directory}/Neuromab_final_cleaned_df.csv'
    return path 

def merge_with_master(merging_df_path):
    '''
    This function takes the newly created dataframes and merges them with the master dataframe 
    '''
    master_df = pd.read_csv(generate_path_to_master_df(), encoding='utf-8')
    merging_df = pd.read_csv(merging_df_path, encoding='utf-8')
    
    print(f"Length before Merge: {len(master_df)}")
    
    # Concatenate the two DataFrames
    df = pd.concat([master_df, merging_df])
    # Reset the index of the concatenated DataFrame
    df.reset_index(drop=True, inplace=True)

    # Drop duplicated rows
    df.drop_duplicates(subset=master_df.columns[1:], inplace=True)
    
    df.reset_index(drop=True, inplace=True)
    
    print(f"Length After Merge: {len(df)}")
    for col in df.columns:
        if col.startswith("Unnamed"):
            df = df.drop(col, axis=1)
            
    df.to_csv(f'{GS_directory}/Neuromab_final_cleaned_df_test.csv', encoding ='utf-8')

