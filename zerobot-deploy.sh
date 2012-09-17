#!/bin/bash

scriptDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $scriptDir
echo `date` Beginning deploy of $1-$2 from $3 >> /var/log/zerobot-deploy.log
ansible 127.0.0.1 -c local --module-path=$scriptDir -m zerobot-deploy -a "project=$1 app=$2 bucket=$3" >> /var/log/zerobot-deploy.log 2>&1
echo `date` Deploy of $1-$2 from $3 complete >> /var/log/zerobot-deploy.log
