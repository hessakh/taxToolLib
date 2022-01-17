"""
Tax tool utility functions
"""

import subprocess
import os, re, glob, sys

from subprocess import Popen, PIPE
from datetime import datetime

# TODO: simplify the string finding utilities. Make output of uniform type.


def get_tax_form_list():
    """
    Return a list of tax forms to process
    """

	#--Obtain all tax file names and put in list to run code on each file--
    taxfile_lst = []
    parent_dir = 'src/tests/data/2020_Returns'

    for pdf_file in glob.glob(os.path.join(parent_dir, '*.pdf')):
        taxfile_lst.append(pdf_file)

    #--Fix file names, remove \\ and replace with / for Windows compatibility
    # (file won't run in Windows without it)
    taxfile_lst_2 = []
    for elem in taxfile_lst:
        taxfile_lst_2.append(re.sub("\\\\", "/", elem))

    taxfile_lst_2 = sorted(taxfile_lst_2)

    return taxfile_lst_2

#--Original Code for pdftotext from poppler:
#--Resource 1: https://stackoverflow.com/questions/52683133/text-scraping-a-pdf-with-python-pdfquery
#--Resource 2: https://kaijento.github.io/2017/03/27/pdf-scraping-gwinnetttaxcommissioner.publicaccessnow.com/
def pdftotext(pdf, page=None):
    """
    Retrieve all text from a PDF file.

    Arguments:
        pdf: Either the path for the file or the bytes from the `.read()`.
        page: Number of the page to read. If None, read all the pages.

    Returns:
        A list of lines of text.
    """
    if isinstance(pdf, (bytes, bytearray)):
        command = ['pdftotext', '-layout', '-', '-']

        p = Popen(command, stdout=PIPE, stdin=PIPE)
        output = p.communicate(input=pdf)

        return output[0].decode().splitlines()

    if page is None:
        args = ['pdftotext', '-layout', '-q', pdf, '-']
    else:
        args = ['pdftotext', '-f', str(page), '-l', str(page), '-layout',
                '-q', pdf, '-']
    try:
        #--subprocess.check_output takes the output of a program and stores it in a string directly
        txt = subprocess.check_output(args, encoding='utf-8', universal_newlines=True) #--this works in Windows
        # txt = subprocess.check_output(args, universal_newlines=True) #--original that works in Mac
        lines = txt.splitlines()

    except subprocess.CalledProcessError:
        lines = []
    return lines

#--1. Convert from numerical (1,2) to (False,True)
def bool_conv(val):

    if val > 1:
        output = True
    elif val == 1:
        output = False
    else:
        output = 'Error, check value'

    return output


#--FINDING SUBSTRINGS IN FILES--
#--2. Find substring within file or sublist with 1 boundary--
def find_string_1bounds(bound1, file):

    output = None
    for elem in file:
        if bound1 in elem:
#             print(elem)
            output = elem
#         else:
#             output = bound1 + ' not in this file'
    return output


#--3. Find substring within file or sublist with 2 boundaries--
def find_string_2bounds(bound1, bound2, file):

    output = None

    for elem in file:
        #if bound1 and bound2 in elem:
        if bound1 in elem and bound2 in elem:
            output = elem
        #else:
        #    output = (bound1 + ' ' + bound2 + ' not in this file')
    return output


#--4. Find substring within file or sublist with 3 boundaries--
def find_string_3bounds(bound1, bound2, bound3, file):

    output = None

    for elem in file:
        if bound1 in elem and bound2 in elem and bound3 in elem:
            output = elem
#         else:
#             output = (bound1 + ' ' + bound2 + ' ' + bound3 + ' not in this file')
    return output

#--5.Check if a form exists in the Tax File--
def check_form_exist_1bound(bound1,file):

    bool_lst = []

    #--Find if form is true, if so append to list
    for elem in file:
        if bound1 in elem:
            bool_lst.append(True)
        else:
            bool_lst.append(False)
    #--if form exists, set variable to True, otherwise set it to False
    if True in bool_lst:
        exist = True
    else:
        exist = False

    return exist

#--Create Sublist with upper and lower bounds--
def sublist_1up_1low(exist, file, upper1, lower1):

    upper = 0
    lower = 0

    try:
        if exist:
            count = -1
            for elem in file:
                count += 1
                if upper1 in elem:
                    upper = count

            count = -1
            for elem in file:
                count += 1
                if lower1 in elem:
                    lower = count
            sublist = file[upper:lower]
        else:
            print(upper1 +  ' form does not exist. Please check correct form is being run.')
    except:
        sys.exit('Warning: PDF file is not in correct format. You may need to export it in a different format to the disk. Check if file has page with Listing of Forms for This Return. Fix PDF file, then try to re-run it')
    return sublist

#--num1=-1 includes upper1, num1=0 does not include upper1 in sublist result
#--num2=-1 doesn't include lower1, num2=0 includes lower1 in sublist result
#--can change the number of lines after the final string that you want included
def sublist_1up_1low_ch_count(exist, file, upper1, lower1, num1, num2):

    upper = 0
    lower = 0

    if exist:
        count = num1
        for elem in file:
            count += 1
            if upper1 in elem:
                upper = count

        count = num2 #--start at -1 to not include lower1, 0 includes lower1, etc.
        for elem in file:
            count += 1
            if lower1 in elem:
                lower = count
        sublist = file[upper:lower]
    else:
        print(upper1 +  ' form does not exist. Please check correct form is being run.')
    return sublist

#--Create Sublist with 2 upper and 1 lower bounds--
def sublist_2up_1low(exist, file, upper1, upper2, lower1):
    if exist:
        count = -1
        for elem in file:
            count += 1
            if upper1 and upper2 in elem:
                upper = count

        count = -1
        for elem in file:
            count += 1
            if lower1 in elem:
                lower = count
        sublist = file[upper:lower]
    else:
        pass
#         print(upper1 +  ' form does not exist. Please check correct form is being run.')

    return sublist


def build_exists_dictionary(text_file, QS_sublist):
    """
    Build a dictionary with information about the existence of each form

    Parameters
    ---------
    text_file : input text file
    QS_sublist : Quick Summary

    Outputs
    --------
    exists (dict)

    """

    exists = dict()

    ## Federal Form Check

    #--1. Federal 1040--
    fed1040_str = '1040 U.S. Individual Income Tax Return 2020'
    exists['Fed1040'] = check_form_exist_1bound(fed1040_str, text_file)

    #--2. Federal 1040-SR--
    fed1040SR_str = '1040-SR U.S. Tax Return for Seniors'
    exists['Fed1040SR'] = check_form_exist_1bound(fed1040SR_str, text_file)

    # Identify if forms exists using the QS_sublist
    #--3.  SSA Form
    str1_text = 'FORM SSA-1099'
    exists['SSA_income'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--4. Schedule EIC
    str1_text = 'SCHEDULE EIC'
    exists['ScheduleEIC'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--4. Schedule EIC
    str1_text = 'EARNED INCOME CREDIT WITH NO DEPENDENTS'
    exists['ScheduleEICnoDep'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--5. Federal Schedule 1
    str1_text = 'SCHEDULE 1'
    exists['fedSchedule1'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--6. Federal Schedule 2
    str1_text = 'SCHEDULE 2'
    exists['fedSchedule2'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--7. FORM 8889 Health Savings Account
    str1_text = 'FORM 8889'
    exists['fedForm8889'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--8. Federal E-file
    str1_text = 'FORM 8879'
    exists['fedForm8879'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--9. Education Tax Credit Form 8917
    str1_text = 'FORM 8917'
    exists['fedForm8917'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--10. Education Tax Credit Form 8863
    str1_text = 'FORM 8863'
    exists['fedForm8863'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--11. Schedule C
    str1_text = 'SCHEDULE C'
    exists['fedScheduleC'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--11. Schedule SE
    str1_text = ' SCHEDULE SE'
    exists['fedScheduleSE'] = check_form_exist_1bound(str1_text, QS_sublist)

    #--12. Federal Payment Voucher--
    fed1040V_str = '2020 Form 1040-V'
    exists['Fed1040V'] = check_form_exist_1bound(fed1040V_str, text_file)


    ## Michigan Form Check

    #--1. MI-1040--
    mi1040text = 'MICHIGAN Individual Income Tax Return MI-1040'
    #mi1040text_page2 = '2019 MI-1040, Page 2 of 2'
    #mi1040text_page2 = '2020 MI-1040, Page 2 of 2'   #TY20
    mi1040text_page2 = 'Pay amount on line 33 (see instructions)'
    exists['mi1040'] = check_form_exist_1bound(mi1040text, text_file)

    #--2. MI Schedule 1--
    str_sch1 = 'Deduction Based on Year of Birth'
    exists['miSched1_subtractions'] = check_form_exist_1bound(str_sch1, text_file) #--checks for Sched 1 Additions and Subtractions pages (2 pages)

    #--3. MI Schedule NR--
    schedNR_upper = 'MICHIGAN Nonresident and Part-Year Resident Schedule'
    schedNR_lower = 'here and on MI-1040, line 15........................................................................................................................   19.'
    exists['miSchedNR'] = check_form_exist_1bound(schedNR_upper, text_file)

    #--4. MI 1040 CR--
    #mi1040CR_text = '2019 MICHIGAN Homestead Property Tax Credit Claim MI-1040CR'
    mi1040CR_text = '2020 MICHIGAN Homestead Property Tax Credit Claim MI-1040CR'   #TY20
    mi1040CR_text2 = '58. Name and Address (including City, State and ZIP Code) of Housing Facility, Landowner, or Care Facility if you completed lines 54 through 57.'
    mi1040CR_text3 = 'DIRECT DEPOSIT'
    exists['mi1040CR'] = check_form_exist_1bound(mi1040CR_text, text_file)

    #--5. Client and spouse age information--
    age_upperbound1 = 'TAX YEAR: 2020'
    age_upperbound2 = 'PROCESS DATE: '
    age_lowerbound = 'LISTING OF FORMS FOR THIS RETURN'
    exists['age'] = True

    #--6. MI 1040 CR-7 Home Heating Credit
    str1_text = '2020 MICHIGAN Home Heating Credit Claim MI-1040CR-7'
    exists['mi1040cr7'] = check_form_exist_1bound(str1_text, text_file)

    #--7.  Child Tax Credit and Credit for Other Dependents Worksheet
    str1_text = 'Number of qualifying children under 17 with the required social security number:'
    exists['child_tax_worksheet'] = check_form_exist_1bound(str1_text, text_file)

    #--8. 2020 Michigan Direct Debit
    str1_text = '2020 MICHIGAN Direct Debit of Individual Income Tax Payment'
    exists['MI_direct_payment'] = check_form_exist_1bound(str1_text, text_file)

    #--9. MI E-file
    str1_text = '2808 (Rev. 07-20)'
    exists['miEfile'] = check_form_exist_1bound(str1_text, text_file)

    #--9. MI E-file
    str1_text = 'Instructions for Form MI-1040-V'
    exists['mi1040V'] = check_form_exist_1bound(str1_text, text_file)

    return exists


def extract_form_field_value(str1, string, preprocess_type=0, str2=None):
    """
    Extract numerical value from a from field

    Parameters
    ---------
        str1
            field header (e.g. '4a', '4b', '1')

        string
            substring from the form containing the target field
            (usually obtained using utils.find_string_2bounds)

        preprocess_type (int)
            indicates different ways to preprocess the string
            different forms may require different variations

        str2 (optional)
            for some preprocess_types we need extra strings.
            By default this is ignored.

    Returns
    ---------
        value: the extracted value
    """

    if preprocess_type == 1:
        string = re.split(str2, string)[1]
        string = string.replace('.','')

    str_temp = re.split(r'\s' + str1 + r'\s', string)

    try:
        value = int(str_temp[1]
                    .split()[0]
                    .lstrip()
                    .rstrip()
                    )
    except:
        value = 0

    return value



def build_sublist_dictionary(text_file, exists):
    """
    Build a dictionary of sublists.

    Sublists are subsections of the overall text file.

    Parameters
    ---------
      text_file : the entire text file from which to parse the sublists
      exists (dict)

    Outputs
    ---------
      sublist (dict)
    """

    sublist = dict()

    #---Federal 1040---
    Fed1040_sub_upper = '1040 U.S. Individual Income Tax Return 2020'
    Fed1040_sub_lower = 'Go to www.irs.gov/Form1040 for instructions and the latest information.'
    if exists['Fed1040']:
        sublist['Fed1040'] = sublist_1up_1low_ch_count(exists['Fed1040'], text_file, Fed1040_sub_upper, Fed1040_sub_lower, 0, 0)
    else:
        sublist['Fed1040'] = False

    #---Federal 1040 SR--
    Fed1040SR_sub_upper = '1040-SR U.S. Tax Return for Seniors'
    Fed1040SR_sub_lower = 'Go to www.irs.gov/Form1040SR for instructions and the latest information.'
    if exists['Fed1040SR']:
        sublist['Fed1040SR'] = sublist_1up_1low_ch_count(exists['Fed1040SR'], text_file, Fed1040SR_sub_upper, Fed1040SR_sub_lower, -1, 0)
    else:
        sublist['Fed1040SR'] = False

    mi1040text = 'MICHIGAN Individual Income Tax Return MI-1040'
    mi1040text_page2 = 'Pay amount on line 33 (see instructions)'

    schedNR_upper = 'MICHIGAN Nonresident and Part-Year Resident Schedule'
    schedNR_lower = 'here and on MI-1040, line 15........................................................................................................................   19.'

    #---MI-1040---
    if exists['mi1040']:
        #--NOTE: only gives page 1 of the MI-1040
        sublist['mi1040'] = sublist_1up_1low(exists['mi1040'], text_file, mi1040text, mi1040text_page2)
    else:
        sublist['mi1040'] = False

    #---MI Schedule NR---
    if exists['miSchedNR']:
        sublist['miSchedNR'] = sublist_1up_1low(exists['miSchedNR'], text_file, schedNR_upper, schedNR_lower)
    else:
        sublist['miSchedNR'] = False

    #--Client Age Sublist--
    age_upperbound1 = 'TAX YEAR: 2020'
    age_upperbound2 = 'PROCESS DATE: '
    age_lowerbound = 'LISTING OF FORMS FOR THIS RETURN'
#   sublist['age'] = sublist_2up_1low(exists['age'], text_file, age_upperbound1, age_upperbound2, age_lowerbound)
    sublist['age'] = sublist_1up_1low(exists['age'], text_file, age_upperbound2, age_lowerbound)


    #--1040CR--
    mi1040CR_text = '2020 MICHIGAN Homestead Property Tax Credit Claim MI-1040CR'   #TY20
    mi1040CR_text2 = '58. Name and Address (including City, State and ZIP Code) of Housing Facility, Landowner, or Care Facility if you completed lines 54 through 57.'
    mi1040CR_text3 = 'DIRECT DEPOSIT'
    if exists['mi1040CR']:
#       sublist['mi1040CR'] = sublist_1up_1low(exists['mi1040CR'], text_file, mi1040CR_text, mi1040CR_text2)
        sublist['mi1040CR'] = sublist_1up_1low_ch_count(exists['mi1040CR'], text_file, mi1040CR_text, mi1040CR_text2, -1, 5)
    else:
        sublist['mi1040CR'] = False

    #--Child Tax Credit and Credit for Other Dependents Worksheet
    if exists['child_tax_worksheet']:
        CTC_sub_upper = 'Before you begin:                   Figure the amount of any credits you are claiming on Schedule 3, lines 1 through 4;'
        CTC_sub_lower = 'Subtract line 9 from line 3. Enter the result.'
        sublist['CTC'] = sublist_1up_1low_ch_count(True, text_file, CTC_sub_upper, CTC_sub_lower, 0, 0)
    else:
        sublist['CTC'] = False

    #--SSA sublist
    if exists['SSA_income']:
        SSA_sub_upper = '* FORM SSA-1099 INCOME FORMS SUMMARY *'
        SSA_sub_lower = 'TOTALS......'
        sublist['SSA'] = sublist_1up_1low_ch_count(True, text_file, SSA_sub_upper, SSA_sub_lower, 0, 0)
    else:
        sublist['SSA'] = False

    #--Schedule EIC sublist
    if exists['ScheduleEIC']:
        EIC_sub_upper = 'SCHEDULE EIC                                                  Earned Income Credit'
        EIC_sub_lower = 'Schedule EIC (Form 1040) 2020'
        sublist['EIC'] = sublist_1up_1low_ch_count(True, text_file, EIC_sub_upper, EIC_sub_lower, 0, 0)
    else:
        sublist['EIC'] = False

    if exists['ScheduleEIC'] or exists['ScheduleEICnoDep']:
        EIC_Worksheet_upper = 'A—2020 EIC—Line 27'
        EIC_Worksheet_lower = 'Part 7            11.   This is your earned income credit.'
        sublist['EIC_Worksheet'] = sublist_1up_1low_ch_count(True, text_file, EIC_Worksheet_upper, EIC_Worksheet_lower, 0, 0)
    else:
        sublist['EIC_Worksheet'] = False

    return sublist


def define_column_list():
    """
    Define a list of columns for the client tax information
    """

    col_list = ['Filename',
               'DateTime_tool_was_run',
               'TaxFormProcessDate',
               'client_name',
               'client_age', 'client_birthyr', 'spouse_exist', 'spouse_age', 'spouse_birthyr',
               'dependent_listed', 'num_dependents', 'dep_under_17', 'dep_under_24', 'dep_under_6', 'dep_under_2', 'fed_filing_status', 'fed_direct_debit', 'SSA_income_exist', 'medicare_payment',
               'Fed1040SR_exist', 'Fed1040_exist', 'Fed1040_dependent', 'Fed1040_1', 'other_income', 'Fed1040_2b', 'Fed1040_4a', 'Fed1040_4b', 'Fed1040_5a', 'Fed1040_5b', 'Fed1040_6a', 'Fed1040_8',
               'Fed1040_9', 'Fed1040_11', 'Fed1040_19', 'Fed1040_27', 'Fed1040_28',
               'ScheduleEIC_exist', 'fed_earned_income', 'num_eic_dep', 'EITC_limit', 'EIC_PY_earned_income_used', 'EIC_WorksheetB_6', 'EIC_WorksheetB_7', 'EIC_WorksheetB_10', 'child_tax_worksheet_exist',
               'num_dep_ctc', 'num_credit_other_dep', 'fedSchedule1_exist', 'FedSch1_3', 'FedSch1_7', 'FedSch1_12', 'FedSch1_14', 'fedSchedule2_exist', 'FedSch2_4', 'FedSch2_6', 'fedForm8889_exist',
               'FedForm8889_17b', 'fedForm8879_exist (Efile)', 'MI Direct Debit exist', 'mi1040exist', 'mi1040_7a', 'mi1040_7b', 'mi1040_7c', 'mi1040_8a', 'mi1040_8b', 'mi1040_8c', 'mi1040_9b', 'mi1040_9c',
               'mi1040_12', 'mi1040_25', 'MI_exemptions', 'mi_THR', 'miSched1_exist_subtractions', 'miSched1_25', 'miSchedNR_exist', 'miSchNR_c1', 'miSchNR_c2', 'miSchNR_s1', 'miSchNR_s2',
               'month_residence_client', 'month_residence_spouse', 'mi1040CR_exist', 'mi1040CR_10', 'mi1040CR_21', 'mi1040CR_31', 'mi1040CR_33',
               'mi1040CR_51', 'mi1040CR_53', 'mi1040CR_54a', 'mi1040CR_54b', 'mi1040CR_55', 'mi1040CR_57',
               'mi1040cr7_exist', 'hhc_income_limit', 'hhc_eligable', 'mi1040cr7_35', 'rule1_df', 'rule2_df', 'rule4_df', 'rule5_df',
               'rule10_df', 'rule11_df', 'rule12_df', 'rule13_df', 'rule14_df', 'rule15_df', 'rule16_df', 'rule18a_df', 'rule18b_df', 'rule19_df', 'rule21_df', 'rule22_df',
               'rule23_df', 'rule24_df', 'rule25_df', 'rule26_df', 'rule27_df', 'rule28_df', 'rule29_df', 'rule30_df', 'rule31_df']

    return col_list


def get_time_info(age_sublist):
    """
    Fetch time information from the tax form and the OS

    Parameters
    ---------
    age_sublist

    Outputs
    ---------
    Process date (string)
    Code run datetime (datetime)
    """

    dateTimeObj = datetime.now()
    run_code_datetime = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")[:-4]

    #=====================================
    #------------timestamp---------------
    #=====================================
    tax_yr_text = 'TAX YEAR: 2020'
    process_date = 'PROCESS DATE: '

    #--Find and extract substring with timestamp information: labeled 'PROCESS DATE'
    timestamp_fullstr = find_string_2bounds(tax_yr_text, process_date, age_sublist)

    #--get date string after process_date text; add this one to dataframe
    timestamp_str = timestamp_fullstr.split(process_date)[1]

    #--use RegEx to separate date in case there is any other information in the string
    match = re.search('\d{2}/\d{2}/\d{4}', timestamp_str)

    #--create datetime in case there is a need for getting extra info from process date
    timestamp = datetime.strptime(match.group(), '%m/%d/%Y').date()

    return timestamp_str, run_code_datetime
