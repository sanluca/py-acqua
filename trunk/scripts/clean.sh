#!/bin/bash
find . -name "*.pyc" -exec rm {} \;
find . -name "*~" -exec rm {} \;
find . -name "*.o" -exec rm {} \;
