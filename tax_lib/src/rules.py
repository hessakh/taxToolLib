"""
Collection of rules to check forms against
"""

no_error_string = 'OK'
error_string = 'Error'

#===========================================================
#--RULE 1:
# Check if the client is receiving Social Security and under
# the age of 66.  May be eligible for MI disability exemption.
#===========================================================
#--Leave if/else with spouse, or will not capture ages correctly--
def rule_1(final_message, exists, values):

    rule1_error_message = 'WARNING: Check if client is eligible for Michigan disability exemption'

    ss_income = max(values['Fed1040_6a'], values['mi1040CR_21'])

    if values['spouse']:
        rule1 = exists['mi1040'] and ss_income > 0 \
                                and (values['client_age'] < 66 \
                                  or values['spouse_age'] < 66)

        if rule1:
            if values['mi1040_9b'] == 0:
                rule1_df = rule1_error_message
                final_message = final_message + rule1_df + '\n'
            else:
                #--if values['mi1040_9b'] > 0 then there are no warnings
                rule1_df = no_error_string
        else:
            rule1_df = no_error_string + '1'

    else: #--If there is no spouse
        rule1 = exists['mi1040'] and values['Fed1040_6a'] > 0 \
                            and (values['client_age'] < 66)

        if rule1:
            if values['mi1040_9b'] == 0:
                rule1_df = rule1_error_message
                final_message = final_message + rule1_df + '\n'
            else:
                rule1_df = no_error_string
        else:
            rule1_df = no_error_string

    return rule1_df, final_message


#==========================================================
#--RULE 2:
# If client is 66 or older, MI does not allow a disability
# exemption to be claimed for TPD (only for specific cases listed)
#==========================================================
def rule_2(final_message, exists, values):

    rule2_error_message = 'WARNING: A person on the return is 66 or older and a MI disablility exeption is entered.  Check if one of the following are included on the return: 1) an eligable person younger than 66 or 2) a person older than 66 that is deaf, blind, hemiplegic, paraplegic, or quadriplegic.'

    rule2 = exists['mi1040'] and ((values['client_age'] >= 66 and values['spouse_age'] >= 66) \
                        or values['client_age'] >= 66) #--account for there being no sposue

    if rule2:
        if values['mi1040_9b'] > 0:
            rule2_df = rule2_error_message
            final_message = final_message + rule2_df + '\n'
        else:
            rule2_df = no_error_string
    else:
        rule2_df = no_error_string

    return rule2_df, final_message


#=============================================================
#--RULE 4:

# If the client is born before 1946 and has retirement income,
# this income can be subtracted from MI income.
# Check for required MI tax from is present.
#=============================================================
def rule_4(final_message, exists, values):

    hand_check_rule4_5 = 'WARNING - CHECK RULE BY HAND: Check if client was born before 1946 and if so, check if there is retirement income that can be subtracted from MI income.'
    rule4_error_message = "ERROR: Client born before 1946 and has retirement income that can be subtracted from MI income. Check that the MI subtractions from income for retirement income are entered correctly."

    if values['Fed1040_5b'] != error_string and values['Fed1040_4b'] != error_string:

        sum10404b4d = values['Fed1040_4b'] + values['Fed1040_5b']

        if values['spouse']:

            rule4 = exists['mi1040'] and (sum10404b4d > 0) \
                                and ((values['client_birthyr'] < 1946 \
                                   or values['spouse_birthyr'] < 1946))
            if rule4:
                if exists['miSched1_subtractions']:
                    rule4_df = no_error_string
                else:
                    rule4_df = rule4_error_message
                    final_message = final_message + rule4_df + '\n'
            else:
                rule4_df = no_error_string

        else: #--if there's no spouse--
            rule4 = exists['mi1040'] and (sum10404b4d > 0) \
                                and values['client_birthyr'] < 1946

            if rule4:
                if exists['miSched1_subtractions']:
                    rule4_df = no_error_string
                else:
                    rule4_df = rule4_error_message
                    final_message = final_message + rule4_df + '\n'
            else:
                rule4_df = no_error_string
    else:
        final_message = final_message + hand_check_rule4_5 + '\n'

    return rule4_df, final_message


#========================================================
#--RULE 5:
# Check that the correct amount of retirement income is
# subtracted if born before 1946 with retirement income.
#========================================================
def rule_5(final_message, exists, values):

    hand_check_rule4_5 = 'WARNING - CHECK RULE BY HAND: Check if client was born before 1946 and if so, check if there is retirement income that can be subtracted from MI income.'
    rule5_error_message = 'ERROR: Client born before 1946. Check that all MI retirement income subtractions are entered correctly.'

    sum10404b4d = values['Fed1040_4b'] + values['Fed1040_5b']

    if values['Fed1040_5b'] != error_string and values['Fed1040_4b'] != error_string:
        min_val_1 = min(values['Fed1040_4b'] + values['Fed1040_5b'], 52808)
        min_val_2 = min(values['Fed1040_4b'] + values['Fed1040_5b'], 105615)

        if values['spouse']:
            rule5 = exists['mi1040'] and exists['miSched1_subtractions'] \
                                and (sum10404b4d > 0) \
                                and (values['client_birthyr'] < 1946 or values['spouse_birthyr'] < 1946)

            if rule5:
                if values['mi1040_7a'] or values['mi1040_7c']:
                    if values['miSched1_25'] == min_val_1:
                        rule5_df = no_error_string
                    else:
                        rule5_df = rule5_error_message
                        final_message = final_message + rule5_error_message + '\n'

                elif values['mi1040_7b']:
                    if values['miSched1_25'] == min_val_2:
                        rule5_df = no_error_string
                    else:
                        rule5_df = rule5_error_message
                        final_message = final_message + rule5_error_message + '\n'

                else:
                    rule5_df = no_error_string
            else:
                rule5_df = no_error_string


        else: #--if there is no spouse
            rule5 = exists['mi1040'] and exists['miSched1_subtractions'] \
                                and sum10404b4d > 0 \
                                and values['client_birthyr'] < 1946

            if rule5:
                if values['mi1040_7a'] or values['mi1040_7c']:
                    if values['miSched1_25'] == min_val_1:
                        rule5_df = no_error_string
                    else:
                        rule5_df = rule5_error_message
                        final_message = final_message + rule5_error_message + '\n'

                elif values['mi1040_7b']:
                    if values['miSched1_25'] == min_val_2:
                        rule5_df = no_error_string
                    else:
                        rule5_df = rule5_error_message
                        final_message = final_message + rule5_error_message + '\n'
                else:
                    rule5_df = no_error_string
            else:
                rule5_df = no_error_string
    else:
        final_message = final_message + hand_check_rule4_5 + '\n'

    return rule5_df, final_message



#=========================================================
#--RULE 10:
# Check if the client if the client is eligible for the
# homestead property tax credit based on income and residency.
# If eligible based on these two criteria, check that the
# credit is entered.  Set warning to check if not.
#=========================================================
def rule_10(final_message, exists, values):

    rule10_error_message = "WARNING: Check if client is eligible for Homestead Property Tax Credit"

    if exists['mi1040']:
        if exists['mi1040CR']:
            values['mi_THR'] = values['mi1040CR_33']
        else:
            values['mi_THR'] = values['mi1040_12'] + values['Fed1040_6a'] - 300
    else:
        values['mi_THR'] = 0

    #--don't need # months residence here, 8a refers to resident
    rule10 = (values['mi1040_8a'] and exists['mi1040'] and values['mi_THR'] < 60000) or \
             (values['mi1040_8c'] and exists['mi1040'] and values['mi_THR'] < 60000 \
               and (values['month_residence_client'] >= 6 or values['month_residence_spouse'] >= 6))

    if rule10:
        if exists['mi1040CR']:
            rule10_df = no_error_string
        else:
            rule10_df = rule10_error_message
            final_message = final_message + rule10_df + '\n'
    else:
        rule10_df = no_error_string

    return rule10_df, final_message

#=================================================================
#--RULE 11a:
# If the client is not eligible for the homestead property tax credit
# based on residency qualification (less than 6 months or NR),
# ensure that it is not included in the tax return.
#=================================================================
def rule_11(final_message, exists, values):

    rule11_error_message = 'ERROR: Client was not a Michigan resident for at least 6 months and therefore is not eligible for the Homestead Property Tax Credit'

    #--IF TRUE--
    if values['spouse']:
        rule11 = exists['mi1040'] and values['mi1040_8c'] \
                                and values['mi1040_7b'] \
                                and values['month_residence_client'] <= 6 \
                                and values['month_residence_spouse'] <= 6
    else:
        rule11 = exists['mi1040'] and values['mi1040_8c'] \
                                and values['month_residence_client'] <= 6

    #--THEN CHECK--
    if rule11 and not exists['mi1040CR']:
        rule11_df = no_error_string
    elif rule11 and exists['mi1040CR']:
        rule11_df = rule11_error_message
        final_message = final_message + rule11_df + '\n'
    else:
        rule11_df = no_error_string

    return rule11_df, final_message

#=================================================================
#--RULE 12:
# If the client lives in service fee housing, check that subsidized
# housing is not also checked for homestead credit.
#=================================================================
def rule_12(final_message, exists, values):

    rule12_error_message = 'ERROR: If HPTC includes Service Fee Housing, do not select Subsidized Housing even if rent is subsidized.'

    if exists['mi1040CR'] and values['mi1040CR_54b']:
        rule12 = True
    elif exists['mi1040CR'] and not values['mi1040CR_54b']:
        #--this makes sure 54a and 54b aren't checked at the same time
        rule12 = False
    else:
        rule12 = False

    if rule12:
        if not values['mi1040CR_54a']:
            rule12_df = no_error_string
        else:
            rule12_df = rule12_error_message
            final_message = final_message + rule12_df + '\n'
    else:
        rule12_df = no_error_string

    return rule12_df, final_message


#=================================================================
#--RULE 13:
# Check if Total Household Resources are low compared to rent
#=================================================================
def rule_13(final_message, exists, values):

    rule13_error_message = 'Error: Check if there are additional Total Household Resources (THR) that need to be included or if the return should be paper filed with a letter explaining rent vs. THR.'
    temp = values['mi1040CR_33'] * 0.80
    mi1040CR53and55 = values['mi1040CR_53'] + values['mi1040CR_55']

    if exists['mi1040CR'] and values['mi1040_25'] > 0:
        rule13 = True
    else:
        rule13 = False

    if rule13:
        if mi1040CR53and55 < temp:
            rule13_df = no_error_string
        else:
            rule13_df = rule13_error_message
            final_message = final_message + rule13_df + '\n'
    else:
        rule13_df = no_error_string

    return rule13_df, final_message


def rule_14(final_message, exists, values):

    rule14_error_message_line31_is0 = 'WARNING: Check if the client insures a car or pays out-of-pocket insurance expenses (such as supplemental Medicare plan)'
    rule14_error_message_line31_gr0 = 'WARNING: Check to ensure that Medicare premiums included on the SSA-1099 are not included in MI-1040CR line 31'

    rule14 = exists['mi1040CR']

    if rule14:

        if values['mi1040CR_31'] == 0:

            rule14_df = rule14_error_message_line31_is0
            final_message = final_message + rule14_df + '\n'

        elif exists['SSA_income'] and values['medicare_payment'] > 0 \
                              and values['mi1040CR_31'] >= values['medicare_payment']:  #TY20 updated to look at actual medicare paid instead of default $500

            rule14_df = rule14_error_message_line31_gr0
            final_message = final_message + rule14_df + '\n'

        else:
            rule14_df = no_error_string
    else:
        rule14_df = no_error_string

    return rule14_df, final_message

#=================================================================
#--RULE 15:

# Check that rent is not entered into two locations in the 1040CR
# form for homestead property tax credit
#=================================================================
def rule_15(final_message, exists, values):

    rule15_error_message = 'WARNING: Rent payments entered in both Parts 4 and 5 for MI-1040CR. Verify this is correct.'

    rule15 = exists['mi1040CR'] and values['mi1040CR_53'] > 0

    if rule15:
        if values['mi1040CR_55'] == 0 and values['mi1040CR_57'] == 0:
            rule15_df = no_error_string
        else:
            rule15_df = rule15_error_message
            final_message = final_message + rule15_df + '\n'

    else:
        rule15_df = no_error_string

    return rule15_df, final_message


#=================================================================
#--RULE 16:

# Check that Special Housing (Co-op, etc.) pro-rated taxes
# are realistic
#=================================================================
def rule_16(final_message, exists, values):

    rule16_error_message = 'WARNING: Check that the prorated taxes for the Special Housing were entered correctly - MI1040CR line 57.'

    if exists['mi1040CR'] and values['mi1040CR_57'] > 0:
        rule16 = True
    else:
        rule16 = False

    if rule16:
        if values['mi1040CR_57'] < 2500:
            rule16_df = no_error_string
        else:
            rule16_df = rule16_error_message
            final_message = final_message + rule16_df + '\n'
    else:
        rule16_df = no_error_string

    return rule16_df, final_message

#========================================================
#--RULE 18a:

# Check that all dependents eligable for inclusion in the EITC are listed
#========================================================
def rule_18a(final_message, exists, values):

    rule18a_error_message = 'WARNING: EITC does not include all dependents.  Verify that all eligable dependents are included in the EIC credit.  Eligable dependents could include dependents under age 19, dependents under age 24 that are full-time students, and TPD dependents regardless of age.'

    if exists['ScheduleEIC'] and values['dependent_listed']:

        if values['num_eic_dep'] == 3 or values['num_eic_dep'] == values['num_dependents']:
            rule18a_df = no_error_string
        else:
            rule18a_df = rule18a_error_message
            final_message = final_message + rule18a_df + '\n'

    else:
        rule18a_df = no_error_string

    return rule18a_df, final_message

#========================================================
#--RULE 18b:

# Check that all dependents eligable for inclusion in the EITC are listed
#========================================================
def rule_18b(final_message, exists, values):

    rule18b_error_message = 'WARNING: No EITC.  Verify that all eligable dependents are included in the EIC credit.  Eligable dependents could include dependents under age 19, dependents under age 24 that are full-time students, and TBD dependents regardless of age'

    values['fed_earned_income'] = values['Fed1040_1'] + values['FedSch1_3'] - values['FedSch1_14']

    EITC_income_table_single = {1: 41756, 2: 47440, 3: 50954}  #dependents,value
    EITC_income_table_MFJ = {1: 47646, 2: 53330, 3: 56844}
    EITC_dep = min(values['num_dependents'], 3)  #max number of dependents used for the EITC is 3

    if values['dependent_listed']:
        if not values['spouse']:
            EITC_limit = EITC_income_table_single[EITC_dep]
        else:
            EITC_limit = EITC_income_table_MFJ[EITC_dep]
    else:
        if not values['spouse']:
            EITC_limit = 15820
        else:
            EITC_limit = 21710

    #should add investment income limit of $3650
    if values['dependent_listed'] and values['fed_filing_status'] != 3 \
                        and not exists['ScheduleEIC'] \
                        and values['Fed1040_11'] <= EITC_limit \
                        and values['fed_earned_income'] > 0 \
                        and values['fed_earned_income'] < EITC_limit:

        rule18b_df = rule18b_error_message
        final_message = final_message + rule18b_df + '\n'
    else:
        rule18b_df = no_error_string

    return rule18b_df, final_message, EITC_limit


#=================================================================
#--Rule 18c:
#
# EIC Lookback
#=================================================================
def rule_18c(final_message, exists, values):

    rule18c_error_message = 'WARNING: Check if 2019 earned income can be used to generate a larger EIC'

    EIC_max_credit = {0: 538, 1: 3584, 2: 5920, 3: 6660} # values['num_eic_dep'], value
    EIC_peak_upslope = {0: 7000, 1: 10500, 2: 14800, 3: 14800} # values['num_eic_dep'], value

    if exists['ScheduleEICnoDep'] or exists['ScheduleEIC']:
        ScheduleEIC_Check = True
    else:
        ScheduleEIC_Check = False

    if ScheduleEIC_Check and not values['EIC_PY_earned_income_used'] \
        and values['EIC_WorksheetB_6'] < EIC_peak_upslope[values['num_eic_dep']]:    #values['EIC_PY_earned_income_used'] = True when "PY earned income" is found on EIC Worksheet A or B
        if values['EIC_WorksheetB_10'] > 0:
            if values['EIC_WorksheetB_7'] < values['EIC_WorksheetB_10'] \
                and values['EIC_WorksheetB_7'] < EIC_max_credit[values['num_eic_dep']]:
                rule18c_df = rule18c_error_message
                final_message = final_message + rule18c_df + '\n'
            else:
                rule18c_df = no_error_string
        else:
            if values['EIC_WorksheetB_7'] < EIC_max_credit[values['num_eic_dep']]:
                rule18c_df = rule18c_error_message
                final_message = final_message + rule18c_df + '\n'
            else:
                rule18c_df = no_error_string

    else:
        rule18c_df = no_error_string

    return rule18c_df, final_message


#=================================================================
#--Rule 18d:
#
# EIC Lookback - no earned income 2020 but has unemployment income
#=================================================================
def rule_18d(final_message, exists, values):

    rule18d_error_message = 'WARNING: Check if client had 2019 earned income that can be used for the EIC lookback'

    if values['fed_earned_income'] == 0 and values['FedSch1_7'] > 0:
        rule18d_df = rule18d_error_message
        final_message = final_message + rule18d_df + '\n'
    else:
        rule18d_df = no_error_string

    return rule18d_df, final_message

#=================================================================
#--RULE 19:

# Check that all children under age of 17 are included in CTC
#=================================================================
def rule_19(final_message, exists, values):

    rule19_error_message = 'WARNING: Verify that all dependents under age 17 eligable for the Child Tax Credit are included in this credit'

    if values['dependent_listed'] and values['dep_under_17'] > 0 and exists['child_tax_worksheet']:
        if values['dep_under_17'] != values['num_dep_ctc']:
            rule19_df = rule19_error_message
            final_message = final_message + rule19_df + '\n'
        else:
            rule19_df = no_error_string
    elif values['dependent_listed'] and values['dep_under_17'] > 0 and exists['child_tax_worksheet'] == False and values['fed_earned_income'] > 2500:
        rule19_df = rule19_error_message
        final_message = final_message + rule19_df + '\n'
    else:
        rule19_df = no_error_string

    return rule19_df, final_message

#=================================================================
#--RULE 21:

# Check if IRA withdrawl can be exempt for tax penalty
#=================================================================
def rule_21(final_message, exists, values):

    rule21_error_message = 'WARNING: A penalty is applied to a retirement account withdrawl.  Check if there is a valid exemption from the early withdrawl penalty that can be added.'

    if exists['fedSchedule2'] and values['FedSch2_6'] > 0:
        rule21_df = rule21_error_message
        final_message = final_message + rule21_df + '\n'
    else:
        rule21_df = no_error_string

    return rule21_df, final_message


#=================================================================
#--RULE 22:

# Check for Home Heating Credit
#=================================================================
def rule_22(final_message, exists, values):

    rule22_error_message = 'WARNING: Check if the client is eligible for the Home Heating Credit.'
    rule22_error_message2 = 'Error:  Client is a Michigan Non-Resident and therefore not eligable for the Home Heating Credit'

    rule22 = exists['mi1040']

    hhc_income_table = {1: 14043,
                        2: 18986,
                        3: 23900,
                        4: 28842,
                        5: 33757,
                        6: 38700}

    if exists['mi1040']:
        if values['MI_exemptions'] < 7:
            hhc_income_limit = hhc_income_table[values['MI_exemptions']]
        else:
            hhc_income_limit = hhc_income_table[6] + (4943*(values['MI_exemptions'] - 6))
    else:
        hhc_income_limit = False

    if rule22:
        hhc_eligable = values['mi_THR'] <= hhc_income_limit
    else:
        hhc_eligable = False

    if rule22 and hhc_eligable and not values['mi1040_8b']:
        if exists['mi1040cr7']:
            rule22_df = no_error_string
        else:
            rule22_df = rule22_error_message
            final_message = final_message + rule22_df + '\n'
    elif rule22 and hhc_eligable and values['mi1040_8b']:
        if not exists['mi1040cr7']:
            rule22_df = no_error_string
        else:
            rule22_df = rule22_error_message2
            final_message = final_message + rule22_df + '\n'
    else:
        rule22_df = no_error_string

    return rule22_df, final_message, hhc_income_limit, hhc_eligable

#=================================================================
#--RULE 23:

# If home heating credit is included, check for
# insurance deduction from Total Household resources
#=================================================================
def rule_23(final_message, exists, values):

    rule23_error_message_line35_is0 = 'WARNING: Check if the client insures a car or pays out-of-pocket insurance expenses (such as supplemental Medicare plan)'
    rule23_error_message_line35_gr0 = 'WARNING: Check to ensure that Medicare premiums included on the SSA-1099 are not included in line MI-1040CR line 31'

    rule23 = not exists['mi1040CR'] \
             and exists['mi1040cr7'] \
             and not values['mi1040_8b']

    if rule23:
        if values['mi1040cr7_35'] == 0:
            rule23_df = rule23_error_message_line35_is0
            final_message = final_message + rule23_df + '\n'
        elif exists['SSA_income'] and values['medicare_payment'] > 0 \
            and values['mi1040cr7_35'] >= values['medicare_payment']:
            rule23_df = rule23_error_message_line35_gr0
            final_message = final_message + rule23_df + '\n'
        else:
            rule23_df = no_error_string
    else:
        rule23_df = no_error_string

    return rule23_df, final_message


#=================================================================
#--RULE 24:

# Check that HOH is selected if a dependent is listed
#=================================================================
def rule_24(final_message, exists, values):

    rule24_error_message = 'WARNING: Check if client should file as Head of Household'

    if values['dependent_listed'] and not values['spouse'] and values['fed_filing_status'] == 1:
        rule24_df = rule24_error_message
        final_message = final_message + rule24_df + '\n'
    else:
        rule24_df = no_error_string

    return rule24_df, final_message

#=================================================================
#--RULE 25:

# Check that client wants direct debit
#=================================================================
def rule_25(final_message, exists, values):

    rule25_error_message1 = 'WARNING: Verify client wants to use direct debit to pay Federal taxes.'
    rule25_error_message2 = 'WARNING: Verify client wants to use direct debit to pay Michigan taxes.'
    rule25_error_message3 = 'WARNING: Verify client wants to use direct debit to pay Federal and Michigan taxes.'

    if values['fed_direct_debit'] and not exists['MI_direct_payment']:
        rule25_df = rule25_error_message1
        final_message = final_message + rule25_df + '\n'
    elif not values['fed_direct_debit'] and exists['MI_direct_payment']:
        rule25_df = rule25_error_message2
        final_message = final_message + rule25_df + '\n'
    elif values['fed_direct_debit'] and exists['MI_direct_payment']:
        rule25_df = rule25_error_message3
        final_message = final_message + rule25_df + '\n'
    else:
        rule25_df = no_error_string

    return rule25_df, final_message

#=================================================================
#--RULE 26:

# Check that subsidized rent is realistic
#=================================================================
def rule_26(final_message, exists, values):

    rule26_error_message = 'WARNING: Check that subsidized/service fee rent paid (entire year) is correct on MI1040CR Line 55.'

    rule26 = exists['mi1040CR'] and values['mi1040CR_55'] > 0

    if rule26:
        if values['mi1040CR_55'] > 1000 and values['mi1040CR_55'] < 6000:
            rule26_df = no_error_string
        else:
            rule26_df = rule26_error_message
            final_message = final_message + rule26_df + '\n'
    else:
        rule26_df = no_error_string

    return rule26_df, final_message

#=================================================================
#--RULE 27:

# Check that rent paid for a "market rate" apartment is realistic
#=================================================================
def rule_27(final_message, exists, values):

    rule27_error_message = 'WARNING: Check that rent paid (entire year) is correct on MI1040CR Line 53.'

    rule27 = exists['mi1040CR'] and values['mi1040CR_53'] > 0

    if rule27:
        if values['mi1040CR_53'] < 20000:
            rule27_df = no_error_string
        else:
            rule27_df = rule27_error_message
            final_message = final_message + rule27_df + '\n'

    else:
        rule27_df = no_error_string

    return rule27_df, final_message

#=================================================================
#--RULE 28:

# Check if HSA contribution should be deducted
#=================================================================
def rule_28(final_message, exists, values):

    rule28_error_message = 'WARNING: An HSA contributaion deduction is included on Schedule 1 line 12.  Ensure this contributaiton was not made by the client via payroll deduction (i.e. W-2, Box 12, Code W).'

    if exists['fedForm8889'] and values['FedSch1_12'] > 0:
        rule28_df = rule28_error_message
        final_message = final_message + rule28_df + '\n'
    else:
        rule28_df = no_error_string

    return rule28_df, final_message

#=================================================================
#--RULE 29:

# Check if HSA distribution is taxed
#=================================================================
def rule_29(final_message, exists, values):

    rule29_error_message = 'WARNING: An HSA account withdrawl (Form 8889 line 15) are not entered as "qualified" and therefore a penalty was applied.  Check if the HSA withdrawls should have been qualified.'

    if exists['fedForm8889'] and values['FedForm8889_17b'] > 0:
        rule29_df = rule29_error_message
        final_message = final_message + rule29_df + '\n'
    else:
        rule29_df = no_error_string

    return rule29_df, final_message


#=================================================================
#--RULE 30:

# Check if returns are set to "Paper"
#=================================================================
def rule_30(final_message, exists, values):

    rule30_error_message1 = 'WARNING: Federal return is set to PAPER.'
    rule30_error_message2 = 'WARNING: Michigan return is set to PAPER.  This could also indicate that the "E-file" section in TaxSlayer has not been completed.'
    rule30_error_message3 = 'WARNING: Both Federal and Michigan returns are set to PAPER.'

    if not exists['fedForm8879'] and exists['miEfile']:
        rule30_df = rule30_error_message1
        final_message = final_message + rule30_df + '\n'
    elif not exists['fedForm8879'] and not exists['mi1040CR']:
        rule30_df = rule30_error_message1
        final_message = final_message + rule30_df + '\n'
    elif exists['fedForm8879'] and not exists['miEfile'] and exists['mi1040CR']:
        rule30_df = rule30_error_message2
        final_message = final_message + rule30_df + '\n'
    elif not exists['fedForm8879'] and not exists['miEfile'] and exists['mi1040CR']:
        rule30_df = rule30_error_message3
        final_message = final_message + rule30_df + '\n'
    else:
        rule30_df = no_error_string

    return rule30_df, final_message

#=================================================================
#--Rule 31:
#
# Check for "scholarship income"
#=================================================================
def rule_31(final_message, exists, values):

    rule31_error_message1 = 'WARNING: Scholarship income is included on Fed 1040 Line 1.  If scholarship is unrestricted, verify Education Tax Credits are maximized'
    rule31_error_message2 = 'WARNING: Other income is included on Fed Schedule 1 Line 8.  If this is scholarship income and it is unrestricted, verify Education Tax Credits are maximized.'

    if values['other_income'] == 'SCH':
        rule31_df = rule31_error_message1
        final_message = final_message + rule31_df + '\n'
    elif exists['fedSchedule1'] and values['FedSch1_8'] > 1:
        rule31_df = rule31_error_message2
        final_message = final_message + rule31_df + '\n'
    else:
        rule31_df = no_error_string

    return rule31_df, final_message

#=================================================================
#--Rule 32:
#
# Check for "education credits"
#=================================================================
def rule_32(final_message, exists, values):

    rule32_error_message = 'WARNING: Education Credit is included.  Verify tax benefit is maximized (unrestricted scholarships; American Opt Credit vs. Lifetime Learn Credit vs. Tuition & Fees Ded).'


    if exists['fedForm8863'] or exists['fedForm8917']:
        rule32_df = rule32_error_message
        final_message = final_message + rule32_df + '\n'
    else:
        rule32_df = no_error_string

    return rule32_df, final_message

#=================================================================
#--Rule 33:
#
# Check for excessive advance premium tax credit repayment
#=================================================================
def rule_33(final_message, exists, values):

    rule33_error_message = 'WARNING: Excessive advance premium tax credit repayment on Schedule 2 line 2.  Verify enteries on Form 8962 are correct and inform client.'

    if values['FedSch2_2'] > 0:
        rule33_df = rule33_error_message
        final_message = final_message + rule33_df + '\n'
    else:
        rule33_df = no_error_string

    return rule33_df, final_message

#=================================================================
#--Rule 34:
#
# Check for self-employment expenses
#=================================================================
def rule_34(final_message, exists, values):

    rule34_error_message = 'WARNING: Self-employment expenses are not subtracted from income.  Verify client did not have any expenses.'

    if exists['fedScheduleC'] and values['FedSch1_3'] == values['FedSchC_7']:
        rule34_df = rule34_error_message
        final_message = final_message + rule34_df + '\n'
    else:
        rule34_df = no_error_string

    return rule34_df, final_message

#=================================================================
#--Rule 35:
#
# Check for self-employment expenses
#=================================================================
def rule_35(final_message, exists, values):

    rule35_error_message = 'WARNING: Payment voucher(s) included in the return.  Check "Payment Voucher" on client ticket to indicate this needs to be sent to the client.'
    if exists['Fed1040V'] or exists['mi1040V']:
        rule35_df = rule35_error_message
        final_message = final_message + rule35_df + '\n'
    else:
        rule35_df = no_error_string

    return rule35_df, final_message

#=================================================================
#--Rule 36:
#
# Taxable amount of IRA distribution greater than total distribution
#=================================================================
def rule_36(final_message, exists, values):

    rule36_error_message = 'ERROR: Taxable portion of an IRA distribution on Fed 1040 line 4b is greater than the total amount on line 4a.'

    if values['Fed1040_4a'] > 0 and values['Fed1040_4b'] > values['Fed1040_4a']:
        rule36_df = rule36_error_message
        final_message = final_message + rule36_df + '\n'
    else:
        rule36_df = no_error_string

    return rule36_df, final_message

#=================================================================
#--Rule 37:
#
# Taxable amount of pension and annuity greater than total distribution
#=================================================================
def rule_37(final_message, exists, values):

    rule37_error_message = 'ERROR: Taxable portion of a pension and annuity on Fed 1040 line 5b is greater than the total amount on line 5a.'

    if values['Fed1040_5a'] > 0 and values['Fed1040_5b'] > values['Fed1040_5a']:
        rule37_df = rule37_error_message
        final_message = final_message + rule37_df + '\n'
    else:
        rule37_df = no_error_string

    return rule37_df, final_message
