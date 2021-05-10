"fwinput_cfg" -file for contains all the variabls (souce of data).
"Fortimanager_Master"-file contains all the fortimanager class & functions RESTAPI call.
"FMPrework"-file conains all prework task list.
"Cutover" -file conains all cutover task list.
"Rollback"-file conains all rollback task list.
**********************************************

Prework task list:
******************
1.	Create the new sub-interface on the new L3out with access of  [ping, FM].
2.	Associate the new Sub-interface into existing Zone-interface / create the new Zone-interface.
3.	Configure the static route next-hop to the new L3out.
4.	Create/modify the access-list and update the prefixes into access-list.
5.	Only update the new prefixes into the access-list, even if we run multiples time the same script, to avoid duplicate prefix entries in the access-list.
6.	Create/update the route-map, finally associate the access-list into the route-map.
7.	In OSPF, associate route-map filter on static redistribution. 
8.	Push all the configuration to the Fortigate appliance.

Cutover plan:
***********
1.	Disable the current physical/vlan interface.
2.	Push all the configuration to the Fortigate appliance.

Rollback plan:
************
1.	Enable the current physical/vlan interface.
2.	Push all the configuration to the Fortigate appliance.
