#!/usr/bin/python

import json
import re
import os
from subprocess import call
import zipfile
import boto
from boto.s3.key import Key


def latest_release(s3_bucket):
  releases = s3_bucket.list()
  latest_release_number = -1
  for key in releases:
    match = re.match(r'^release-([0-9]+)/', key.name)
    if match:
      release_number = int(match.group(1))
      if release_number > latest_release_number:
        latest_release_number = release_number

  return latest_release_number


def main():
  module = AnsibleModule(
    argument_spec = dict(
      project = dict(required = True),
      app = dict(required = True),
      bucket = dict(required = True),
      dest = dict(required = True)
    )
  )

  project = module.params['project']
  app = module.params['app']
  bucket = module.params['bucket']
  dest = module.params['dest']

  changed = False

  conn = boto.connect_s3()
  s3_bucket = conn.get_bucket(bucket)

  release_num = latest_release(s3_bucket)
  if release_num > 0:
    release_folder_name = 'release-%s' % release_num
    zip_name = app + '.zip'
    dest_folder = dest + '/%s/%s/%s' % (project, app, release_folder_name)
    dest_zip_name = dest_folder + '/' + zip_name
    if not os.path.exists(dest_folder):
      changed = True
      os.makedirs(dest_folder)

    if not os.path.exists(dest_zip_name):
      changed = True
      release_key = Key(s3_bucket)
      release_key.key = '%s/%s' % (release_folder_name, zip_name)
      release_key.get_contents_to_filename(dest_zip_name)

    if not os.path.exists(dest_folder + '/deploy'):
      changed = True
      with zipfile.ZipFile(dest_zip_name) as dest_zip:
        dest_zip.extractall(dest_folder)

    ansible_command_line = 'ansible-playbook -c local -e "app_home=\'%s\'" %s/deploy/deploy.yml' % (dest_folder, dest_folder)
    return_code = call([ansible_command_line], shell = True)
    module.fail_json("Ansible deploy playbook returned " + return_code)

  module.exit_json(changed = changed)


# include magic from lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>
main()
