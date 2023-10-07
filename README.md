------------------
# CAMSPdfExtractor
------------------

- [Introduction](#introduction)
- [How to use](#how-to-use)
- [Request CAS statement from CAMS](#request-cas-statement-from-cams)
- [TODO](#todo)

------------------
## Introduction
------------------
Tool/Library that will extract CAMS Mutual fund PDF statement (India) data into either
- csv file
- dataframe
- json string
- list of dicts


This tool was designed after looking at how [@SudheerNotes](https://github.com/SudheerNotes) implemented his tool [cams2csv](https://github.com/SudheerNotes/cams2csv).

------------------
------------------
## How to use
First you need to request CAMS detailed Mutual Fund statement from CamsOnline ([How To?](#request-cas-statement-from-cams))

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
                                             fund_name          isin scheme_code         folio_num  ...     amount     units       nav balance_units
0    Aditya Birla Sun Life Liquid Fund - Growth-Dir...  INF209K01VA3      119568        1039837274  ...  360000.00  1122.052  320.8408      1122.052
..                                                 ...           ...         ...               ...  ...        ...       ...       ...           ...
655        UTI Nifty Next 50 Index Fund - Direct Plan   INF789FC12T1      143341  599321413667 / 0  ...   99995.00  6358.740   15.7256     86737.464
[656 rows x 10 columns]
>>> 
>>> 
>>> # If you want to dump it to csv file, you do like below
>>> 
>>> out = pp.get_pdf_data()
Processing PDF. Please wait...
CSV file "CAMS_data_04_10_2023_00_25.csv" created successfully.
>>> 
```

Sample CSV file format

!['samplecsv.png'](/img/samplecsv.png)


- You can set the `output_format` for `get_pdf_data` method to be `dicts` or `json` or `df` incase you want to further process the data in your applications
- `output_format`  can be set to `csv` if you want to use it for other tools developed by say [freefincal](https://freefincal.com/track-your-mutual-fund-and-stock-investments-with-this-google-sheet/) or others you might still need to modify the csv according to the tool, but that should be a trivial job in my opinion 

------------------

------------------
## Request CAS statement from CAMS
- To request your CAS file, first open the CAMS website by clicking this [link](https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement)
  
!['CAS1.1.png'](/img/CAS1.1.png)

- Next, fill the CAS Request form by selecting the following options:
    - Statement Type: **Detailed**
    - Period: **Specific Period**
    - From Date: **When you first started investing in mutual funds**
    - To Date: **Today's date**
    - Folio Listing: **With zero balance folios**
    
  Enter your registered email address and create a password for your file (which you can easily remember).
  Then, click **Submit**.

!['CAS2.1.png'](/img/CAS2.1.png)

- You will shortly receive an email from CAMSOnline with your CAS statement attached as a PDF file. Download the CAS file attachment pdf.
  
!['CAS3.1.png'](/img/CAS3.1.png)

------------------

------------------
## TODO
- Add a GUI if needed to get CSV data instead of executing via cmdline
