# PLAYBOOK TO DISABLE NXAPI FEATURE
## VUL0xxxxxx FOR ALL 
Cisco NX-OS: Cisco NX-OS Software NX-API Arbitrary Command Execution Vulnerability

# PURPOSE
The purpose of this playbook is to disable features on NXOS. First run the script in "--check" mode and analyse the output in the "changes" folder. Then run the playbook without "--check". Analyze the pre and post tests.

# VERSION
Verion 0.1
# USAGE
Check mode:
"ansible-playbook -i hosts disable_nxapi.yml --check"

Run in check mode and verify in the directory "changes" what is being executed. Based on the output hosts can be ommited from the change

Production:
"ansible-playbook -i hosts disable_nxapi.yml"


# OPEN ITEMS/TODO's
Version | Item | Status | Prio
--------|------|------- | ------
0.1 | Playbook | Closed | High
0.1 | Checkmode | Closed | High
0.1 | Run pre and post tests and safe results | Closed | Medium
0.2 | Run filters to analyze output | Open | High
