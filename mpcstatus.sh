#!/bin/bash
mpc status | grep '\[' | cut -f1 -d " "
