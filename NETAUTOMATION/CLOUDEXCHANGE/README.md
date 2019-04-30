# Cloud exchange datamodel
I am using the Automation course to develop a fully automated Cloud Exchange. I will work together with our selected vendor to develop this automation. My first attempt will be with Ansible, but i am not sure yet if the initial methods will be used in a production ready solution.

## Where I work 
I work for a large insurance company, the sixth largest company in the United States. My role within the company is Service Level Owner in our Datacenter Infrastructure Services department. 

## Cloud Exchange 
The cloud exchange will provide layer2 and layer3 VPN extensions based on VXLAN overlay. I use Arista in this PoC. One feature i like is the fact that Arista switches can shape traffic. 

### Legacy Cloud Exchange 
![Legacy](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/DATAMODEL/Pictures/legacy.png)

I will use the Automation course to develop a new cloud exchange. The cloud exchange will be BGP-EVPN based VXLAN solution that can use the Core of our network as an underlay. It does not need physical cross connects to provide layer2 extensions into the different zones in our network. 
All connections between Cloud Exchange and our internal data centers will be of type point-to-point or point-to-multi-point. 

### New Cloud Exchange 
![Cloud exchange](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/DATAMODEL/Pictures/CloudXG.png)

## Variables 
I will first describe the atomic variables, these are the essential values. I will move on to describe derived values and move into the business logic. 
### Cloud Exchange Variables 
#### Atomic Variables
* CLOUD-EXCHANGE-VTEP-IP address:<br />
  Anycast VTEP IP address<br />
  \<IP address>
* Local-Mgt-Loopback-IP address:<br />
  Loopback IP address<br />
  \<IP address>
* Local VLANs:<br />
  Locally significant to the cloud exchange number below 4094 with some reserved values.<br />
  \<number>
* CloudXG-ID:<br />
  CloudXG identifier, in short "id" is a unique number, it is used to create derived variables<br />
  \<number>
* Service:<br />
  List of dictionaries: cihl3=01, ispl2=10, ispl3=11
#### Derived Variables 
* vpnid:<br />
  Derived variable from Service-id+Provider-id+CloudXG-id
* VRF name:<br />
  Derived from service-name+vpnid
  \<service-name>\<vpnid>
* Route-distinguisher:<br />
  \<Local-Mgt-Loopback-IP address>:\<vpnid>
* Import route-targets:<br />
  \<SERVICE-VTEP-IP address>:\<vpnid>
* Export route-targets:<br />
  \<CLOUD-EXCHANGE-VTEP-IP address>:\<vpnid><br />
### Service VTEP variables
#### Atomic Variables
* Service VLANs:<br />
  Locally significant to the service
   \<number>
#### Derived Variables
* vpnid:<br />
  Derived variable from Service-id+Provider-id+CloudXG-id
* VRF name:<br />
  Derived from service-name+vpnid
  \<service-name>\<vpnid>
* Route-distinguisher:<br />
  \<Local-Mgt-Loopback-IP address>:\<vpnid>
* Import route-targets:<br />
  \<CLOUD-EXCHANGE-VTEP-IP address>:\<vpnid><br />
* Export route-targets:<br />
  \<SERVICE-VTEP-IP address>:\<vpnid>


![variables](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/DATAMODEL/Pictures/variables.png)

## Business Logic 
The picture below depicts an UML inspired data model

![Business logic](https://github.com/martijnvanoverbeek/IPSPACE/blob/master/DATAMODEL/Pictures/Datamodel.png)

After this chapter I will work on the Ansible Roles (toughest part for me probably)
