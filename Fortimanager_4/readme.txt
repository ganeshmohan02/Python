"Fortimanager_Master"-file for all the fortimanager class & functions RESTAPI call.
"fwinput_cfg" -file for variables {WEB,APP}(Source of data).
"FMPrework"-file for prework job.
"Cutover"  -file for cutover job.
"Rollback" -file for rollback job.
**********************************************

Prework task list:
******************
1.	Create the new sub-interface on the new L3out with access to [ping, FM].
2.	Associate the new Sub-interface into existing Zone-interface / create the new Zone-interface.
3.	Configure the new static route with next-hop of new L3out.
4.	Create/modify the access-list and update the news prefixes into access-list.
5.	Condition: Append only the new prefix into access-list, even if we run multiples time the same script, this will avoid duplicate prefix entries in the access-list.
6.	Create/update the route-map, and then associate the access-list into route-map.
7.	In OSPF, associate route-map filter with static redistribution enabled. 
8.	Push all the configuration to the Fortigate appliance.

Cutover plan:  Traffic will swithover via new L3out interface.
***********
1.	Disable the current physical/vlan interface.
2.	Push all the configuration to the Fortigate appliance.

Rollback plan: Traffic will swithover back to the old interface.
************
1.	Enable the current physical/vlan interface.
2.	Push all the configuration to the Fortigate appliance.
