def set_up_parameters():
    '''
    Description:
    Returns desired directory and paths for created dfs and used dfs. Also sets up the year parameters that are used 
    
    Args:
    Path to file = the path to where you would like to save the created file to from the Scholar Results
    
    Returns:
    the location of where to put the summary table that shows how the google search went 
    by reporting number of articles found for each search term 
    This df should include the conversion catalog numbers from NeuroMab to Antibodies, and the seperate 
    results from each iteration,
    
    '''
    GS_results_directory = "/Users/HMans_MacBook_Pro/Desktop/Test_Code/ONE_COMMAND"
    path_to_file = f"{GS_results_directory}/test_run.csv"
    summary_file_path = "/Users/HMans_MacBook_Pro/Desktop/Test_Code/ONE_COMMAND/runresults_test.xlsx"
    first_year = 2006
    last_year = 2023
    Entrez.email = 'hdheath@ucdavis.edu' # Replace with your email
    pubmed = PubMed(tool="PubMedSearcher", email="mao@ucdavis.edu")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'email': 'hdheath@ucdavis.edu'  # Replace with your email
    }
    
    return (GS_results_directory, path_to_file, summary_file_path, first_year, last_year, Entrez.email, pubmed, headers )

# Grab the neuromab website dataframe to be used to add the target columns 
data_Neuromab = requests.get("https://neuromab.ucdavis.edu/catalog-download.cfm").content
neuromab_website_df = pd.read_csv(BytesIO(data_Neuromab))

GS_directory = None
path_to_file = None
SUM_df = None
first_year = None
last_year = None

GS_directory, path_to_file, SUM_df, first_year, last_year, Entrez.email, pubmed, headers = set_up_parameters()
