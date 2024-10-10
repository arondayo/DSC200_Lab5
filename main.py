import slate3k
import csv
import re

pdfFilename = "data/Table9.pdf"
DEBUG = True

with open(pdfFilename, "rb") as pdfFileObject:
    # Getting raw data
    doc = slate3k.PDF(pdfFileObject)
    page_data = []
    for page in doc:
        page_data.append(page.split("\n\n"))
    if DEBUG: print(f"Raw page_data:\n{page_data}\n")

    # Getting headers
    # headers = page_data[0][-24:-2]

    # pulled from last assignment because I'm lazy and it'll work for now
    headers_dict = {
        'B': 'Countries and areas',
        'E': 'Child labour (%)+2005–2012*_total',
        'G': 'Child labour (%)+2005–2012*_male',
        'I': 'Child labour (%)+2005–2012*_female',
        'K': 'Child marriage (%)2005–2012*_married by 15',
        'M': 'Child marriage (%)2005–2012*_married by 18',
        'O': 'Birth registration (%)+2005–2012*_total',
        'Q': 'Female genital mutilation/cutting (%)+2002–2012*_prevalence_womena  ',
        'S': 'Female genital mutilation/cutting (%)+2002–2012*_prevalence_girlsb ',
        'U': 'Female genital mutilation/cutting (%)+2002–2012*_attitudes_support for the practicec',
        'W': 'Justification of wife beating (%) 2005–2012*_male',
        'Y': 'Justification of wife beating (%) 2005–2012*_female',
        'AA': 'Violent discipline (%)+2005–2012*_total',
        'AC': 'Violent discipline (%)+2005–2012*_male',
        'AE': 'Violent discipline (%)+2005–2012*_female'
    }

    headers = list(headers_dict.values())
    if DEBUG: print(f"Raw headers (len: {len(headers)}):\n{headers}\n")
    # TODO produce clean headers directly from pdf file ?

    # Cleaning data
    i = 0
    for i in range(len(page_data)):
        if i == 0:
            # (Discard first 6 elements, find where the data stops and discard from then on)
            page_data[i] = page_data[i][6:]
            cutoff = 0
            for item in page_data[i]:
                if re.findall("TABLE 9", item):
                    cutoff = page_data[i].index(item)
            page_data[i] = page_data[i][:cutoff]
            if DEBUG: print(f"Data from page {i}, Length: {len(page_data[i])}\n{page_data[i]}")
        else:
            # (Discard first 7 elements, find where the data stops and discard from then on)
            page_data[i] = page_data[i][7:]
            cutoff = 0
            if i != len(page_data) - 1:
                for item in page_data[i]:
                    if re.findall("TABLE 9", item):
                        cutoff = page_data[i].index(item)
            else:
                for item in page_data[i]:
                    if re.findall("SUMMARY", item):
                        cutoff = page_data[i].index(item)
            page_data[i] = page_data[i][:cutoff]
            if DEBUG: print(f"Data from page {i}, Length: {len(page_data[i])}\n{page_data[i]}")

    # Separate all the data into rows like it is in the pdf document
    rows = []
    i = 0
    for raw_row in page_data:
        for i in range(int(len(raw_row) / 15)):  # each row is 15 cells long
            rows.append(raw_row[(15 * i):(15 * (i + 1))])

    # Cleaning cell data
    for row in rows:
        #   Example:
        #     [
        #         "Bolivia (Plurinational \n   State of) ",
        #         "26 x ",
        #         "24 x,y ",
        #         "–  ",
        #         "16  ",
        #         "–",
        #     ]
        #   Cleans to:
        #     [
        #         "Bolivia (Plurinational State of) ",
        #         "26",
        #         "24",
        #         "–",
        #         "16",
        #         "–",
        #     ]
        i = 0
        for i in range(len(row)):
            row[i] = row[i].strip()  # strips trailing whitespace
            row[i] = row[i].replace("\n   ", "")  # removes newline + whitespace in country names
            if re.match("[0-9]* [A-z,]*", row[i]):  # removes the extra stuff after numbers
                row[i] = row[i].split(" ")[0]

    if DEBUG: print(f"\nCleaned data (Rows: {len(rows)}, Cells per row: {len(rows[0])}):\n{rows}")

# TODO: add logic to discard row if it only contains '-'

# TODO: write to csv file
