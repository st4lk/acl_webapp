Tests
=====

Run instructions
----------------

 - Run all
    
    python -m tests.runtests

 - Run using tox

    pip install tox
    tox

 - Run with coverage

    pip install coverage
    coverage run --source=acl_webapp -m tests.runtests
    coverage report

Test create instructions
------------------------

 - If new test module is created, then it must be put in runtests TEST_MODULES
