#  scrape_candidates.py
#  
#  Please note this code uses selenium to control a firefox webbrowser.  
#  For it to work properly, you must have Firefox installed on your 
#  machine.
#  Some users may also need to download the latest executable geckodriver, 
#  which is available here:  https://github.com/mozilla/geckodriver/releases
#  Make sure selenium can find the path to the geckodriver executable.  


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os, csv, time

browser = webdriver.Firefox()

jurisdiction_list = ["City of Atlanta", "Fulton"]

at_large_offices = ["Atlanta City Mayor", 
                    "Atlanta City Council President", 
                    "Atlanta City Municipal Court Judge",
                    "Ballot Committee",
                    "Chief Magistrate Judge",
                    "Clerk of Superior Court",
                    "Judge of the Probate Court",
                    "Sheriff",
                    "Solicitor General",
                    "State Court Judge",
                    "Surveyor",
                    "Tax Commissioner"]


def click_next_page():
    """ Click the button that takes browser to next page of results """
    
    global browser
    time.sleep(4)
    try:
        next_button = browser.find_element_by_class_name("dxWeb_pNext")
        time.sleep(1)
        next_button.click()
        time.sleep(1)
        return True
    
    #  If you're already on the last page of results, the next page  
    #  button won't be active, so trying to find it will throw an error.
    except:
        print "False!"
        return False
        pass


def check_for_DOI(candidate_row):
    """ 
    Find the button used to reveal the document list for each 
    candidate, click it, then check for a "DOI" doc in the third column
    """

    global browser
    
    #We'll need this id to find our way back when the AJAX gets odd with the DOM
    doc_table_id = candidate_row.get_property("id").replace("DXDataRow", "DXDRow")
       
    doc_reveal_button = candidate_row.find_element_by_class_name("dxgvDetailButton")
    doc_reveal_button.click()
    time.sleep(2)
    
    #The DOM does something funky when the table is revealed.  So we have to use the element id.
    doc_table = browser.find_element_by_id(doc_table_id)
    doc_list = doc_table.find_elements_by_class_name("dxgvDataRow")
    
    DOI_date = [f.find_elements_by_class_name("dxgv")[1].text for f in doc_list if f.find_elements_by_class_name("dxgv")[2].text == "DOI"]
    #DOI_date is going to be a list because some candidates have more than one DOI doc

    #close the doc list
    #doc_reveal_button.click()
    time.sleep(1)
    
    if DOI_date:
        return DOI_date
    else:
        return ""
    

def clean_up_entry(candidate_row_entry):
    """Parse out district from office name."""
    global jurisdiction
    global at_large_offices
    candidate_row_entry[0] = jurisdiction
    if candidate_row_entry[3] in at_large_offices:
        district = "At Large"
    else:
        district = candidate_row_entry[3].replace("Atlanta Bd of Education Member District ", "").replace("Atlanta City Council Member District ", "").replace("Atlanta City Council Member Post 1 ", "").replace("Atlanta City Council Member Post 2 ", "").replace("Atlanta City Council Member Post 3 ","").replace("Board of Commission District ","").replace("Board of Education District ","")
    
    candidate_row_entry.append(district)
    return candidate_row_entry

def fetch_candidate_tables_by_jurisdiction(jurisdiction):
    """ 
    Open financial reporting webage and goes to results for a specific
    jurisdiction.
    """

    global browser
    more_pages = True

    browser.get("http://gaeasyfile.com")
    time.sleep(1)
    #Find the text box for entering the jurisdiction name
    dropdown_list = browser.find_element_by_id("ContentPlaceHolder1_cbCountyList_I")
    
    dropdown_list.send_keys(jurisdiction)
    time.sleep(1)
    dropdown_list.send_keys(Keys.TAB)
    time.sleep(1)
    dropdown_list.send_keys(Keys.ENTER)
    time.sleep(1)
    
    while more_pages == True:
        candidate_file = open("atlanta_candidates.csv", "ab")
        
        writer = csv.writer(candidate_file)
              
        # get id attribute for each row in table since we can't 
        # iterate over the table itself and click the buttons
        row_ids = [table_row.get_attribute("id") for table_row in browser.find_elements_by_class_name("dxgvDataRow")]
        
        for i in row_ids:
            table_row = browser.find_element_by_id(i)
            candidate_details = clean_up_entry([column.text for column in table_row.find_elements_by_tag_name("td")])
            DOI_details = check_for_DOI(table_row)
            
            candidate_details.append(DOI_details)
            print candidate_details
            writer.writerow(candidate_details)
            
            time.sleep(1)

        #close the file and reopen it every time because I get nervous.
        candidate_file.close()

        more_pages = click_next_page()
        

def main(args):
    global jurisdiction
    candidate_file = open("atlanta_candidates.csv", "wb")
    writer = csv.writer(candidate_file)
    writer.writerow(["Jurisdiction", "Last Name", "First Name", "Office", "District", "DOI Filed"])
    candidate_file.close()
    for jurisdiction in jurisdiction_list:
        fetch_candidate_tables_by_jurisdiction(jurisdiction)
    print "file saved to ", os.getcwd()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
