# Create inventory from NA CSV
## Purpose
Create an inventory file from the NA inventory. This ansible playbook first creates a list of dictionaries from the csv files of NA. It then iterates through the models and creates an ini type inventory that can be used by Ansible
