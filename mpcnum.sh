#!/bin/bash
mpc status | grep '\[' | cut -f2 -d " "
