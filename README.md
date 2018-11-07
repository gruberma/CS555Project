[![Build Status](https://travis-ci.org/gruberma/CS555Project.svg?branch=master)](https://travis-ci.org/gruberma/CS555Project)

# Expectations (ProjectExpectations.pdf)
### (NOTE: Instructions on running our sprints is down lower under "Usage" heading)
* at least 2 user stories per member per sprint
* refactoring counts as one user story
* BUT each student must work at least on one story that provides value to the customer per sprint
* Also participate in
    * qackage / upload deliverables at end of sprint
    * active participation in sprint planning / review

# Usage

## To run the validator on the sprint 3 acceptance test file execute

`CS555Project/gedcomValidator/validate.py  CS555Project/gedcom_test_files/sprint3_acceptance_file.ged`

For US 22, 23, 25, 29, 30 and 31 you will see error messages

For US 27 you will notice that at the top of the output all individuals are printed together with their ages.

For US 28 you will notice that at the top of the output the child-list of every family is ordered by the age of the
siblings.

## To run the validator on the old acceptance test file execute

### Run sprint 1
`CS555Project/gedcomValidator/validate.py CS555Project/gedcom_test_files/sprint1_acceptance_file.ged`

### Run sprint 2
`CS555Project/gedcomValidator/validate.py CS555Project/gedcom_test_files/sprint2_acceptance_file.ged`

## To run the unit tests, run

`cd CS555Project/test; python3 unitTests.py`
