Tests
=====

Run instructions
----------------

 - Run all
    
        python -m tests.runtests

 - Run one

        python -m tests.runtests tests.news_test.NewsCreateTest.test_post_is_saved

 - Run using tox

        pip install tox
        tox

 - Run with coverage

        pip install coverage
        coverage run --source=acl_webapp -m tests.runtests
        coverage report
    To see detailed html report, run

        coverage html
    Then visit htmlcov/index.html in your browser, to see a report [like this](http://nedbatchelder.com/code/coverage/sample_html).

Test create instructions
------------------------

 - If new test module is created, then it must be put in runtests TEST_MODULES
