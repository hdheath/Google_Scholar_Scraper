# Data Visualization and Analysis of Product 

# Average number of Antibodies per publication 

# Sample dataframe
neuromab_df = pd.read_csv(generate_path_to_merged_df())

def count_items(row):
    neuromabs = row['Neuromab(s)']
    if isinstance(neuromabs, str):
        return len(neuromabs.split(','))
    else:
        return 0


# Apply the function to each row and store the counts in a new column
neuromab_df['Number of AB\'s'] = neuromab_df.apply(count_items, axis=1)

# Display the updated dataframe
#print(neuromab_df)

# Calculate the average of the values in the 'Number of AB\'s' column
average = neuromab_df['Number of AB\'s'].mean()

# Display the average
print("Average number of AB's used in each publication: ", average)

# Number of Publications without PubMed ID 
import pandas as pd

# Count the number of empty values in the 'Publication' column
count = 0
count_2 = 0 

for pub in neuromab_df['Publication']:
    if pd.isna(pub) or pub == '':
        count += 1
        
for pub in neuromab_df['Neuromab(s)']:
    if pd.isna(pub) or pub == '':
        count_2 += 1

# Get the total number of rows in the DataFrame
rows = len(neuromab_df)

# Print the count of publications without a PubMed ID and the total number of rows
print(f'The total number of publication results is {rows}')
print(f'The number of publications with a PubMed ID is {rows - count} - ({count} without PMID)')
print(f'The number of publications without referencing a specific NeuroMab is {count_2}')

# Set a threshold for percentage display
threshold = 1.5 # Only display percentages above 1.5%

# Create a pie chart of the different numbers of antibodies used
# Count the occurrences of each unique value in 'Number of AB\'s' column
count_by_number = neuromab_df['Number of AB\'s'].value_counts()

# Calculate percentage for each count
percentages = count_by_number / count_by_number.sum() * 100

# Filter percentages based on threshold
filtered_percentages = percentages[percentages > threshold]

# Create pie chart
plt.figure(figsize=(8, 6))
plt.pie(filtered_percentages, labels=filtered_percentages.index, autopct='%1.1f%%', startangle=90)
plt.title('Number of AB\'s Used per Publication')
plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# Extract the 'Neuromab(s)' column as a Series
neuromabs = neuromab_df['Neuromab(s)']

# Create a dictionary to store the counts of each item
item_counts = {}

# Iterate through the 'Neuromab(s)' column in the DataFrame
for row in neuromabs:
    # Check if the value is a float
    if isinstance(row, float):
        continue
        
    # Convert the value to a string and split the items by commas
    items = str(row).split(',')
    
    # Iterate through the items and update the counts
    for item in items:
        # Remove whitespace from each item
        item = item.strip()
        if item in item_counts:
            item_counts[item] += 1
        else:
            item_counts[item] = 1

# Sort the items by count in descending order
sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
items = [item[0] for item in sorted_items]
counts = [item[1] for item in sorted_items]

# Filter items with count above 50
items_filtered = [item for item, count in zip(items, counts) if count > 50]
counts_filtered = [count for count in counts if count > 50]

# Create a figure with a larger size and higher resolution
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)


# Create a bar plot for filtered items
plt.bar(items_filtered, counts_filtered)
plt.xlabel('NeuroMab')
plt.ylabel('# of Publications')
plt.title('Most Published NeuroMabs')
# Rotate the x-axis labels by 45 degrees
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# Parse the dates in the 'Date' column as datetime objects
neuromab_df['Date'] = pd.to_datetime(neuromab_df['Date'], format='%m/%d/%y')

# Create a new column 'Month' that contains only the month and year information
neuromab_df['Month'] = neuromab_df['Date'].dt.strftime('%Y-%m')

# Group the DataFrame by 'Neuromab(s)' and count the number of rows for each group
neuromab_counts = neuromab_df.groupby(['Neuromab(s)', 'Month']).size().reset_index(name='Publication Count')

# Filter the counts to keep only the unique Neuromab(s) published more than 50 times
neuromab_counts_filtered = neuromab_counts[neuromab_counts['Neuromab(s)'].isin(items_filtered)]

# Group the filtered counts by 'Neuromab(s)' and calculate the average publication count per month for each Neuromab(s)
neuromab_monthly_average = neuromab_counts_filtered.groupby('Neuromab(s)')['Publication Count'].mean()

# Sort the neuromab_monthly_average Series in descending order of values
neuromab_monthly_average = neuromab_monthly_average.sort_values(ascending=False)

# Set the style of the plot
plt.style.use('seaborn-whitegrid')

# Create a figure with a larger size and higher resolution
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# Create a bar plot for the average publication count per month for each Neuromab(s)
ax.bar(neuromab_monthly_average.index, neuromab_monthly_average.values)

# Set the x-axis and y-axis labels and title of the plot
ax.set_xlabel('NeuroMab')
ax.set_ylabel('Avg. # of Publications per Month')
ax.set_title('Average Number of Publications Since First Appearance')

# Rotate the x-axis labels by 45 degrees
plt.xticks(rotation=45, ha='right')

# Tighten the layout of the plot
fig.tight_layout()

# Display the plot
plt.show()

# Citations by year / Impact over time 

import pandas as pd
import matplotlib.pyplot as plt

# Extract the year from the Date column
neuromab_df['Year'] = pd.DatetimeIndex(neuromab_df['Date']).year

# Group the DataFrame by year and sum the Cited by column
citation_counts = neuromab_df.groupby('Year')['Cite Count'].sum()



# Create a bar graph of the citation counts by year
plt.bar(citation_counts.index, citation_counts.values)
plt.xlabel('Year')
plt.ylabel('Number of Citations')
plt.title('Citation Counts by Year')
plt.show()

# July 1st 2022 - March 31st 2023 

import pandas as pd
import matplotlib.pyplot as plt

# Extract the year from the Date column
neuromab_df['Year'] = pd.DatetimeIndex(neuromab_df['Date']).year

# Group the DataFrame by year and count the Publication column
pub_counts = neuromab_df.groupby('Year')['Publication'].count()

# Set the style of the plot
plt.style.use('seaborn-whitegrid')

# Create a figure with a larger size and higher resolution
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# Create a bar graph of the publication counts by year
plt.bar(pub_counts.index, pub_counts.values)
plt.xlabel('Year')
plt.ylabel('Number of Publications')
plt.title('NeuroMab Publications Per Year')

# Set x-ticks to only include whole years
plt.xticks(range(int(pub_counts.index.min()), int(pub_counts.index.max())+1))

plt.show()

import pandas as pd
import matplotlib.pyplot as plt


# Convert the Date column to datetime format
neuromab_df['Date'] = pd.to_datetime(neuromab_df['Date'])

# Set the start and end dates
start_date = pd.to_datetime('2022-07-01')
end_date = pd.to_datetime('2023-03-31')

# Filter the DataFrame by date range
filtered_df = neuromab_df[(neuromab_df['Date'] >= start_date) & (neuromab_df['Date'] <= end_date)]

# Group the filtered DataFrame by month and count the number of papers
paper_counts = filtered_df.groupby(pd.Grouper(key='Date', freq='M')).size()

# Create a bar chart of the paper counts by month
ax = paper_counts.plot(kind='bar', color='blue', figsize=(10,6))

# Set the title and axis labels
ax.set_title('7/1/22 - 3/31/23 Publications', fontsize=18)
ax.set_xlabel('Month', fontsize=14)
ax.set_ylabel('# of Publications', fontsize=14)

# Format the x-axis labels as shortened month names
ax.set_xticklabels(paper_counts.index.strftime('%b'))

# Display the plot
plt.show()

# Calculate the total number of papers
total_papers = paper_counts.sum()
print(f'Number of Publications between 7/1/22 and 3/31/23 : {total_papers}')

from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Convert Title column to string data type and drop NaN values
titles = neuromab_df['Title'].astype(str).dropna()

# Join all titles into a single string
titles_text = " ".join(title for title in titles)

# Create a WordCloud object with some basic parameters
wordcloud = WordCloud(width=1600, height=800, background_color='white', colormap='inferno', max_words=100)

# Generate the word cloud
wordcloud.generate(titles_text)

# Plot the word cloud
plt.figure(figsize=(20, 10), dpi=300)
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.savefig('wordcloud.png', bbox_inches='tight')
plt.show()
