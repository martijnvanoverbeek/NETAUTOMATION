# CIH automation tool
## Cloud Integration Hub (CIH)
First version of the Cloud Integration Hub automation script. This script will deploy configuration on 6 devices. This version should eventually morph into a production version of CIH2.0.
The picture below depicts the environment. The red arrows are the devices subject to automation.

![CIH](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/DATAMODEL/Ansible/pictures/cihautomation.png)

# VERSION
Verion 0.1
# USAGE
In the folder is a variable file containing the following variables:
* cloud_vlan_id: 100 <-- this is the vlan used at the cloud exchange it connects to the cloud providers
* ip_subnet: 10.225.225.0/29 <--- layer3 subnet to cloud provider
* cih_vlan_id: 123 <-- this is the vlan used in the decryption zone to connect CIHVTEP with CIHEDGE
* id: 9999 <-- incrementing id 
* service: cihl3 <-- for CIH always 'cihl3'
* provider: AZERPRI <-- Azure or AWS

"ansible-playbook -i hosts cih.yml -e "id=\<four digit string> service=\<selected service> provider=\<selected provider> cloud_vlan_id=\<vlan-id> cih_vlan_id=\<vlan-id>"

#Work in progress
test_facts file, this file needs to compare hostvar_interface with facts to see if an interface already exists. Currently set fact is hard coded but this has to be populated with the variables.
Currently trying to figure out how that works


# OPEN ITEMS/TODO's
Version | Item | Status | Prio
--------|------|------- | ------
0.1 | Validate configurations before writing to devices | High | Open
0.1 | Remove tenant and validate before removing | High | Open
0.1 | Generate vpnid at runtime instead of writing to file | Medium | Open
0.1 | Plugin to Infoblox to obtain IP address space | Medium | Open
0.1 | Plugin to Database to obtain id, and store other information |Medium | Open 
0.1 | Rewrite playbook to leverate EAPI calls | Low | Open


