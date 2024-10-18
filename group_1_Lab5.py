import slate3k
import csv
import re

pdfFilename = "data/Table9.pdf"
DEBUG = False

with open(pdfFilename, "rb") as pdfFileObject:
    # Getting raw data
    doc = slate3k.PDF(pdfFileObject)
    page_data = []
    for page in doc:
        page_data.append(page.split("\n\n"))
    if DEBUG: print(f"Raw page_data:\n{page_data}\n")

    # Getting headers
    # pulled from last assignment
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
            row[i] = row[i].replace("\n   ", "")  # removes newline+whitespace in country names
            if re.match("[0-9]* [A-z,]*", row[i]):  # removes the extra stuff after numbers
                row[i] = row[i].split(" ")[0]

            # NOTE:
            # the "–" characters extracted from the pdf are:
            #   U+2013 : EN DASH
            # which is not the same character from the -_ key on the keyboard:
            #   U+002D : HYPHEN-MINUS {hyphen, dash; minus sign}
            if re.match(r"–", row[i]):
                row[i] = None

    # logic to discard row if it only contains '-'
    # for each row in rows, iterate through the row from [1:], if it's all None mark the row for deletion
    i = 0
    rows_to_delete = []
    for i in range(len(rows)):
        marked_for_deletion = True
        for entry in rows[i][1:]:
            if entry is not None:
                marked_for_deletion = False
                break
        if marked_for_deletion:
            rows_to_delete.append(i)

    # deletion process iterates through backwards to avoid index shifting affecting the next deletion target
    for index in sorted(rows_to_delete, reverse=True):
        del rows[index]

    if DEBUG: print(f"\nCleaned data (Rows: {len(rows)}, Cells per row: {len(rows[0])}):\n{rows}")

# # write to csv file
# with open("data/group_1_Lab5_unflattened.csv", "w") as file_pointer:
#     writer = csv.writer(file_pointer, delimiter=",", lineterminator="\n")
#     writer.writerow(headers)
#     writer.writerows(rows)
#     file_pointer.close()


# Flattening to output format (adapted from lab 4)
output_headers = ["CountryName", "CategoryName", "CategoryTotal"]
output_list = []
for data in rows:  # Loop through each country's data from rows
    row = []
    country = data[0]
    row.append(country)  # set the country name for the CountryName column
    i = 1  # Keeps track of which data element the loop is on
    for value in headers:  # Loops through each header for each country
        if value == "Countries and areas":
            continue
        row.append(value)  # Add in the value for the CategoryName column
        if i < len(data):  # Ensure i does not go out of bounds
            if data[i] is None:  # Check if the row is equal to zero or a -, throw out if true
                i += 1
                row = [country]  # Reset the row list to be ready for the next iteration
                continue
            else:  # add in the value for the CategoryTotal Column
                row.append(data[i])
        i += 1
        output_list.append(row)  # Add the row to the output list
        row = [country]  # Reset the row list to be ready for the next iteration

# Write output_headers and output_list to csv file
with open("data/group_1_Lab5.csv", "w") as outfile:
    csvWriter = csv.writer(outfile, lineterminator='\n')
    csvWriter.writerow(output_headers)
    count = 0
    for row in output_list:
        csvWriter.writerow(row)
        count += 1

# print the number of rows outputted to the csv
print("There are {} rows in the csv!".format(count))
