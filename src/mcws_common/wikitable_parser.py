# code taken from 
# https://kiwiphrases.github.io/coding/example/2019/06/17/wikipedia-table-parser.html

##Libraries used are:
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import requests
from bs4 import Tag

def pre_process_table(table:Tag):
    """
    INPUT:
        1. table - a bs4 element that contains the desired table: ie <table> ... </table>
    OUTPUT:
        a tuple of: 
            1. rows - a list of table rows ie: list of <tr>...</tr> elements
            2. num_rows - number of rows in the table
            3. num_cols - number of columns in the table
            4. caption - caption of table if exists
    """
    
    # find title if exists
    caption=None
    if caption:=table.find('caption'):
        caption = caption.get_text(strip=True)
        # print(f"{caption=}")
    
    
    rows = [x for x in table.find_all('tr')]

    num_rows = len(rows)
    
    ## get table's column count. Most of often, this will be accurate
    num_cols = max([len(x.find_all(['th','td'])) for x in rows])

    ## ...on occasion, the above fails because some columns have colspan attributes too. The below accounts for that:
    header_rows_set = [x.find_all(['th', 'td']) for x in rows if len(x.find_all(['th', 'td']))>num_cols/2]
    
    num_cols_set = []

    for header_rows in header_rows_set:
        num_cols = 0
        for cell in header_rows:
            row_span, col_span = get_spans(cell)
            num_cols+=len([cell.getText()]*col_span)
            
        num_cols_set.append(num_cols)
    
    num_cols = max(num_cols_set)
    #print(num_cols)
    
    return (rows, num_rows, num_cols, caption)


def get_spans(cell):
        """
        INPUT:
            1. cell - a <td>...</td> or <th>...</th> element that contains a table cell entry
        OUTPUT:
            1. a tuple with the cell's row and col spans
        """
        if cell.has_attr('rowspan'):
            rep_row = int(cell.attrs['rowspan'])
        else: # ~cell.has_attr('rowspan'):
            rep_row = 1
        if cell.has_attr('colspan'):
            rep_col = int(cell.attrs['colspan'])
        else: # ~cell.has_attr('colspan'):
            rep_col = 1 
        
        return (rep_row, rep_col)
 
def process_rows(rows, num_rows, num_cols,caption=None):
    """
    INPUT:
        1. rows - a list of table rows ie <tr>...</tr> elements
    OUTPUT:
        1. data - a Pandas dataframe with the html data in it
    """
        
    # data = pd.DataFrame(np.ones((num_rows, num_cols))*np.nan)
    data = pd.DataFrame(np.full((num_rows, num_cols), np.nan, dtype=object))
    if caption is not None:
        data.Name = caption
    for i, row in enumerate(rows):
        col_stat = data.iloc[i,:][data.iloc[i,:].isnull()].index[0]

        for j, cell in enumerate(row.find_all(['td', 'th'])):
            rep_row, rep_col = get_spans(cell)

            #print("cols {0} to {1} with rep_col={2}".format(col_stat, col_stat+rep_col, rep_col))
            #print("\trows {0} to {1} with rep_row={2}".format(i, i+rep_row, rep_row))

            #find first non-na col and fill that one
            while any(data.iloc[i,col_stat:col_stat+rep_col].notnull()):
                col_stat+=1

            data.iloc[i:i+rep_row,col_stat:col_stat+rep_col] = cell.getText()
            if col_stat<data.shape[1]-1:
                col_stat+=rep_col

    return data

def fetch_website(url):
    ## apply a more friendly user agent
    user_agent={'User-agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.18 Safari/537.36'}
    r=requests.get(url, headers=user_agent)
    try:
        #print("Accessed and downloaded URL data")
        return(r.content)
    except ConnectionError:
        print("Skipping this url")
        return(None)    
    
def main(table):
    """
    DESCRIPTION:
        Parse one table and return a Pandas DataFrame
    """
    import pandas as pd
    import numpy as np
    from bs4 import BeautifulSoup as bs
    
    rows, num_rows, num_cols = pre_process_table(table)
    df = process_rows(rows, num_rows, num_cols)
    return(df)

def set_first_row_as_header(df):
    df.columns = df.iloc[0]         # Set first row as column headers
    df = df[1:].reset_index(drop=True)  # Drop the first row and reset index
    return df