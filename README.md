# Google Scholar Scraper

# Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Data Visualization](#data-visualization)
5. [Author](#author)

## Pipeline Overview
![MasterHead](https://imgur.com/GpAZKvD.png)

## Introduction
In the field of science the ability for researchers to keep up with new advances is very important. Search engines such as Google Scholar and PubMed are currently used to elucidate new and pertinent information to researchers. These tools enable efficient literature review by swiftly identifying and accessing relevant papers, saving researchers valuable time and effort. Moreover, they facilitate the identification of trends and patterns across studies, aiding in the exploration of emerging research areas and knowledge gaps. By gathering evidence from a wide range of studies, researchers can generate and validate hypotheses effectively, while also staying up to date with the latest advancements in their respective fields. Overall, these scraping tools empower researchers, enabling them to navigate the vast scientific landscape, contribute to existing knowledge, and drive progress and innovation forward.

Google Scholar Scraper is a software that will create a database of research literature that includes any given search terms in it. This makes it a useful resource by providing researchers a way to efficiently review literature, explore data, and monitor research progress for any topic they so desire. Google Scholar Scraper (GSS) pulls information on research from the 100 million plus articles on Google Scholar[1], and then uses a unique verification process to ensure that the articles are relevant to, and include, the requested search term. 

Google Scholar Scraper is an open-source software that provides an efficient and more accurate way to access relevant scientific articles than what is currently available. Its goal is to be used as a tool for researchers to review research so that they may further innovation in a more productive manner. Shown here is an exmaple of GSS used for mono-clonal antibody literature review.

## Data Flow from Example use-case 

Shows the total number of papers analyzed and verified by the GSS
![MasterHead](https://imgur.com/MzAexgw.png)

## Installation
Before running the scraper, ensure you have the following dependencies installed:
- Python 3.x
- selenium
- pandas
- Other dependencies listed in requirements.txt
```
pip install -r Import.py
```
Also upload search terms to excel file in relative path - runresults.xlsx

## Usage
Setting Up Parameters
First, set up your parameters by editing the set_up_parameters() function in the configuration file:

```
# Example configuration
GS_results_directory = "/path/to/results"
path_to_file = f"{GS_results_directory}/output.csv"
summary_file_path = "/path/to/summary.xlsx"
first_year = 2006
last_year = 2023
Entrez.email = 'your_email@example.com'  # Replace with your email

```

Scraping Google Scholar
Run the scraper using the Scholar_Query command:

```
# Example command
Scholar_Query(447, True)

```

Merging Data
After scraping, merge the data using:

```
# Example command
merge_created_dataframes_from_GS()

```

Adding PubMed Information
To augment the dataset with PubMed information:

```
# Example command
add_Pubmed_info_to_dataframe(0, 100, pd.read_csv(generate_path_to_merged_df()), False)

```

Verification Process
Verify the results with:

```
# Example command
verify_GS_results(path_to_merged_df_w_pubmed(), SUM_df, 0, False)

```

Cleaning Data
Clean the dataframe for further processing:

```
# Example command
clean_for_neuromab_site(generate_path_to_df_to_clean())

```

Merging with Master Dataframe
Finally, merge the cleaned data with the master dataframe using:
```
# Example command
merge_master.py

```
## Data Visualization 

![Most Published Antibodies](https://imgur.com/V0lCWxy.png?1)

![AVG PER Month](https://imgur.com/tqZyT2f.png?1)

![AVG PER year](https://imgur.com/AJgdHld.png?1)

Word cloud of words derived from over 4000 published papers 
![Word Cloud](https://imgur.com/wD9sSGJ.png?1)

## Author
Harrison Heath 
