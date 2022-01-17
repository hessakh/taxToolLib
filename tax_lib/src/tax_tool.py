"""
Main code for tax tool.

Replaces what used to be in `batching_unitedwaytaxtool_2020_V2.2`

"""

import pandas as pd

# Import tax tool modules
from . import utils, rules, parsers

def process_one_form(file):
    # Run the tax tool on an uploaded file
    #
    # Inputs:
    #   file: a file object
    #
    # Returns the final output as a string

    # Check if the passed in `file` is a path or an actual file object.
    if isinstance(file, str):
        file_name = file
        text_file = utils.pdftotext(file)
    else:
        file_name = file.name
        text_file = utils.pdftotext(file.read())

    final_message = '' #--print out for volunteers

    col_lst = utils.define_column_list()

    #---Quick Summary---
    # Used to check for federal forms
    QS_sub_upper = 'TAX YEAR: 2020'
    QS_sub_lower = 'AMOUNT DUE'
    QS_sublist = utils.sublist_1up_1low_ch_count(True, text_file, QS_sub_upper, QS_sub_lower, 0, 0)

    #=====================================
    #--Check if forms exist in Tax File--
    #=====================================
    exists = utils.build_exists_dictionary(text_file, QS_sublist)

    #=====================================
    #-----Create Sublists for Forms------
    #=====================================
    sublist = utils.build_sublist_dictionary(text_file, exists)

    #=====================================
    #------ Date/Time Tool was Run -------
    #=====================================
    timestamp_str, run_code_datetime = utils.get_time_info(sublist['age'])

    #================================
    #---- Variables
    #================================
    values = dict()

    #=====================================
    #-----Client Summary Sheet ---------
    #=====================================

    client_summary_values = parsers.parse_client_summary_sheet(
                                        sublist['age'],
                                        QS_sublist,
                                        text_file,
                                        exists['SSA_income'],
                                        ssa_sublist=sublist['SSA']
                                        )

    values.update(client_summary_values)

    #=====================================
    #-----Federal 1040 & 1040-SR ---------
    #=====================================

    federal_1040_values = parsers.parse_federal_1040_forms(exists['Fed1040'],
                                                           sublist['Fed1040'],
                                                           sublist['Fed1040SR'])
    values.update(federal_1040_values)

    #===============================
    #---------Child Tax Credit and Credit for Other Dependents----------------
    #================================
    ctc_values = parsers.parse_child_tax_worksheet(exists['child_tax_worksheet'],
                                                   sublist['CTC'])

    values.update(ctc_values)

    #===============================
    #---------Schedule EIC----------
    #===============================
    schedule_eic_values = parsers.parse_schedule_eic(exists['ScheduleEIC'],
                                                     sublist['EIC'])

    values.update(schedule_eic_values)

    #===============================
    #---------EIC Worksheet-------
    #===============================

    eic_worksheet_values = parsers.parse_eic_worksheet(exists['ScheduleEIC'],
                                                       exists['ScheduleEICnoDep'],
                                                       sublist['EIC_Worksheet'])

    values.update(eic_worksheet_values)

    #===============================
    #---------Schedule 1 ----------
    #===============================

    fed_schedule_1_values = parsers.parse_fed_schedule_1(exists['fedSchedule1'],
                                                         text_file)

    values.update(fed_schedule_1_values)

    #===============================
    #---------Schedule 2 ----------
    #===============================

    fed_schedule_2_values = parsers.parse_fed_schedule_2(exists['fedSchedule1'],
                                                         text_file)

    values.update(fed_schedule_2_values)

    #===============================
    #---------Form 8889 HSA---------
    #===============================

    fed_form_8889_values = parsers.parse_fed_form_8889(exists['fedForm8889'],
                                                       text_file)

    values.update(fed_form_8889_values)

    #===============================
    #---------Form Schedule C-------
    #===============================

    fed_schedule_c_values = parsers.parse_fed_schedule_c(exists['fedScheduleC'],
                                                         text_file)

    values.update(fed_schedule_c_values)

    #================================
    #---------MI-1040----------------
    #================================

    mi1040_values = parsers.parse_mi1040_values(exists['mi1040'],
                                                sublist['mi1040'],
                                                values['num_dependents'],
                                                values['spouse'])

    values.update(mi1040_values)

    #================================
    #---------MI-1040CR-7------------
    #================================

    mi1040cr7 = parsers.parse_mi1040cr7_values(exists['mi1040cr7'],
                                               text_file)


    values.update(mi1040cr7)

    #================================
    #---------MI-1040CR-------------
    #================================

    mi1040cr_values = parsers.parse_mi1040cr_values(exists['mi1040CR'], sublist['mi1040CR'])

    values.update(mi1040cr_values)

    #================================
    #---------MI Schedule 1----------
    #================================

    misched1_values = parsers.parse_misched1_values(exists['miSched1_subtractions'],
                                                    text_file)


    values.update(misched1_values)

    #=====================================================================
    #---------MI Schedule NR
    #=====================================================================

    miSchedNr_values, final_message = parsers.parse_mi_sched_nr_values(exists['miSchedNR'],
                                                                       sublist['miSchedNR'], values['spouse'],
                                                                       final_message)

    values.update(miSchedNr_values)



    #==============================================
    #
    #----- RULES
    #
    #==============================================

    rule1_df, final_message = rules.rule_1(final_message, exists, values)
    rule2_df, final_message = rules.rule_2(final_message, exists, values)
    rule4_df, final_message = rules.rule_4(final_message, exists, values)
    rule5_df, final_message = rules.rule_5(final_message, exists, values)
    rule10_df, final_message = rules.rule_10(final_message, exists, values)
    rule11_df, final_message = rules.rule_11(final_message, exists, values)
    rule12_df, final_message = rules.rule_12(final_message, exists, values)
    rule13_df, final_message = rules.rule_13(final_message, exists, values)
    rule14_df, final_message = rules.rule_14(final_message, exists, values)
    rule15_df, final_message = rules.rule_15(final_message, exists, values)
    rule16_df, final_message = rules.rule_16(final_message, exists, values)
    rule18a_df, final_message = rules.rule_18a(final_message, exists, values)
    rule18b_df, final_message, EITC_limit = rules.rule_18b(final_message, exists, values)
    rule18c_df, final_message = rules.rule_18c(final_message, exists, values)
    rule18d_df, final_message = rules.rule_18d(final_message, exists, values)
    rule19_df, final_message = rules.rule_19(final_message, exists, values)
    rule21_df, final_message = rules.rule_21(final_message, exists, values)
    rule22_df, final_message, hhc_income_limit, hhc_eligable = rules.rule_22(final_message, exists, values)
    rule23_df, final_message = rules.rule_23(final_message, exists, values)
    rule24_df, final_message = rules.rule_24(final_message, exists, values)
    rule25_df, final_message = rules.rule_25(final_message, exists, values)
    rule26_df, final_message = rules.rule_26(final_message, exists, values)
    rule27_df, final_message = rules.rule_27(final_message, exists, values)
    rule28_df, final_message = rules.rule_28(final_message, exists, values)
    rule29_df, final_message = rules.rule_29(final_message, exists, values)
    rule30_df, final_message = rules.rule_30(final_message, exists, values)
    rule31_df, final_message = rules.rule_31(final_message, exists, values)
    rule32_df, final_message = rules.rule_32(final_message, exists, values)
    rule33_df, final_message = rules.rule_33(final_message, exists, values)
    rule34_df, final_message = rules.rule_34(final_message, exists, values)
    rule35_df, final_message = rules.rule_35(final_message, exists, values)
    rule36_df, final_message = rules.rule_36(final_message, exists, values)
    rule37_df, final_message = rules.rule_37(final_message, exists, values)


    #=================================================================
    #---Create Dateframe of Variables and Values--
    #=================================================================

    #--col_lst is in a cell above this one--
    var_lst = [file_name, run_code_datetime, timestamp_str, values['client_name'], values['client_age'], values['client_birthyr'], values['spouse'], values['spouse_age'], values['spouse_birthyr'], values['dependent_listed'], values['num_dependents'], values['dep_under_17'],
            values['dep_under_24'], values['dep_under_6'], values['dep_under_2'], values['fed_filing_status'], values['fed_direct_debit'], exists['SSA_income'], values['medicare_payment'], exists['Fed1040SR'], exists['Fed1040'],
            values['Fed1040_dependent'], values['Fed1040_1'], values['other_income'], values['Fed1040_2b'], values['Fed1040_4a'], values['Fed1040_4b'], values['Fed1040_5a'], values['Fed1040_5b'], values['Fed1040_6a'], values['Fed1040_8'], values['Fed1040_9'], values['Fed1040_11'],
            values['Fed1040_19'], values['Fed1040_27'], values['Fed1040_28'], exists['ScheduleEIC'], values['fed_earned_income'], values['num_eic_dep'],
            EITC_limit, values['EIC_PY_earned_income_used'], values['EIC_WorksheetB_6'], values['EIC_WorksheetB_7'], values['EIC_WorksheetB_10'], exists['child_tax_worksheet'], values['num_dep_ctc'], values['num_credit_other_dep'], exists['fedSchedule1'],
            values['FedSch1_3'], values['FedSch1_7'], values['FedSch1_12'], values['FedSch1_14'], exists['fedSchedule2'], values['FedSch2_4'], values['FedSch2_6'], exists['fedForm8889'], values['FedForm8889_17b'], exists['fedForm8879'], exists['MI_direct_payment'],
            exists['mi1040'], values['mi1040_7a'], values['mi1040_7b'], values['mi1040_7c'], values['mi1040_8a'], values['mi1040_8b'], values['mi1040_8c'], values['mi1040_9b'], values['mi1040_9c'], values['mi1040_12'], values['mi1040_25'], values['MI_exemptions'], values['mi_THR'],
            exists['miSched1_subtractions'], values['miSched1_25'], exists['miSchedNR'], values['miSchNR_c1'], values['miSchNR_c2'], values['miSchNR_s1'], values['miSchNR_s2'],
            values['month_residence_client'], values['month_residence_spouse'], exists['mi1040CR'], values['mi1040CR_10'], values['mi1040CR_21'], values['mi1040CR_31'], values['mi1040CR_33'],
            values['mi1040CR_51'], values['mi1040CR_53'], values['mi1040CR_54a'], values['mi1040CR_54b'], values['mi1040CR_55'], values['mi1040CR_57'],
            exists['mi1040cr7'], hhc_income_limit, hhc_eligable, values['mi1040cr7_35'],
            rule1_df, rule2_df, rule4_df, rule5_df, rule10_df, rule11_df, rule12_df, rule13_df, rule14_df, rule15_df, rule16_df, rule18a_df, rule18b_df, rule19_df,
            rule21_df, rule22_df, rule23_df, rule24_df, rule25_df, rule26_df, rule27_df, rule28_df, rule29_df, rule30_df, rule31_df]

    # Assemble a list of name-value pairs for debugging
    debug_list = []
    for value, varname in zip(var_lst, col_lst):
        debug_list.append(f'{varname}: {value}')

    results ='Automated Check Tool' + '\n'
    results = results + 'RESULTS FOR: ' + values['client_name'] + '\n' #+ "Today's Date: " + str(run_code_datetime) + '\n'
    results = results + 'Filename: ' + file_name + '\n' +  '====================================================== \n' + final_message

    if len(results.split()) < 17:
        results = results + 'There are no Errors or Warnings for this client tax file.'
    else:
        pass

    return (results, debug_list)


def run():
    """
    Main runner function.

    The general flow for each tax form is:
      1. Convert PDF to text file
      2. Convert text file into `sublists` (smaller chunks representing each form)
         TODO: make the building blocks more robust
      3. Check for existence of forms
      4. Parse values out of each form
      5. Apply rule-set
      6. Write results
    """

    tax_form_file_list = utils.get_tax_form_list()

    #--Create empty dataframe and empty string for all client data--
    col_lst = utils.define_column_list()
    all_tax_df = pd.DataFrame(columns=col_lst)

    #--empty strings for output .txt files--
    all_tax_txt_file = ''
    hand_check_txt_file = ''

    formcount = 0

    for file in tax_form_file_list:

        (string_output, tax_df) = process_one_form(file)

        all_tax_df = all_tax_df.append(tax_df)
        all_tax_txt_file = all_tax_txt_file + string_output + '\n\n\n\n'
        formcount += 1
        print('Form ' + str(formcount) + ' complete;  ', 'Filename: ' + file)

    #=================================================================
    #--EXPORT DATAFRAME to .csv and RULES TO .txt FILE--
    #=================================================================

    #--Create text file for all clients--
    file = 'src/tests/output/Client_output.txt'
    txt_file = open(file, 'w')
    n = txt_file.write(all_tax_txt_file)
    txt_file.close()

    #--Text file output of client names where the .pdf file did not work for
    # batching--
    file = 'src/tests/output/Completely_hand_check_these_files.txt'
    txt_file = open(file, 'w')
    n = txt_file.write(hand_check_txt_file)
    txt_file.close()

    #--Export Dataframe to.csv and .xls--
    file_name = 'src/tests/output/2020_client_tax_information.csv'
    all_tax_df.to_csv(file_name)
