# CAMSPdfExtractor
Tool/Library that will extract CAMS Mutual fund PDF statement (India) data into either a csv file or dataframe or json string or list of dicts

### How to use
First you need to request CAMS detailed Mutual Fund statement from CamsOnline [How To?](#request-cas-statement-from-cams)
Once you have the PDF downloaded to your machine, you can use the library to extract data from it

```python
>>> 
>>> from camspdf import ProcessPDF
>>> filename = "camsonline.pdf"
>>> password = "Check123"
>>> pp = ProcessPDF(filename, password)
>>> out = pp.get_pdf_data(output_format="df")  # output_format can be either "dicts", "csv", "json", "df"
Processing PDF. Please wait...
>>> print(out)
fund_name          isin         folio_num         date   txn     amount     units       nav balance_units
0    Aditya Birla Sun Life Liquid Fund - Growth-Dir...  INF209K01VA3        1039837274  26-Apr-2020   Buy  360000.00  1122.052  320.8408       1122.052
...           ...               ...          ...   ...        ...       ...       ...            ...
655        UTI Nifty Next 50 Index Fund - Direct Plan   INF789FC12T1  599321413667 / 0  26-Jun-2023   Buy   99995.00  6358.740   15.7256      86737.464
[656 rows x 9 columns]
>>> 
>>> 
>>> # If you want to dump it to csv file, you do like below
>>> 
>>> out = pp.get_pdf_data()
Processing PDF. Please wait...
CSV file "CAMS_data_04_10_2023_00_25.csv" created successfully.
>>> 
```


# Request CAS statement from CAMS
- To request your CAS file, first open the CAMS website by clicking this [link](https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement)
- Next, fill the CAS Request form by selecting the following options:
    - Statement Type: *Detailed*
    - Period: Specific Period
    - From Date: When you first started investing in mutual funds
    - To Date: Today's date
    - Folio Listing: With zero balance folios
    Enter your registered email address and create a password for your file (which you can easily remember).
    Then, click Submit.
- You will shortly receive an email from CAMSOnline with your CAS statement attached as a PDF file. Download the CAS file attachment pdf.


