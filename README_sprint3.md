# Usage

## To run the validator on the sprint 3 acceptance test file execute

`CS555Project/gedcomValidater/validate.py  CS555Project/gedcom_test_files/sprint3_acceptance_file.ged`

For US 22, 23, 25, 29, 30 and 31 you will see error messages

For US 27 you will notice that at the top of the output all individuals are printed together with their ages.

For US 28 you will notice that at the top of the output the child-list of every family is ordered by the age of the
siblings.

## To run the validator on the old acceptance test file execute

### Run sprint 1
`CS555Project/gedcomValidater/validate.py CS555Project/gedcom_test_files/sprint1_acceptance_file.ged`

### Run sprint 2
`CS555Project/gedcomValidater/validate.py CS555Project/gedcom_test_files/sprint2_acceptance_file.ged`

## To run the unit tests, run

`cd CS555Project/test; python3 unitTests.py`
