# Routediff Ansible tool
Routediff can be used to compare routing tables prior to and after a change. Currently only tested on N9K and N7K devices. Use it during your change to compare route tables prior to and after a change. There are two versions available routediff which only compares default routing tables and vrfroutes which compares the vrf-tables on devices.

## routediff
### Usage
Route diff uses tags. The following tags are validated:
* prechange
* postchange
* compare

### syntax
ansible-playbook -i hosts routediff.yml --tag "tag"

#### prechange
Prechange tag will copy the routing table to the "prechange" folder

#### postchange
Postchange tag will copy the routing table to the "postchange" folder

#### compare
Compare tag will create a var file per ansible_host in the vars directory and create FOUR csv files in the "results" folder. Each ansible_host will have the following files:
* prechange: csv file with all routes prior to the change, separated by prefix, nexthop, protocol and adminstrative distance
* postchange: csv file with all routes after the change, separated by prefix, nexthop, protocol and adminstrative distance
* added: csv file with all new routes, separated by prefix, nexthop, protocol and adminstrative distance
* removed: csv file with all deleted routes, separated by prefix, nexthop, protocol and adminstrative distance
