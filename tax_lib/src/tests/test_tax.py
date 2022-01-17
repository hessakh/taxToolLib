import pytest
import pandas as pd

import sys

from src import tax_tool

sys.path.insert(0, '/')

@pytest.fixture(scope='module')
def tax_tool_outputs():
    """
    Run the tax tool once to generate the outputs
    """

    tax_tool.run()


def test_client_tax_information(tax_tool_outputs):
    """
    Verify that information from the `client_tax_information.csv` is correct

    The file includes a datetime of when the file was run; we don't want to
    compare this. Compare everything else to ensure they are the same.

    """

    solution_file = 'src/tests/output/solution/2020_client_tax_information.csv'
    this_file = 'src/tests/output/2020_client_tax_information.csv'

    df_solution = pd.read_csv(solution_file)
    df_this = pd.read_csv(this_file)

    # Drop columns we know are going to be different but they don't matter
    df_solution = df_solution.drop(columns=['DateTime_tool_was_run'])
    df_this = df_this.drop(columns=['DateTime_tool_was_run'])

    assert df_solution.equals(df_this)


def test_client_output():
    """
    Verify that information from the `client_output.csv` file is correct
    """

    solution_file = 'src/tests/output/solution/Client_output.txt'
    this_file = 'src/tests/output/Client_output.txt'

    # Compare string representations of the files
    a = open(solution_file, 'r').read()
    b = open(this_file, 'r').read()

    assert(a == b)

def test_hand_check_files():
    """
    Verify that information from the `completely_hand_check_these_files` file
    is correct
    """

    solution_file = 'src/tests/output/solution/Completely_hand_check_these_files.txt'
    this_file = 'src/tests/output/Completely_hand_check_these_files.txt'

    # Compare string representations of the files
    a = open(solution_file, 'r').read()
    b = open(this_file, 'r').read()

    assert(a == b)


