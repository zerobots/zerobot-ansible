#!/bin/bash

scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $scriptDir
ansible 127.0.0.1 -c local --module-path=$scriptDir -m zerobot-deploy2 -a "project=$1 app=$2 bucket=$3" >> /var/log/zerobot-deploy.log 2>&1
