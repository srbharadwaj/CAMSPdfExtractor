"""
# A tool/library that will extract CAMS Mutual fund PDF statement (India) data 
# into either a csv file or dataframe or json string or list of dicts
#
# Below is an example on how to use it
# 
#   >>> 
#   >>> from camspdf import ProcessPDF
#   >>> filename = "testfile.pdf"
#   >>> password = "Check123"
#   >>> pp = ProcessPDF(filename, password)
#   >>> out = pp.get_pdf_data(output_format="df")  # output_format can be either be "dicts", "csv", "json", "df"
#   Processing PDF. Please wait...
#   >>> print(out)
#                                                fund_name          isin         folio_num         date   txn     amount     units       nav  balance_units
#   0    Aditya Birla Sun Life Liquid Fund - Growth-Dir...  INF209K01VA3        1039837274  26-Apr-2020   Buy  360000.00  1122.052  320.8408       1122.052
#   1    Aditya Birla Sun Life Liquid Fund - Growth-Dir...  INF209K01VA3        1039837274  21-Mar-2021   Buy  199990.00   603.877  331.1767       1725.929
#   ..                                                 ...           ...               ...          ...   ...        ...       ...       ...            ...
#   654        UTI Nifty Next 50 Index Fund - Direct Plan   INF789FC12T1  599321413667 / 0  19-Oct-2022   Buy   39998.00  2611.841   15.3141      80378.724
#   655        UTI Nifty Next 50 Index Fund - Direct Plan   INF789FC12T1  599321413667 / 0  26-Jun-2023   Buy   99995.00  6358.740   15.7256      86737.464
#   
#   [656 rows x 9 columns]
#   >>> 
#   >>> 
#   >>> # If you want to dump it to csv file, you do like below
#   >>> 
#   >>> out = pp.get_pdf_data()
#  Processing PDF. Please wait...
#  CSV file "CAMS_data_04_10_2023_00_25.csv" created successfully.
#  >>> 
#  
#
# This tool was designed after looking at how @SudheerNotes implemented 
# his tool cams2csv (https://github.com/SudheerNotes/cams2csv/)
#
#
# Copyright (c) 2023, Suhas Bharadwaj <@srbharadwaj>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""

import os
import re
from datetime import datetime
from dataclasses import dataclass, asdict
import csv
import json
import traceback
import pdfplumber
import pandas as pd


basedir = os.path.dirname(__file__)


# Defining RegEx patterns
REGULAR_BUY_TXN = r"(?P<date>\d+\-\S+\-\d+)\s+(?P<txn>.*)\s+(?P<amount>[0-9]+\.[0-9]*)\s+(?P<units>[0-9]+\.[0-9]*)\s+(?P<nav>[0-9]+\.[0-9]*)\s+(?P<unitbalance>[0-9]+\.[0-9]*).*"
REGULAR_SELL_TXN = r"(?P<date>\d+\-\S+\-\d+)\s+(?P<txn>.*)\s+(?P<amount>\([0-9]+\.[0-9]*\))\s+(?P<units>\([0-9]+\.[0-9]*\))\s+(?P<nav>[0-9]+\.[0-9]*)\s+(?P<unitbalance>[0-9]+\.[0-9]*).*"
SEGR_BUY_TXN = r"(?P<date>\d+\-\S+\-\d+)\s+(?P<txn>.*)\s+(?P<units>[0-9]+\.[0-9]*)\s+(?P<unitbalance>[0-9]+\.[0-9]*).*"
FOLIO_PAN = r"^Folio No:\s+(?P<folio_num>.*)\s+PAN:\s+(?P<pan>[A-Z,0-9]{10})"
FNAME_ISIN = r"^\S+\-(?P<fund_name>.*)\s*\-\s*ISIN:\s+(?P<isin>[A-Z,0-9]+)(\(?P<advisor>Advisor:\s+\S+\))?.*"


@dataclass
class _FundDetails:
    fund_name: str
    isin: str
    folio_num: str
    date: str
    txn: str
    amount: float
    units: float
    nav: float
    balance_units: float


class _ProcessTextFile:
    def __init__(
        self,
        alllines="text.txt",
    ) -> None:
        self.alldata = []
        if alllines == "text.txt":
            with open(alllines, "r") as f:
                self.alllines = f.readlines()
        else:
            self.alllines = alllines
        self.process()

    def write_to_csv(self, csv_file_name=None):
        if csv_file_name is None:
            csv_file_name = f'CAMS_data_{datetime.now().strftime("%d_%m_%Y_%H_%M")}.csv'
        # Get the fieldnames from the Item dataclass
        fieldnames = [
            field.name for field in _FundDetails.__dataclass_fields__.values()
        ]

        # Write the list of dataclass objects to the CSV file
        with open(csv_file_name, mode="w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            # Write the header
            writer.writeheader()

            # Write the data
            for item in self.alldata:
                d = {}
                for f in fieldnames:
                    d[f] = getattr(item, f)
                writer.writerow(d)

        print(f'CSV file "{csv_file_name}" created successfully.')

    def process(self):
        if not self.alllines:
            return
        folio_num = ""
        fund_name = ""
        isin = ""
        for eachline in self.alllines:
            m = re.match(FOLIO_PAN, eachline)
            if m:
                folio_num = m.groupdict().get("folio_num")
                continue

            m = re.match(FNAME_ISIN, eachline)
            if m:
                fund_name = m.groupdict().get("fund_name")
                isin = m.groupdict().get("isin")
                continue

            m = re.match(REGULAR_BUY_TXN, eachline)
            if m:
                date = m.groupdict().get("date")
                txn = "Buy"
                amount = m.groupdict().get("amount")
                units = m.groupdict().get("units")
                nav = m.groupdict().get("nav")
                balance_units = m.groupdict().get("unitbalance")

                # date_format = "%d-%b-%Y"  # Specify the format of the input date string
                # # Convert the string to a datetime object
                # date_obj = datetime.strptime(date, date_format)

                t = _FundDetails(
                    folio_num=folio_num,
                    fund_name=fund_name,
                    isin=isin,
                    date=date,
                    txn=txn,
                    amount=amount,
                    units=units,
                    nav=float(nav),
                    balance_units=float(balance_units),
                )
                self.alldata.append(t)
                continue

            m = re.match(REGULAR_SELL_TXN, eachline)
            if m:
                date = m.groupdict().get("date")
                txn = "Sell"
                amount = m.groupdict().get("amount")
                amtstring = re.sub(r"\(|\)", "", amount)
                units = m.groupdict().get("units")
                unitstring = re.sub(r"\(|\)", "", units)
                nav = m.groupdict().get("nav")
                balance_units = m.groupdict().get("unitbalance")

                # date_format = "%d-%b-%Y"  # Specify the format of the input date string
                # # Convert the string to a datetime object
                # date_obj = datetime.strptime(date, date_format)
                t = _FundDetails(
                    folio_num=folio_num,
                    fund_name=fund_name,
                    isin=isin,
                    date=date,
                    txn=txn,
                    amount=float(amtstring),
                    units=float(unitstring),
                    nav=float(nav),
                    balance_units=float(balance_units),
                )
                self.alldata.append(t)
                continue

            m = re.match(SEGR_BUY_TXN, eachline)
            if m:
                date = m.groupdict().get("date")
                txn = "Buy"
                amount = "0"
                units = m.groupdict().get("units")
                nav = "0"
                balance_units = m.groupdict().get("unitbalance")

                date_format = "%d-%b-%Y"  # Specify the format of the input date string
                # Convert the string to a datetime object
                date_obj = datetime.strptime(date, date_format)
                t = _FundDetails(
                    folio_num=folio_num,
                    fund_name=fund_name,
                    isin=isin,
                    date=date,
                    txn=txn,
                    amount=amount,
                    units=units,
                    nav=float(nav),
                    balance_units=float(balance_units),
                )
                self.alldata.append(t)
                continue


class ProcessPDF:
    def __init__(self, filename, password) -> None:
        self.filename = filename
        self.password = password
        self.alldata = []

    def get_pdf_data(self, output_format="csv"):
        file_path = self.filename
        doc_pwd = self.password
        final_text = ""
        print("Processing PDF. Please wait...")
        try:
            with pdfplumber.open(file_path, password=doc_pwd) as pdf:
                for i in range(len(pdf.pages)):
                    txt = pdf.pages[i].extract_text()
                    final_text = final_text + "\n" + txt
                pdf.close()
            # Replace all occurrences of ',' with an empty string
            final_text = final_text.replace(",", "")
            # print("Text found, writing to file")
            # with open("text.txt", "w+") as f:
            #     f.write(final_text)
            # self.extract_text(final_text)
            format_specifiers = ["dicts", "csv", "json", "df"]
            if output_format not in format_specifiers:
                raise Exception(
                    f"Error!! Output format can be one of {','.join(format_specifiers)}"
                )
            pt = _ProcessTextFile(alllines=final_text.splitlines())

            if output_format == "csv":
                pt.write_to_csv()
            else:
                item_dicts = [asdict(item) for item in pt.alldata]
                if output_format == "df":
                    # Convert the list of dictionaries to a DataFrame
                    df = pd.DataFrame(item_dicts)
                    return df
                elif output_format == "json":
                    json_string = json.dumps(item_dicts)
                    return json_string
                else:
                    return item_dicts
        except Exception as ex:
            print(ex)
            traceback.print_exc()
