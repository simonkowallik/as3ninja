
#!/usr/bin/env bash

if [[ "$REPORT" != "true" ]]
then
    exit 0
fi

case $1 in
"install")
    curl -L -o ./cc-test-reporter \
        https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64
    chmod +x ./cc-test-reporter
    ;;
"prepare")
    ./cc-test-reporter before-build
    ;;
"report")
    echo "-----[ code climate ]---------------------------"
    ./cc-test-reporter after-build --exit-code $TRAVIS_TEST_RESULT
    echo "------------------------------------------------"
    echo
    echo "-----[ codecov ]--------------------------------"
    codecov -v
    echo "------------------------------------------------"
    ;;
esac
