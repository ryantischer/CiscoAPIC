# CiscoAPIC
Collection of scripts to automation Cisco ACI

build_port.py 
#Script configures a phyiscal port in an EPG for a bare metal server
#Assumes the phyiscal port is configured under fabric \ access policies

#Requires sys, json and requests.
#Requires http enabled on the APIC.  Optionally can configure TLS1.1/1.2 on script server for https.

# To enable http on APIC...

#On the menu bar, FABRIC -> Fabric Policies -> Pod Policies -> Policies -> Communication
#Under Communication, click the default policy
#In the Work pane, enable HTTP and disable HTTPS

#NOTE:  Configuration is atomic, if it fails for whatever reason, the entire configuration fails.
