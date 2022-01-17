"""
A collection of methods used to extract values from different tax forms
"""

import re
from datetime import datetime
from dateutil import relativedelta

from . import utils


def parse_client_summary_sheet(age_sublist, QS_sublist, text_file,
                               ssa_income_exists, ssa_sublist=None
                               ):
    """
    TODO: get rid of dependence on entire text_file which introduces
          unnecessary coupling
    """


    values = dict()

    client_text1 = 'CLIENT'
    client_text2 = 'BIRTH DATE'
    client_text3 = 'Age:'
    spouse_text1 = 'SPOUSE'

    #--1. Extract text that includes the age and birth_yr of the client and spouse (if spouse exists) from sublist['age']--
    client_age_lst = []
    spouse_age_lst = []
    spouse_bool_lst = []

    for elem in age_sublist:
        if client_text1 in elem:
            client_age_lst.append(elem)

    #--create string for elements in sublist['age'], see if SPOUSE exists--
    for elem in age_sublist:
        if spouse_text1 in elem:
            spouse_bool_lst.append(True)
            spouse_age_lst.append(elem)
        else:
            spouse_bool_lst.append(False)

    #--2. Extract Client Name--
    m = client_age_lst[0].split('BIRTH')[0]
    #pattern2 = '\d{3}-\d{2}-\d{4}' #--remove social security number
    #--remove social security number TY20
    pattern2 = '\d{3}-\d{2}-\d{4}'
    str_name = re.sub(pattern2, '', m)
    str_name1 = re.sub('CLIENT', '', str_name)
    str_name2 = re.sub(':', '', str_name1)
    client_name = str_name2.lstrip().rstrip()


    #--3a. Find age and birth_yr for client --
    #--split client_age_lst on 'Age:' to extract age number and convert to int
    client_age = int(client_age_lst[0].split('Age:')[1])
    #match = re.search('\d{2}/\d{2}/\d{4}', client_age_lst[0]) #--use regex to extract birthdate from birth info string, then convert to datetime to extract birth year
    #client_birthyr = datetime.strptime(match.group(), '%m/%d/%Y').date()
    #client_birthyr = client_birthyr.year
    #--use regex to extract birthdate from birth info string, then convert to datetime to extract birth year TY20
    match = re.search('/\d{4}', client_age_lst[0])
    client_birthyr = match.group() #TY20
    client_birthyr = int(re.sub('/', '', client_birthyr)) #TY20


    #--3b. Find if spouse exists, if spouse exists, extract age and birth_yr for spouse --
    if True in spouse_bool_lst: #--check if spouse information is in sublist, if it is, find age and birth_yr, if not, set those variables to 0
        spouse = True
        spouse_age = int(spouse_age_lst[0].split('Age:')[1]) #--split client_age_lst on 'Age:' to extract age number and convert to int

        #match = re.search('\d{2}/\d{2}/\d{4}', spouse_age_lst[0]) #--use regex to extract birthdate from birth info string, then convert to datetime to extract birth year
        match = re.search('/\d{4}', spouse_age_lst[0]) #--use regex to extract birthdate from birth info string, then convert to datetime to extract birth year

        spouse_birthyr = match.group() #TY20
        spouse_birthyr = int(re.sub('/', '', spouse_birthyr)) #TY20

        #spouse_birthyr = datetime.strptime(match.group(), '%m/%d/%Y').date()
        #spouse_birthyr = spouse_birthyr.year
    else:
        spouse = False
        spouse_age = 0
        spouse_birthyr = 0

    values['spouse'] = spouse
    values['spouse_age'] = spouse_age
    values['spouse_birthyr'] = spouse_birthyr
    values['client_birthyr'] = client_birthyr
    values['client_name'] = client_name
    values['client_age'] = client_age

    #print('Complete: Time and Client/spouse Information')

    # Get filing status (single, married filing joint, married filing seperate, head of househould)
    str1_status = 'FILING STATUS'
    str_name = utils.find_string_1bounds(str1_status, QS_sublist)
    str_name1 = re.sub('FILING STATUS', '', str_name)
    values['fed_filing_status'] = int(str_name1.strip()[0][0])

    # Check if they are paying Fed taxes electronically
    str1_status = 'ELECTRONIC PAYMENT'
    str_name = utils.find_string_1bounds(str1_status, QS_sublist)
    values['fed_direct_debit'] = bool(str_name)

    # Get the number of dependents and their ages
    str1_status = 'DEPENDENT NAME'
    str_name = utils.find_string_1bounds(str1_status, QS_sublist)
    if not bool(str_name):
        values['dependent_listed'] = False
        values['num_dependents'] = 0
        values['dep_under_17'] = 0
        values['dep_under_24'] = 0
        values['dep_under_6'] = 0
        values['dep_under_2'] = 0
    else:
        values['dependent_listed'] = True

    if values['dependent_listed']:
        dep_sub_upper = 'BIRTH DATE AGE        SSN       RELATIONSHIP   MONTHS'
        dep_sub_lower = 'LISTING OF FORMS FOR THIS RETURN'
        dependent_sublist = utils.sublist_1up_1low_ch_count(True, text_file, dep_sub_upper, dep_sub_lower, 0, 0)
        i = 0
        dep_age = []

        while i < len(dependent_sublist):
            str_dep = dependent_sublist[i]
            str_dep = str_dep.lstrip().rstrip()
            match = re.search('/\d{4}', str_dep)
            if bool(match):
                str_date = match.group()
                str_dep = str_dep.split(str_date)[1]
                str_dep = str_dep.lstrip().rstrip()
                match = re.search('\d{3}-\d{2}-\d{4}',str_dep)
                str_ssn = match.group()
                #str_ssn = str_dep.split(str_dep)[1]
                str_dep = str_dep.split(str_ssn)[0]
                str_dep = str_dep.lstrip().rstrip()
                str_dep = int(str_dep)
                dep_age.append(str_dep)
                i += 1
            else:
                i += 1

        #number of dependents
        values['num_dependents'] = len(dep_age)
        k = 17  #cut-off age for child tax credit
        values['dep_under_17'] = sum(i < k for i in dep_age)
        k = 24  #cut-off age of EITC dependent if full-time student
        values['dep_under_24'] = sum(i < k for i in dep_age)
        k = 2  #cut-off age of EITC dependent if full-time student
        values['dep_under_2'] = sum(i < k for i in dep_age)
        k = 5  #cut-off age of EITC dependent if full-time student
        values['dep_under_6'] = sum(i < k for i in dep_age)

    # If client recieved social security, get the amount they paid (total) for Medicare included on their SSA1099 statement
    if ssa_income_exists:
        str_name1 = 'TOTALS......'
        str_name = utils.find_string_1bounds(str_name1, ssa_sublist)
        str_name = str_name.lstrip().rstrip()
        values['medicare_payment'] = int(str_name[str_name.rindex(' ')+1:]) #get all characters after the last space in the string
    else:
        values['medicare_payment'] = 0

    return values


def parse_federal_1040_forms(fed1040_exists, fed1040_sublist, fed1040sr_sublist):

    values = dict()

    #======== 1 W-2 Wages==========
    str1 = '1'
    str2 = 'Wages'
    str3 = 'Attach Form(s)'
    if fed1040_exists:
        string = utils.find_string_3bounds(str1, str2, str3, fed1040_sublist)
        no_space_str = string.replace(" ", "")
        if '................' in no_space_str:  # look to see if other or scholarship income is printed over the "...."
            string = re.split(str2,string)[1]
            values['other_income'] = False
        else:
            next_index = fed1040_sublist.index(string) + 1
            string = fed1040_sublist[next_index]
            if 'SCH' in fed1040_sublist[next_index-1]:
                values['other_income'] = 'SCH'
            else:
                values['other_income'] = 'unknown'
    else:
        string = utils.find_string_3bounds(str1, str2, str3, fed1040sr_sublist)
        no_space_str = string.replace(" ", "")
        if '...........' in no_space_str:  # look to see if other or scholarship income is printed over the "...."
            string = re.split(str2,string)[1]
            values['other_income'] = False
        else:
            next_index = fed1040sr_sublist.index(string) + 1
            string = fed1040sr_sublist[next_index]
            if 'SCH' in fed1040sr_sublist[next_index-1]:
                values['other_income'] = 'SCH'
            else:
                values['other_income'] = 'unknown'

    values['Fed1040_1'] = utils.extract_form_field_value(str1, string)

    #======== 6a Social Security Income=======
    str1 = '6a'
    str2 = 'Social security benefits'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split('Taxable',string)[0]
    string = re.split(str2,string)[1]
    string = string.replace('b','')
    values['Fed1040_6a'] = utils.extract_form_field_value(str1, string)

    #======== 2b Taxable Interest ========
    str1 = '2b'
    str2 = 'Tax-exempt interest'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_2b'] = utils.extract_form_field_value(str1, string)

    #======== 4a IRA total=======
    str1 = '4a'
    str2 = 'IRA distributions'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split('Taxable',string)[0]
    string = re.split(str2,string)[1]
    string = string.replace('b','')
    values['Fed1040_4a'] = utils.extract_form_field_value(str1, string)

    #======== 4b Taxable IRA income ========
    str1 = '4b'
    str2 = 'Taxable amount'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_4b'] = utils.extract_form_field_value(str1, string)

    #======== 5a IRA total=======
    str1 = '5a'
    str2 = 'Pensions and annuities'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split('Taxable',string)[0]
    string = re.split(str2,string)[1]
    string = string.replace('b','')
    values['Fed1040_5a'] = utils.extract_form_field_value(str1, string)

    #======== 5b Taxable pension income ========
    str1 = '5b'
    str2 = 'Taxable amount'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_5b'] = utils.extract_form_field_value(str1, string)

    #======== 8 Other Income ========
    str1 = '8'
    str2 = 'income from Schedule 1, line 9'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_8'] = utils.extract_form_field_value(str1, string)

    #======== 9 Total Income ========
    str1 = '9'
    str2 = 'This is your total income'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_9'] = utils.extract_form_field_value(str1, string)

    #======== 11 AGI ========
    str1 = '11'
    str2 = 'This is your adjusted gross income'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_11'] = utils.extract_form_field_value(str1, string)

    #======== 19 Non-refundable CTC ========
    str1 = '19'
    str2 = 'tax credit or credit for other dependents'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_19'] = utils.extract_form_field_value(str1, string)

    #======== 27 EIC ========
    str1 = '27'
    str2 = 'Earned income credit'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_27'] = utils.extract_form_field_value(str1, string)

    #======== 28 Additional child tax credit ========
    str1 = '28'
    str2 = 'child tax credit. Attach Schedule 8812'
    if fed1040_exists:
        string = utils.find_string_2bounds(str1, str2, fed1040_sublist)
    else:
        string = utils.find_string_2bounds(str1, str2, fed1040sr_sublist)
    string = re.split(str2,string)[1]
    values['Fed1040_28'] = utils.extract_form_field_value(str1, string)

    #======= Claimed as a dependent ===========
    str1 = 'Someone can claim: X You as a dependent'
    if fed1040_exists:
        values['Fed1040_dependent'] = utils.check_form_exist_1bound(str1, fed1040_sublist)
    else:
        values['Fed1040_dependent'] = False


    return values


def parse_child_tax_worksheet(worksheet_exists, ctc_sublist):

    values = dict()

    if worksheet_exists:

        #======== String for # dependents included in child tax credit ========
        str_1 = '$2,000'
        str_2 = 'Enter the result'
        string = utils.find_string_2bounds(str_1, str_2, ctc_sublist)
        string = string.split('$2,000')[0]
        try:
            values['num_dep_ctc'] = int(string)
        except:
            values['num_dep_ctc'] = 0

        #======== String for # dependents included in credit for other dependents ========
        str_1 = '$500'
        str_2 = 'required social security number:'
        string = utils.find_string_2bounds(str_1, str_2, ctc_sublist)
        string = string.split('$500')[0]
        string = string.split(str_2)[1]
        try:
            values['num_credit_other_dep'] = int(string)
        except:
            values['num_credit_other_dep'] = 0
    else:
        values['num_dep_ctc'] = 0
        values['num_credit_other_dep'] = 0

    return values


def parse_schedule_eic(schedule_eic_exists, eic_sublist):

    values = dict()

    if schedule_eic_exists:
        #======== find the # of dependents included on the EIC form ========
        str1_status = 'showing a live birth'
        str_name = utils.find_string_1bounds(str1_status, eic_sublist)
        dep_ssn = re.findall('\d{3}-\d{2}-\d{4}', str_name)
        values['num_eic_dep'] = len(dep_ssn)
        try:
            values['num_eic_dep'] = len(dep_ssn)
        except:
            values['num_eic_dep'] = 0
    else:
        values['num_eic_dep'] = 0

    return values


def parse_eic_worksheet(schedule_eic_exists, schedule_eic_nodep_exists,
                        eic_worksheet_sublist):

    values = dict()

    if schedule_eic_exists or schedule_eic_nodep_exists:

        str1_text = 'PY Earned Income'
        values['EIC_PY_earned_income_used'] = utils.check_form_exist_1bound(str1_text, eic_worksheet_sublist)
        # EIC Worksheet B line 7
        str1 = '7'
        str2 = 'Be sure you use the correct column for your filing status'
        string =  utils.find_string_2bounds(str1, str2, eic_worksheet_sublist)
        string = re.split(str2,string)[1]
        values['EIC_WorksheetB_7'] = utils.extract_form_field_value(str1, string)

        # EIC Worksheet B line 10
        str1 = '10'
        str2 = 'status and the number of children you have. Enter the credit'
        string =  utils.find_string_2bounds(str1, str2, eic_worksheet_sublist)
        string = re.split(str2,string)[1]
        values['EIC_WorksheetB_10'] = utils.extract_form_field_value(str1, string)

        # EIC Worksheet B line 6
        str1 = '6'
        str2 = 'Enter your total earned income from Part 4, line 4b'
        string =  utils.find_string_2bounds(str1, str2, eic_worksheet_sublist)
        string = re.split(str2,string)[1]
        values['EIC_WorksheetB_6'] = utils.extract_form_field_value(str1, string)

    else:

        values['EIC_PY_earned_income_used'] = False
        values['EIC_WorksheetB_6'] = 0
        values['EIC_WorksheetB_7'] = 0
        values['EIC_WorksheetB_10'] = 0

    return values


def parse_fed_schedule_1(fed_schedule_1_exists, text_file):

    values = dict()

    if fed_schedule_1_exists:

        # Self employment income
        str1 = '3'
        str2 = 'Attach Schedule C'
        str3 = 'Business income or'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSch1_3'] = utils.extract_form_field_value(str1, string)

        # Unemployment income
        str1 = '7'
        str2 = 'compensation'
        str3 = 'Unemployment'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSch1_7'] = utils.extract_form_field_value(str1, string)

        # HSA personal contribution
        str1 = '12'
        str2 = 'Attach Form 8889'
        str3 = 'Health savings account deduction'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSch1_12'] = utils.extract_form_field_value(str1, string)

        # Deductable portion of self-employment tax
        str1 = '14'
        str2 = 'Attach Schedule SE'
        str3 = 'Deductible part of self'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSch1_14'] = utils.extract_form_field_value(str1, string)

        #other income
        str1 = '8'
        str2 = 'Other income. List type and amount'
        string =  utils.find_string_2bounds(str1, str2, text_file)
        next_index = text_file.index(string) + 1
        string = text_file[next_index]
        #string = re.split(str2,string)[1]
        values['FedSch1_8'] = utils.extract_form_field_value(str1, string)

    else:
        values['FedSch1_3'] = 0
        values['FedSch1_12'] = 0
        values['FedSch1_14'] = 0
        values['FedSch1_8'] = 0
        values['FedSch1_7'] = 0

    return values


def parse_fed_schedule_2(fed_schedule_2_exists, text_file):

    values = dict()

    if fed_schedule_2_exists:

        # Retirement account early withdrawl penalty
        str1 = '2'
        str2 = 'Attach Form 8962'
        str3 = 'Excess advance premium tax credit repayment'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSch2_2'] = utils.extract_form_field_value(str1, string)

        # Self-employment tax
        str1 = '4'
        str2 = 'Attach Schedule SE'
        str3 = 'tax'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSch2_4'] = utils.extract_form_field_value(str1, string)

        # Retirement account early withdrawl penalty
        str1 = '6'
        str2 = 'Attach Form 5329 if required'
        str3 = 'accounts'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSch2_6'] = utils.extract_form_field_value(str1, string)

    else:
        values['FedSch2_2'] = 0
        values['FedSch2_6'] = 0
        values['FedSch2_4'] = 0

    return values


def parse_fed_form_8889(fed_form_8889_exists, text_file):
    """
    Federal Form 8889 HSA Variables
    """

    values = dict()

    if fed_form_8889_exists:

        # HSA distribution penalty
        str1 = '17b'
        str2 = 'check box c and enter'
        str3 = '“HSA”'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedForm8889_17b'] = utils.extract_form_field_value(str1, string)

    else:
        values['FedForm8889_17b'] = 0

    return values


def parse_fed_schedule_c(fed_schedule_c_exists, text_file):

    values = dict()

    if fed_schedule_c_exists:

        # gross income
        str1 = '7'
        str2 = 'Gross income'
        str3 = 'Add lines 5 and 6'
        string =  utils.find_string_3bounds(str1, str2, str3, text_file)
        string = re.split(str2,string)[1]
        values['FedSchC_7'] = utils.extract_form_field_value(str1, string)
    else:
        values['FedSchC_7'] = 0

    return values


def parse_mi1040_values(mi1040_exists, mi1040_sublist, num_dependents, spouse):
    """
    Michigan 1040 form
    """

    values = dict()

    if mi1040_exists:

        #======== 7a, 8a Filing and Residency Status========
        str_7a = 'Single'
        str_8a = 'If you check box “c,” complete'

        str7a8a = utils.find_string_2bounds(str_7a, str_8a, mi1040_sublist)
        remove1 = '* If you check box “c,” complete'
        str7a8a = str7a8a.replace(remove1, "") #--remove unnecessary words from string
        #--remove whitespace and split on a. to separate elements
        str7a8a_lst = str7a8a.lstrip().rstrip().split('a. ')
        #--Filing Status Single: If val == 1, no X in 7a, if value == 2, there's an X in 7a
        mi1040_7a_num = len(str7a8a_lst[1].lstrip().rstrip().split())
        #--Residency Status Resident: If val == 1, no X in 8a, if value == 2, there's an X in 8a
        mi1040_8a_num = len(str7a8a_lst[2].lstrip().rstrip().split())

        #--Convert to boolean values--
        values['mi1040_7a'] = utils.bool_conv(mi1040_7a_num)
        values['mi1040_8a'] = utils.bool_conv(mi1040_8a_num)

        #======== 7b, 8b Filing and Residency Status========
        str7b = 'Nonresident'
        str7b_2 = 'below:'
        str8b = '“c,” you must complete'
        remove1 = '*'

        count = -1
        for elem in mi1040_sublist:
            count += 1
            if str7b and str7b_2 and str8b in elem:
                #--Information for whether 7b has a checkmark is in the string after the one with the 7b garbled text, or count + 1
                str7b_only = count + 1
                str8b_only = elem

        #---7b.---: The X for the values['mi1040_7b'] box is not in the same string as the text, but in the string after it--
        if 'X' in mi1040_sublist[str7b_only]: #--Determine if there is an 'X' in the string at the index str7b_only
            mi1040_7b_num = 2 #--Length of 7a is 2 if there is an X present in the box, so keeping consistent for coding the Rules
        else:
            mi1040_7b_num = 1 #--Length of 7a is 1 if there is no X present in the box

        #---8b.---
        str8b_only = str8b_only.replace(str8b, "").replace(remove1, "") #--remove unnecessary words from Nonresident part of string
        str8b_lst = str8b_only.lstrip().rstrip().split('b. ')  #--remove whitespace and split on b. to separate elements
        mi1040_8b_num = len(str8b_lst[2].lstrip().rstrip().split())

        values['mi1040_7b'] = utils.bool_conv(mi1040_7b_num)
        values['mi1040_8b'] = utils.bool_conv(mi1040_8b_num)

        #======== 7c, 8c Filing and Residency Status========
        str_7c_8c = 'Part-Year Resident *'
        remove1 = 'Resident'
        remove2 = ' *'

        str7c8c = utils.find_string_1bounds(str_7c_8c, mi1040_sublist)
        str7c8c = str7c8c.replace(remove1, "").replace(remove2, "") #--remove unnecessary words from string
        #str7c8c = str7c8c.replace(remove1, "").replace(remove2, "") #--remove unnecessary words from string
        str7c8c_lst = str7c8c.lstrip().rstrip().split('c. ')  #--remove whitespace and split on c. to separate elements
        mi1040_7c_num = len(str7c8c_lst[1].lstrip().rstrip().split()) #--Filing Status (Married Filing Separately): If value == 1, there is no X in 7c, if value == 2, there is an X in 7c
        if mi1040_7c_num == 0:
            mi1040_7c_num = 1
        elif mi1040_7c_num == 1:
            # TODO: Is this a typo?
            mi_1040_7c_num = 2

        #--Residency Status (Part-Year Resident): If value == 1, there is no X in 8c, if value == 2, there is an X in 8c
        mi1040_8c_num = len(str7c8c_lst[2].lstrip().rstrip().split())
        values['mi1040_7c'] = utils.bool_conv(mi1040_7c_num) #--Convert to boolean values--
        values['mi1040_8c'] = utils.bool_conv(mi1040_8c_num) #--Convert to boolean values--

        #======== 9b Disability Exemption + 9c Disabled Veterans ========
        str1  = '9b'
        str2  = 'blind, hemiplegic, paraplegic, quadriplegic, or totally and permanently disabled'
        string = utils.find_string_2bounds(str1, str2, mi1040_sublist)
        next_index = mi1040_sublist.index(string) + 1  # used to find the index for line 9c needed below
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040_9b'] = utils.extract_form_field_value(str1, string)

        str1 = '9c'
        string = mi1040_sublist[next_index]  #9c is garbled text in the PDF import.  Uses the line 9b to find line 9c.
        string = string.replace('.','')
        values['mi1040_9c'] = utils.extract_form_field_value(str1, string)

        #======== 12 Total Income ========
        str1  = '12'
        str2  = 'Total. Add lines 10 and 11'
        string = utils.find_string_2bounds(str1, str2, mi1040_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040_12'] = utils.extract_form_field_value(str1, string)

        #====== 25 Property Tax Credit ==========
        str1 = '25'
        str2 = 'Property Tax Credit'
        string = utils.find_string_2bounds(str1, str2, mi1040_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040_25'] = utils.extract_form_field_value(str1, string)

        #TEST W/O PTC to see what happens with the "00"

        #======= Michigan Exemptions ========

        # uses the number of dependents (values['num_dependents']) shown on the TaxSlayer summary sheet.  This helps to include dependents
        #that may not be included on the Fed/MI returns but are allowed on the HHC (added manually)

        values['MI_exemptions'] = 1 + values['mi1040_9b'] + values['mi1040_9c'] + num_dependents
        if spouse:
            values['MI_exemptions'] = values['MI_exemptions'] + 1
        else:
            pass

    else:
        values['mi1040_7a'] = False
        values['mi1040_7b'] = False
        values['mi1040_7c'] = False
        values['mi1040_8a'] = False
        values['mi1040_8b'] = False
        values['mi1040_8c'] = False
        values['mi1040_9b'] = 0
        values['mi1040_9c'] = 0
        values['mi1040_12'] = 0
        values['mi1040_25'] = 0
        values['MI_exemptions'] = 0

    return values


def parse_mi1040cr7_values(mi1040cr7_values, text_file):

    values = dict()

    if mi1040cr7_values:

        #======= 35 Medical Premiums Paid =============
        str1 = '35'
        str2 = 'Medical insurance or HMO premiums paid'
        string =  utils.find_string_2bounds(str1, str2, text_file)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040cr7_35'] = utils.extract_form_field_value(str1, string)
    else:
        values['mi1040cr7_35'] = 0

    return values


def parse_mi1040cr_values(mi1040cr_exists, mi1040cr_sublist):

    values = dict()

    if mi1040cr_exists:

        #======== 10 Property Taxes Paid ========
        str1 = '10'
        str2 = 'or amount from line 51, 56 and/or 57'
        string =  utils.find_string_2bounds(str1, str2, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_10'] = utils.extract_form_field_value(str1, string)

        #======== 21 Social Security + SSI Benefits ========
        str1 = '21'
        str2 = 'SUB pay, etc'
        string =  utils.find_string_2bounds(str1, str2, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_21'] = utils.extract_form_field_value(str1, string)

        #======== 31 Medical Premiums Paid ========
        str1 = '31'
        str2 = 'see instructions'
        string =  utils.find_string_2bounds(str1, str2, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_31'] = utils.extract_form_field_value(str1, string)

        #======== 33 Total Household Resources ========
        str1 = '33'
        str2  = 'you are not eligible for this credit'
        str3 = 'If more than $60,000'
        string =  utils.find_string_3bounds(str1, str2, str3, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_33'] = utils.extract_form_field_value(str1, string)

        #======== 51 Prorated property taxes paid ========
        str1 = '51'
        str2 = 'Enter here and on line 10'
        string =  utils.find_string_2bounds(str1, str2, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_51'] = utils.extract_form_field_value(str1, string)

        #======== 53 Rent Paid Market Value Housing ========
        str1 = '53'
        str2 = 'Add total rent for each period'
        string =  utils.find_string_2bounds(str1, str2, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_53'] = utils.extract_form_field_value(str1, string)

        #======== 54a, 54b Subsidized or Service Fee Housing Type ========
        mi1040CR_54stra = 'a.   X    Subsidized Housing: complete line 55'
        mi1040CR_54strb = 'b.     X     Service Fee Housing: complete lines 55 and 56.'
        values['mi1040CR_54a'] = utils.check_form_exist_1bound(mi1040CR_54stra, mi1040cr_sublist)
        values['mi1040CR_54b'] = utils.check_form_exist_1bound(mi1040CR_54strb, mi1040cr_sublist)

        #======== 55 Rent Paid Subsidized or Service Fee Housing ========
        str1 = '55'
        str2 = 'paid on your behalf by a government agency'
        string =  utils.find_string_2bounds(str1, str2, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_55'] = utils.extract_form_field_value(str1, string)

        #======== 57 Prorated Property Taxes Paid Special Housing ========
        str1 = '57'
        str2 = 'facility checked'
        string =  utils.find_string_2bounds(str1, str2, mi1040cr_sublist)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['mi1040CR_57'] = utils.extract_form_field_value(str1, string)
    else:
        values['mi1040CR_10'] = 0
        values['mi1040CR_21'] = 0
        values['mi1040CR_31'] = 0
        values['mi1040CR_33'] = 0
        values['mi1040CR_51'] = 0
        values['mi1040CR_53'] = 0
        values['mi1040CR_54a'] = 0
        values['mi1040CR_54b'] = 0
        values['mi1040CR_55'] = 0
        values['mi1040CR_57'] = 0

    return values


def parse_misched1_values(misched1_subtractions_exists, text_file):

    values = dict()

    if misched1_subtractions_exists:

        #==== 25 Retirement Benefit Subtraction =======
        str1 = '25'
        str2 = 'Include Form 4884'
        string =  utils.find_string_2bounds(str1, str2, text_file)
        string = re.split(str2,string)[1]
        string = string.replace('.','')
        values['miSched1_25'] = utils.extract_form_field_value(str1, string)

    else:
        values['miSched1_25'] = 0

    return values


def parse_mi_sched_nr_values(miSchedNR_exists, miSchedNR_sublist, spouse, final_message):

    values = dict()

    #=====================================================================
    #---------MI Schedule NR: Loop 1---------
    #--Checks if Nonresident or Part-Year Resident checked
    #--Extracts strings with dates; Removes excess text and 2020 from strings
    #--Sets variables to 0's if no dates in boxes or Schedule NR doesn't exist
    #=====================================================================

    from_str1 = 'FROM: '
    #to_str1 = 'Enter dates of Michigan residency in 2019*'
    to_str1 = 'Enter dates of Michigan residency in 2020*'  #TY20
    non_res_str = 'X     Nonresident'
    partyr_res_str = 'b.    X     Part-Year Resident of Michigan'

    if miSchedNR_exists:

        #--Check if individual was non_resident or part_yr_resident--
        non_resident = utils.check_form_exist_1bound(non_res_str, miSchedNR_sublist) #--returns string
        part_yr_resident = utils.check_form_exist_1bound(partyr_res_str, miSchedNR_sublist)

        #--Extract FROM: and TO: Residency Date strings--
        from_text = utils.find_string_1bounds(from_str1, miSchedNR_sublist) #--From Dates
        to_text = utils.find_string_1bounds(to_str1, miSchedNR_sublist) #--To Dates

        #--Check for dates--
        from_match = re.search('\d{2}-\d{2}-', from_text) #--returns <class 're.Match'>
        to_match = re.search('\d{2}-\d{2}-', to_text)

        #--if the match exists, there's a date in the string
        if from_match != None:
            #--remove 2019 from from_text and to_text--
            #remove_yr = '2019'
            remove_yr = '2020' #TY20
            from_str_no_yr = from_text.replace(remove_yr,"")
            to_str_no_yr = to_text.replace(to_str1, "").replace(remove_yr, "") #--removes excess text and year
#             print('Yes, dates in residency status boxes')
            #--YES dates in Schedule NR, proceed to next loop and parse dates
        else:
            #--NO dates in Schedule NR, set values to 0's
#             print('No dates in Schedule NR')
            from_str_no_yr = 'False'
            to_str_no_yr = 'False'
            values['miSchNR_c1'] = 0
            values['miSchNR_c2'] = 0
            values['miSchNR_s1'] = 0
            values['miSchNR_s2'] = 0
            values['month_residence_client'] = 0
            values['month_residence_spouse'] = 0

    else:
        non_resident = False
        part_yr_resident = False
        from_str_no_yr = 'False'
        to_str_no_yr = 'False'
        from_text = False
        to_text = False
        values['miSchNR_c1'] = 0
        values['miSchNR_c2'] = 0
        values['miSchNR_s1'] = 0
        values['miSchNR_s2'] = 0
        values['month_residence_client'] = 0
        values['month_residence_spouse'] = 0


    #==============================================
    #---------MI Schedule NR: Loop 2---------
    #--Checks 2 main conditions, whether part-yr resident or nonresident
    #--If part-yr resident, then extracts variables for client
    #--If part-yr resident and spouse exists, grabs spouse variables
    #==============================================

    if miSchedNR_exists and part_yr_resident:
        if len(from_str_no_yr.split()) == 1: #--only 'FROM:' is in the list
            #--set values to 0's
            values['miSchNR_c1'] = 0
            values['miSchNR_c2'] = 0
            values['miSchNR_s1'] = 0
            values['miSchNR_s2'] = 0
            values['month_residence_client'] = 0
            values['month_residence_spouse'] = 0

        elif len(from_str_no_yr.split()) > 1: #--dates are in list as well as 'FROM:'
            #--get client FROM: variables
            from_dates_lst = from_str_no_yr.replace('FROM:', "").split()  #--remove FROM:, then create date list
            #miSchNR_c1 = from_dates_lst[0] + '2019'
            values['miSchNR_c1'] = from_dates_lst[0] + '2020' #TY20
            client_from_dt = datetime.strptime(values['miSchNR_c1'], '%m-%d-%Y').date() #--create datetime object from date string

            #--get client variables TO: variables
            to_dates_lst = to_str_no_yr.replace('TO:', "").split()  #--remove TO:, then create date list
            #miSchNR_c2 = to_dates_lst[0] + '2019'
            values['miSchNR_c2'] = to_dates_lst[0] + '2020' #TY20

            #--create datetime object from date string
            client_to_dt = datetime.strptime(values['miSchNR_c2'], '%m-%d-%Y').date()

            #--get client # months in residence in MI--
            r = relativedelta.relativedelta(client_to_dt, client_from_dt)

            #--number of months client has lived in Michigan
            values['month_residence_client'] = r.months

            if spouse:
                #--if dates exist: return values for spouse dates
                #miSchNR_s1 = from_dates_lst[1] + '2019'
                values['miSchNR_s1'] = from_dates_lst[1] + '2020' #TY20

                #--create datetime object from date string
                spouse_from_dt = datetime.strptime(values['miSchNR_s1'], '%m-%d-%Y').date()

                #miSchNR_s2 = to_dates_lst[1] + '2019'
                values['miSchNR_s2'] = to_dates_lst[1] + '2020' #TY20

                #--create datetime object from date string
                spouse_to_dt = datetime.strptime(values['miSchNR_s2'], '%m-%d-%Y').date()

                #--get spouse # months in residence in MI--
                r = relativedelta.relativedelta(spouse_to_dt, spouse_from_dt)

                #--number of months client has lived in Michigan
                values['month_residence_spouse'] = r.months

            else:
                #--if no spouse, return 0's for spouse values
                values['miSchNR_s1'] = 0
                values['miSchNR_s2'] = 0
                values['month_residence_spouse'] = 0
        else:
            print("WARNING: Did you mean to check Part-Year Resident, no date values available for Schedule NR. Please check form.")

    elif miSchedNR_exists and not part_yr_resident:

        if len(from_str_no_yr.split()) == 1:
            #--set values to 0's
            values['miSchNR_c1'] = 0
            values['miSchNR_c2'] = 0
            values['miSchNR_s1'] = 0
            values['miSchNR_s2'] = 0
            values['month_residence_client'] = 0
            values['month_residence_spouse'] = 0

        elif len(from_str_no_yr.split()) > 1: #--dates are in list as well as 'FROM:'
            m = "WARNING: Did you mean to check Nonesident, date are values available for Schedule NR. Please check form. \n"
            final_message = final_message + m
        #--check for date values for client
        #--if date values exist: print("Did you mean to check Nonresident, date values are available for Schedule NR")
        #--else: if date values don't exist: set all values to 0's
        else:
            m = 'WARNING: No dates in Schedule NR, check form' #--Redo this part
            final_message = final_message + m

    else:
        pass #--Placeholder for now--


    return values, final_message
