#!/bin/bash
swaymsg -t get_tree | jq '.. | select(.type?) | select(.focused==true) | .type'