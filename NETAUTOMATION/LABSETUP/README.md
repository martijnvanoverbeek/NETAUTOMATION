# My testlab
I am on a journey re-inventing myself as a Network Engineer with some automation skills. To get there I signed up for Ivan (the legend) Pepeljnak's Automation course.

## System Specifications
For the Automation course I will predominantly use my home PC, which is a Windows10 Machine that i recently purchased. It has 12 Cores with 2 threads each, which gives me 24 virtual cores to creates simulations with.

![System](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/Pictures/System.png)

## EVE-NG
I don't want to waste a lot of time learning Vagrant, although i hear it is a great tool, I am not that familiar with it and it lacks an UI.
I chose EVE-NG-PRO for my simulations, I know this tool well and it is just a great tool to work with.

![EVE](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/Pictures/EVE-NG.png)

EVE allows me to create simulations on my home PC of about 20-30 nodes depending on the device i need to virtualize.
The PRO version allows me to export my labs so i can post them on github.

## Virtualization
I purchased VMWare Professional to install the EVE-VM and a CENTOS VM. 

![VMWare](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/Pictures/VMWare.png)

On the CENTOS VM i run my tools such as Ansible, Git and Visual Studio Code. I have Carl Buchmann to thank for the CENTOS setup, see url below for the automated install of all tools needed.

https://github.com/carlbuchmann/iac-dev

## Ansible
I use a simple setup below to test common network devices i encounter at my work. 

![Ansible](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/Pictures/Ansible_test.png)

## Cloud Exchange
The main goal of my automation course is to set up a fully automated Cloud Exchange. The cloud exchange makes it possible to connect Public and Private peerings from cloud providers to various destinations in our corporate network. The Cloud exchange should also be able to connect BGP ISP peerings.

![Cloud exchange Automation](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/Pictures/CloudXG.png)
