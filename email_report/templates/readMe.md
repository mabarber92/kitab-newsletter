# HTML coding for email

Templates are written in a variant of bootstrap that can be converted into an email compliant html with some basic styling. **WARNING: Results may vary - html emails sent to outlook tend to lose some of their styling compared to those sent to gmail - it is best to use the minimal styling necessary and test thoroughly.

[bootstrapemail](https://bootstrapemail.com/) is used for converting the bootstrap html into a html that can be read by the email client. Conversions can be done using the inbuilt converter or through command line using the ruby converter. See their documentation.

All templates with a "_rendered" have been rendered using bootstrapemail.

# The email writing pipeline

Their are two types of email template 'general' and 'spec'. General is for those who have not contributed texts to the OpenITI and spec if for those who have. For a spec, the list of URIs with reuse data is specific to the contributor.

The email writing script takes rendered email html as input - looking for the tags - marked between @@ and replacing them with the current data.

If a change is made to a template - the rendered email html should be updated - either through the command line or bootstrapemail's online converter. If the converter is not run, then the changes will not be reflected in the outputted emails.

The process:

1. The Python script takes as input:
    - A csv list of contributors - which specifies if they have contributed URIs to the corpus - and the URIs they have contributed
    - A tsv containing stats for the last release
    - A tsv containing stats for the current release
    - A tsv containing metadata for the last release
    - A tsv containing metadata for the current release
    - base_general_template_rendered.html
    - base_spec_template_rendered.html
2. Calculate the aggregated stats and the change from the last release to the current
3. Fetch the top 4 new URIs for this release and a count of their pairwise files
4. Goes through each contributor in the csv
5. If the user has contributed:
    - Fetch the top 4 URIs and a count of pairwise files
    - Insert the data into the email by replacing the relevant fields with data (fields detailed below)
    - Write out an html file with the contributor's ID
6. Write a general email using the general template to use with everyone else

# Field tags in template emails

@INST-ST@ - Total number of reuse instances
@INST-CH@ - Change in instances from last release
@WM-ST@ - Total number of words matched 
@WM-CH@ - Change in total word match from last release
@BC-ST@ - Total number of books in release
@BC-CH@ - Change in book count from last release
@PW-ST@ - Number of pairwise files
@PW-CH@ - Change in pairwise files from last release

## Ids to replace - either with recipient specific data or top 4 new reusers

The pattern here is the same for each URI - where the id number is either 1, 2, 3, or 4.

@URLID1@ - Url to metadata page with query string for the URI
@0000AUTHOR.BOOK.ID1@ - The full URI of the text
@id1data@ - The total number of pairwise files for the URI


