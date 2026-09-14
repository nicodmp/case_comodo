#!/bin/bash

set -a
source ~/.config/my-script/env
set +a

exec /usr/bin/python3 ~/comodo/github_user_repos.py
