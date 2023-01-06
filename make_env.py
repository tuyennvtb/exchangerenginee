#!/usr/bin/env python3
import os
import json
from jinja2 import Environment, FileSystemLoader



file_loader = FileSystemLoader('.')
env = Environment(loader=file_loader)
template = env.get_template('env.template')
config = {}
for env in os.environ:
    config[env]=os.environ[env]


output = template.render(config = config)

with open('./BitmoonExchanger/BitmoonExchanger/.env', 'w') as f:
    f.write(output)
